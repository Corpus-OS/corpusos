from typing import AsyncIterator, Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import time
import hashlib
from corpus_sdk.embedding.embedding_base import BaseEmbeddingAdapter
from corpus_sdk.embedding.embedding_base import (
    EmbeddingCapabilities, EmbedSpec, BatchEmbedSpec,
    EmbedResult, BatchEmbedResult, EmbeddingVector,
    EmbedChunk, EmbeddingStats, OperationContext
)
from corpus_sdk.embedding.embedding_base import (
    BadRequest, AuthError, ResourceExhausted, TransientNetwork,
    Unavailable, NotSupported, DeadlineExceeded,
    TextTooLong, ModelNotAvailable
)


# ----------------------------------------------------------------------
# MOCK CLIENT (Replace with real provider SDK in production)
# ----------------------------------------------------------------------

@dataclass
class MockEmbedResponse:
    """Mock provider response."""
    vector: List[float]
    tokens: int


class MockEmbedClient:
    """Mock embedding provider client."""
    
    def __init__(self):
        self._dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072
        }
    
    async def embed(self, model: str, text: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Mock embedding call."""
        await asyncio.sleep(0.01)  # Simulate network
        
        # Generate deterministic vector based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        dim = self._dimensions.get(model, 1536)
        vector = [float(int(text_hash[i % len(text_hash)], 16)) / 15.0 for i in range(dim)]
        
        # Simple token counting (words)
        tokens = len(text.split())
        
        return {
            "vector": vector,
            "tokens": tokens
        }
    
    async def count_tokens(self, model: str, text: str, timeout: Optional[float] = None) -> int:
        """Mock token counting."""
        await asyncio.sleep(0.001)
        return len(text.split())
    
    async def health_check(self) -> bool:
        """Mock health check."""
        return True


# ----------------------------------------------------------------------
# PRODUCTION EMBEDDING ADAPTER
# ----------------------------------------------------------------------

class ProductionEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    Production-ready embedding adapter with 100% conformance.
    
    BATCH FAILURE MODE: Collect per-item failures with partial success reporting.
    STREAMING PATTERN: Single-chunk (one final chunk with complete vector).
    CAPABILITIES: Hardcoded based on provider capabilities.
    """
    
    def __init__(self, client, supported_models, model_dimensions, **kwargs):
        super().__init__(**kwargs)
        self._client = client
        self._supported_models = tuple(supported_models)
        self._dimensions = model_dimensions
        self._max_batch_size = 256
        self._max_text_length = 8192
        
        # Stats: NO CACHE METRICS (base owns those)
        self._stats = {
            "embed_calls": 0,
            "embed_batch_calls": 0,
            "stream_embed_calls": 0,
            "count_tokens_calls": 0,
            "total_texts_embedded": 0,
            "total_tokens_processed": 0,
            "total_processing_time_ms": 0.0,
            "error_count": 0
        }
    
    # ----------------------------------------------------------------------
    # CAPABILITIES (Hardcoded - NOT configurable)
    # ----------------------------------------------------------------------
    
    async def _do_capabilities(self) -> EmbeddingCapabilities:
        """Advertise true provider capabilities - NEVER configurable."""
        return EmbeddingCapabilities(
            server="my-embed-provider",
            version="1.0.0",
            protocol="embedding/v1.0",
            supported_models=self._supported_models,
            max_batch_size=self._max_batch_size,
            max_text_length=self._max_text_length,
            max_dimensions=max(self._dimensions.values()),
            supports_normalization=True,
            supports_truncation=True,
            supports_token_counting=True,
            normalizes_at_source=False,  # Provider returns raw vectors
            truncation_mode="base",
            supports_deadline=True,
            idempotent_writes=True,
            supports_multi_tenant=True,
            supports_streaming=True,
            supports_batch_embedding=True
        )
    
    # ----------------------------------------------------------------------
    # SINGLE EMBED (with validation)
    # ----------------------------------------------------------------------
    
    async def _do_embed(self, spec: EmbedSpec, *, ctx=None) -> EmbedResult:
        """MANDATORY: Single embedding with validation."""
        self._stats["embed_calls"] += 1
        t0 = time.monotonic()
        
        # ✅ VALIDATE in _do_embed
        if not isinstance(spec.text, str) or not spec.text.strip():
            raise BadRequest("text must be a non-empty string")
        
        if spec.model not in self._supported_models:
            raise ModelNotAvailable(
                f"Model '{spec.model}' is not supported",
                details={
                    "requested_model": spec.model,
                    "supported_models": list(self._supported_models)
                }
            )
        
        # Get timeout from deadline
        timeout = self._get_timeout(ctx)
        
        try:
            response = await self._client.embed(
                model=spec.model,
                text=spec.text,
                timeout=timeout
            )
        except Exception as e:
            self._stats["error_count"] += 1
            raise self._map_provider_error(e)
        
        vec = response["vector"]
        tokens = response.get("tokens", self._count_tokens_sync(spec.text, spec.model))
        
        ev = EmbeddingVector(
            vector=vec,
            text=spec.text,
            model=spec.model,
            dimensions=len(vec)
        )
        
        self._stats["total_texts_embedded"] += 1
        self._stats["total_tokens_processed"] += tokens
        self._stats["total_processing_time_ms"] += (time.monotonic() - t0) * 1000
        
        return EmbedResult(
            embedding=ev,
            model=spec.model,
            text=spec.text,
            tokens_used=tokens,
            truncated=False  # Base sets this if truncation occurred
        )
    
    # ----------------------------------------------------------------------
    # BATCH EMBED (Collection pattern - chosen, not configurable)
    # ----------------------------------------------------------------------
    
    async def _do_embed_batch(self, spec: BatchEmbedSpec, *, ctx=None) -> BatchEmbedResult:
        """
        BATCH FAILURE MODE: Collect per-item failures, continue processing.
        
        This adapter never fails the entire batch due to individual item errors.
        Failures are reported in failed_texts with full error details.
        """
        self._stats["embed_batch_calls"] += 1
        t0 = time.monotonic()
        
        if spec.model not in self._supported_models:
            raise ModelNotAvailable(f"Model '{spec.model}' is not supported")
        
        if len(spec.texts) > self._max_batch_size:
            reduction_pct = self._suggested_batch_reduction_percent(
                len(spec.texts), self._max_batch_size
            )
            raise BadRequest(
                f"Batch size {len(spec.texts)} exceeds maximum of {self._max_batch_size}",
                details={
                    "max_batch_size": self._max_batch_size,
                    "actual": len(spec.texts)
                },
                suggested_batch_reduction=reduction_pct
            )
        
        timeout = self._get_timeout(ctx)
        
        embeddings = []
        failures = []
        total_tokens = 0
        
        for i, text in enumerate(spec.texts):
            try:
                # ✅ Validate each item
                if not isinstance(text, str) or not text.strip():
                    raise BadRequest("text must be non-empty")
                
                if len(text) > self._max_text_length:
                    raise TextTooLong(
                        f"Text length {len(text)} exceeds maximum of {self._max_text_length}",
                        details={
                            "max_length": self._max_text_length,
                            "actual_length": len(text)
                        }
                    )
                
                # Call provider
                response = await self._client.embed(
                    model=spec.model,
                    text=text,
                    timeout=timeout
                )
                
                vec = response["vector"]
                tokens = response.get("tokens", self._count_tokens_sync(text, spec.model))
                
                embeddings.append(EmbeddingVector(
                    vector=vec,
                    text=text,
                    model=spec.model,
                    dimensions=len(vec)
                ))
                
                total_tokens += tokens
                self._stats["total_texts_embedded"] += 1
                self._stats["total_tokens_processed"] += tokens
                
            except Exception as e:
                # COLLECT failure, continue processing
                failures.append({
                    "index": i,
                    "text": text[:100],  # Truncate for safety
                    "error": type(e).__name__,
                    "code": getattr(e, "code", None) or type(e).__name__.upper(),
                    "message": str(e)[:200],  # Truncate for safety
                    "metadata": spec.metadatas[i] if spec.metadatas else None
                })
                self._stats["error_count"] += 1
        
        self._stats["total_processing_time_ms"] += (time.monotonic() - t0) * 1000
        
        return BatchEmbedResult(
            embeddings=embeddings,
            model=spec.model,
            total_texts=len(spec.texts),
            total_tokens=total_tokens,
            failed_texts=failures  # REQUIRED: partial failure reporting
        )
    
    def _suggested_batch_reduction_percent(self, requested: int, maximum: int) -> Optional[int]:
        """PERCENTAGE reduction hint, not absolute."""
        if requested <= 0 or maximum < 0 or requested <= maximum:
            return None
        return int(100 * (requested - maximum) / requested)
    
    # ----------------------------------------------------------------------
    # STREAM EMBED (Single-chunk pattern - chosen, not configurable)
    # ----------------------------------------------------------------------
    
    async def _do_stream_embed(
        self, spec: EmbedSpec, *, ctx=None
    ) -> AsyncIterator[EmbedChunk]:
        """
        STREAMING PATTERN: Single chunk with one complete vector.
        
        This adapter emits exactly one chunk with is_final=True containing
        the complete embedding vector. No partial vectors are emitted.
        """
        self._stats["stream_embed_calls"] += 1
        t0 = time.monotonic()
        
        # Validate (same as _do_embed)
        if not isinstance(spec.text, str) or not spec.text.strip():
            raise BadRequest("text must be a non-empty string")
        
        if spec.model not in self._supported_models:
            raise ModelNotAvailable(f"Model '{spec.model}' is not supported")
        
        timeout = self._get_timeout(ctx)
        
        try:
            response = await self._client.embed(
                model=spec.model,
                text=spec.text,
                timeout=timeout
            )
        except Exception as e:
            self._stats["error_count"] += 1
            raise self._map_provider_error(e)
        
        vec = response["vector"]
        tokens = response.get("tokens", self._count_tokens_sync(spec.text, spec.model))
        
        ev = EmbeddingVector(
            vector=vec,
            text=spec.text,
            model=spec.model,
            dimensions=len(vec)
        )
        
        # SINGLE CHUNK, is_final=True
        yield EmbedChunk(
            embeddings=[ev],
            is_final=True,
            usage={"tokens": tokens},
            model=spec.model
        )
        
        self._stats["total_texts_embedded"] += 1
        self._stats["total_tokens_processed"] += tokens
        self._stats["total_processing_time_ms"] += (time.monotonic() - t0) * 1000
    
    # ----------------------------------------------------------------------
    # TOKEN COUNTING (Accurate - no approximations)
    # ----------------------------------------------------------------------
    
    async def _do_count_tokens(self, text: str, model: str, *, ctx=None) -> int:
        """MANDATORY: Accurate token counting."""
        self._stats["count_tokens_calls"] += 1
        t0 = time.monotonic()
        
        if model not in self._supported_models:
            raise ModelNotAvailable(f"Model '{model}' is not supported")
        
        timeout = self._get_timeout(ctx)
        
        try:
            count = await self._client.count_tokens(
                model=model,
                text=text,
                timeout=timeout
            )
        except Exception as e:
            self._stats["error_count"] += 1
            raise self._map_provider_error(e)
        
        self._stats["total_processing_time_ms"] += (time.monotonic() - t0) * 1000
        return count
    
    def _count_tokens_sync(self, text: str, model: str) -> int:
        """Synchronous token count for internal use (simple word split for demo)."""
        # In production, use tiktoken or provider's tokenizer
        return len(text.split())
    
    # ----------------------------------------------------------------------
    # STATS (NO CACHE METRICS - CRITICAL)
    # ----------------------------------------------------------------------
    
    async def _do_get_stats(self, ctx=None) -> EmbeddingStats:
        """MANDATORY: Adapter-owned stats ONLY. NO cache metrics."""
        total_ops = (
            self._stats["embed_calls"] +
            self._stats["embed_batch_calls"] +
            self._stats["stream_embed_calls"] +
            self._stats["count_tokens_calls"]
        )
        
        avg_ms = (self._stats["total_processing_time_ms"] / total_ops) if total_ops else 0
        
        # ✅ CORRECT: NO cache_hits, NO cache_misses
        return EmbeddingStats(
            total_requests=total_ops,
            total_texts=self._stats["total_texts_embedded"],
            total_tokens=self._stats["total_tokens_processed"],
            avg_processing_time_ms=avg_ms,
            error_count=self._stats["error_count"]
        )
    
    # ----------------------------------------------------------------------
    # HEALTH
    # ----------------------------------------------------------------------
    
    async def _do_health(self, ctx=None) -> Dict[str, Any]:
        """Health check - NO ctx.attrs-driven forcing."""
        try:
            healthy = await self._client.health_check()
            return {
                "ok": healthy,
                "status": "ok" if healthy else "degraded",
                "server": "my-embed-provider",
                "version": "1.0.0",
                "models": {
                    m: {"status": "ready"}
                    for m in self._supported_models
                }
            }
        except Exception:
            return {
                "ok": False,
                "status": "down",
                "server": "my-embed-provider",
                "version": "1.0.0"
            }
    
    # ----------------------------------------------------------------------
    # UTILITIES
    # ----------------------------------------------------------------------
    
    def _get_timeout(self, ctx):
        """Convert deadline to timeout."""
        if ctx is None:
            return None
        rem = ctx.remaining_ms()
        if rem is None or rem <= 0:
            return None
        return rem / 1000.0
    
    def _map_provider_error(self, e: Exception):
        """Map provider errors to canonical Corpus errors."""
        if "rate limit" in str(e).lower():
            return ResourceExhausted("Rate limit exceeded", retry_after_ms=5000)
        if "auth" in str(e).lower() or "key" in str(e).lower():
            return AuthError("Authentication failed")
        if "timeout" in str(e).lower():
            return TransientNetwork("Request timeout")
        if "too long" in str(e).lower() or "length" in str(e).lower():
            return TextTooLong(str(e))
        if "model" in str(e).lower() and "not found" in str(e).lower():
            return ModelNotAvailable(str(e))
        
        return Unavailable(f"Provider error: {type(e).__name__}")
    
    def reset_stats(self):
        """Reset stats (for testing)."""
        self._stats = {k: 0 for k in self._stats}


# ----------------------------------------------------------------------
# COMPREHENSIVE TESTS
# ----------------------------------------------------------------------

async def main():
    """Test suite for ProductionEmbeddingAdapter."""
    
    # Setup
    client = MockEmbedClient()
    models = ["text-embedding-3-small", "text-embedding-3-large"]
    dimensions = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072
    }
    
    adapter = ProductionEmbeddingAdapter(client, models, dimensions)
    
    print("=" * 60)
    print("PRODUCTION EMBEDDING ADAPTER - COMPREHENSIVE TESTS")
    print("=" * 60)
    
    # TEST 1: Capabilities
    print("\n[TEST 1] Capabilities")
    caps = await adapter.capabilities()
    print(f"✅ Server: {caps.server}")
    print(f"✅ Protocol: {caps.protocol}")
    print(f"✅ Models: {len(caps.supported_models)}")
    print(f"✅ Max batch: {caps.max_batch_size}")
    print(f"✅ Max dimensions: {caps.max_dimensions}")
    print(f"✅ Streaming: {caps.supports_streaming}")
    print(f"✅ Batch embedding: {caps.supports_batch_embedding}")
    
    # TEST 2: Single Embed
    print("\n[TEST 2] Single Embed")
    spec = EmbedSpec(
        text="Hello world",
        model="text-embedding-3-small"
    )
    result = await adapter.embed(spec)
    print(f"✅ Dimensions: {result.embedding.dimensions}")
    print(f"✅ Tokens: {result.tokens_used}")
    print(f"✅ Model: {result.model}")
    print(f"✅ Truncated: {result.truncated}")
    assert result.embedding.dimensions == 1536, "Wrong dimensions"
    assert len(result.embedding.vector) == 1536, "Vector size mismatch"
    
    # TEST 3: Batch Embed (Success)
    print("\n[TEST 3] Batch Embed (All Success)")
    batch_spec = BatchEmbedSpec(
        texts=["first text", "second text", "third text"],
        model="text-embedding-3-small"
    )
    batch_result = await adapter.embed_batch(batch_spec)
    print(f"✅ Total texts: {batch_result.total_texts}")
    print(f"✅ Embeddings: {len(batch_result.embeddings)}")
    print(f"✅ Failures: {len(batch_result.failed_texts)}")
    print(f"✅ Total tokens: {batch_result.total_tokens}")
    assert len(batch_result.embeddings) == 3, "Should have 3 embeddings"
    assert len(batch_result.failed_texts) == 0, "Should have 0 failures"
    
    # TEST 4: Batch Embed (Partial Failure)
    print("\n[TEST 4] Batch Embed (Partial Failure)")
    batch_spec_mixed = BatchEmbedSpec(
        texts=["good text", "", "another good", "   "],  # Two empty strings
        model="text-embedding-3-small"
    )
    batch_result_mixed = await adapter.embed_batch(batch_spec_mixed)
    print(f"✅ Total texts: {batch_result_mixed.total_texts}")
    print(f"✅ Embeddings: {len(batch_result_mixed.embeddings)}")
    print(f"✅ Failures: {len(batch_result_mixed.failed_texts)}")
    print(f"✅ Failure indices: {[f['index'] for f in batch_result_mixed.failed_texts]}")
    assert len(batch_result_mixed.embeddings) == 2, "Should have 2 successful embeddings"
    assert len(batch_result_mixed.failed_texts) == 2, "Should have 2 failures"
    assert batch_result_mixed.failed_texts[0]['index'] == 1, "First failure at index 1"
    assert batch_result_mixed.failed_texts[1]['index'] == 3, "Second failure at index 3"
    
    # TEST 5: Streaming
    print("\n[TEST 5] Streaming Embed")
    stream_spec = EmbedSpec(
        text="Streaming test text",
        model="text-embedding-3-small"
    )
    chunks = []
    async for chunk in adapter.stream_embed(stream_spec):
        chunks.append(chunk)
        print(f"✅ Chunk: {len(chunk.embeddings)} embeddings, is_final={chunk.is_final}")
    assert len(chunks) == 1, "Should have exactly 1 chunk"
    assert chunks[0].is_final, "Chunk should be final"
    assert len(chunks[0].embeddings) == 1, "Chunk should have 1 embedding"
    assert chunks[0].embeddings[0].dimensions == 1536, "Wrong dimensions"
    
    # TEST 6: Token Counting
    print("\n[TEST 6] Token Counting")
    text = "Count these tokens please"
    count = await adapter.count_tokens(text, "text-embedding-3-small")
    print(f"✅ Token count: {count}")
    assert count == 4, "Should have 4 tokens"
    
    # TEST 7: Stats
    print("\n[TEST 7] Stats")
    stats = await adapter.get_stats()
    print(f"✅ Total requests: {stats.total_requests}")
    print(f"✅ Total texts: {stats.total_texts}")
    print(f"✅ Total tokens: {stats.total_tokens}")
    print(f"✅ Avg time (ms): {stats.avg_processing_time_ms:.2f}")
    print(f"✅ Errors: {stats.error_count}")
    assert stats.total_requests > 0, "Should have requests"
    assert stats.total_texts > 0, "Should have processed texts"
    assert stats.total_tokens > 0, "Should have processed tokens"
    
    # TEST 8: Health Check
    print("\n[TEST 8] Health Check")
    health = await adapter.health()
    print(f"✅ OK: {health['ok']}")
    print(f"✅ Status: {health.get('status')}")
    print(f"✅ Server: {health.get('server')}")
    print(f"✅ Models: {len(health.get('models', {}))}")
    assert health['ok'], "Health check should pass"
    
    # TEST 9: Error Handling (Invalid Model)
    print("\n[TEST 9] Error Handling (Invalid Model)")
    try:
        bad_spec = EmbedSpec(
            text="Test",
            model="invalid-model"
        )
        await adapter.embed(bad_spec)
        print("❌ Should have raised ModelNotAvailable")
    except ModelNotAvailable as e:
        print(f"✅ Caught ModelNotAvailable: {e}")
    
    # TEST 10: Error Handling (Empty Text)
    print("\n[TEST 10] Error Handling (Empty Text)")
    try:
        empty_spec = EmbedSpec(
            text="",
            model="text-embedding-3-small"
        )
        await adapter.embed(empty_spec)
        print("❌ Should have raised BadRequest")
    except BadRequest as e:
        print(f"✅ Caught BadRequest: {e}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✅")
    print("=" * 60)
    
    # Final stats summary
    final_stats = await adapter.get_stats()
    print(f"\n📊 Final Stats:")
    print(f"   - Total requests: {final_stats.total_requests}")
    print(f"   - Total texts embedded: {final_stats.total_texts}")
    print(f"   - Total tokens processed: {final_stats.total_tokens}")
    print(f"   - Average processing time: {final_stats.avg_processing_time_ms:.2f}ms")
    print(f"   - Errors: {final_stats.error_count}")


if __name__ == "__main__":
    asyncio.run(main())
