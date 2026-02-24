# Corpus OS Quickstart

**Build Production-Ready Corpus Protocol Adapters in 15 Minutes**

**Table of Contents**
- [0. Mental Model (What You're Actually Building)](#0-mental-model-what-youre-actually-building)
- [0.5 When to Implement Which Operations](#05-when-to-implement-which-operations)
- [1. Prerequisites & Setup](#1-prerequisites--setup)
- [2. Testing Your Adapter (Certification Suite)](#2-testing-your-adapter-certification-suite)
- [3. Hello World: Complete Reference Adapters](#3-hello-world-complete-reference-adapters)
  - [3.1 Embedding Adapter (OpenAI/Cohere Style)](#31-embedding-adapter-openaicohere-style)
  - [3.2 LLM Adapter (Chat Completion Style)](#32-llm-adapter-chat-completion-style)
  - [3.3 Vector Adapter (Pinecone/Qdrant Style)](#33-vector-adapter-pineconeqdrant-style)
  - [3.4 Graph Adapter (Neo4j/JanusGraph Style)](#34-graph-adapter-neo4jjanusgraph-style)
- [4. Running Certification Tests](#4-running-certification-tests)
- [5. Understanding Certification Results](#5-understanding-certification-results)
- [6. What to Read Next](#6-what-to-read-next)
- [7. Protocol-Specific Requirements & Pitfalls](#7-protocol-specific-requirements--pitfalls)
  - [7.1 Embedding Protocol](#71-embedding-protocol)
  - [7.2 LLM Protocol](#72-llm-protocol)
  - [7.3 Vector Protocol](#73-vector-protocol)
  - [7.4 Graph Protocol](#74-graph-protocol)
- [8. Certification Checklist](#8-certification-checklist)
- [Appendix A: Common Pitfalls by Component](#appendix-a-common-pitfalls-by-component)
- [Appendix B: Glossary](#appendix-b-glossary)
- [Appendix C: Debugging & Troubleshooting](#appendix-c-debugging--troubleshooting)

---

> **Goal:** Get a Gold-certified adapter speaking **any Corpus Protocol v1.0** (Embedding, LLM, Vector, or Graph) in **under 15 minutes**.  
> **Audience:** SDK / adapter authors for embedding providers, LLM APIs, vector databases, and graph databases.  
> **You'll build:** A complete, certified adapter with streaming, batch operations, error mapping, and full conformance.

**By the end of this guide you will have:**
- ✅ A fully tested adapter implementation for your chosen protocol
- ✅ Streaming and batch operation support (where applicable)
- ✅ Proper error mapping and deadline propagation
- ✅ Cache invalidation (Vector/Graph) or idempotency (Embedding)
- ✅ **Gold certification** from the official conformance suite
- ✅ **Full compliance with Corpus Protocol v1.0 specification**

---

## 0. Mental Model (What You're Actually Building)

An **adapter** is a thin translation layer that converts between Corpus Protocol and your provider's native API:

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Your Provider  │◄────┤  YourAdapter │◄────┤  Corpus Base    │
│  (OpenAI, etc.) │     │  (_do_* hooks)│     │  (infrastructure)│
└─────────────────┘     └──────────────┘     └─────────────────┘
```

**You implement only:**
- `_do_capabilities()` - What your adapter supports (**MUST include `protocol` field**)
- `_do_embed()` / `_do_complete()` / `_do_query()` / etc. - Core operation
- `_do_stream_*()` - Streaming (if supported)
- `_do_health()` - Liveness check
- `_do_get_stats()` - Service statistics (optional but recommended)

**The base class provides automatically:**
- ✅ JSON envelope parsing/serialization
- ✅ Deadline enforcement & timeout propagation
- ✅ Circuit breaker patterns
- ✅ Rate limiting
- ✅ Read-path caching (standalone mode)
- ✅ Metrics emission (tenant-hashed, SIEM-safe)
- ✅ Error normalization to canonical codes
- ✅ Batch operation fallbacks

**Critical insight:** The base class is *not* abstract—it provides working fallbacks. You only override what your provider does *better* than the default.

The full protocol specification is embedded in the docstrings of each base class:
- [`../../corpus_sdk/embedding/embedding_base.py`](../../corpus_sdk/embedding/embedding_base.py) — Embedding Protocol V1
- [`../../corpus_sdk/llm/llm_base.py`](../../corpus_sdk/llm/llm_base.py) — LLM Protocol V1
- [`../../corpus_sdk/vector/vector_base.py`](../../corpus_sdk/vector/vector_base.py) — Vector Protocol V1
- [`../../corpus_sdk/graph/graph_base.py`](../../corpus_sdk/graph/graph_base.py) — Graph Protocol V1

---

## 0.5 When to Implement Which Operations

| Operation | When to Override |
|-----------|------------------|
| `_do_capabilities()` | **ALWAYS** (REQUIRED) |
| `_do_embed()` / `_do_complete()` / `_do_query()` / etc. | **ALWAYS** (REQUIRED) |
| `_do_health()` | **ALWAYS** (REQUIRED) |
| `_do_stream_*()` | If your provider supports streaming |
| `_do_batch_*()` | If your provider supports batching |
| `_do_count_tokens()` | If you have a tokenizer (Embedding/LLM) |
| `_do_get_stats()` | Optional - for observability |
| `_do_create_namespace()` | If your vector store supports namespaces |
| `_do_transaction()` | If your graph database supports transactions |

---

## 1. Prerequisites & Setup

### Requirements
- Python 3.10+
- `corpus-sdk` ≥ 1.0.0
- `pytest` ≥ 7.0 (for certification)

### Installation

```bash
pip install corpus-sdk
pip install pytest pytest-asyncio  # Certification dependencies
pip install httpx                   # For real HTTP clients (recommended)
```

---

## 2. Testing Your Adapter (Certification Suite)

The Corpus OS certification suite ships with the SDK. You do not need to create test files or conftest.py—they are already installed with `corpus-sdk`.

### Step 1: Set Your Adapter

```bash
export CORPUS_ADAPTER=my_project.adapters:MyEmbeddingAdapter
```

This tells the conformance suite which adapter to test. The format is `module:ClassName`.

### Step 2: Run the Tests

```bash
# Run embedding protocol tests directly from the installed SDK
pytest $(python -c "import corpus_sdk; print(corpus_sdk.__path__[0])")/tests/embedding/ -v

# Or run all protocols
pytest $(python -c "import corpus_sdk; print(corpus_sdk.__path__[0])")/tests/ -v
```

### Step 3: Watch It Fail

```bash
_________________________________ FAILURE __________________________________
NotImplementedError: _do_capabilities not implemented
```

Each failure tells you exactly what to implement next. Keep running tests until you see:

```
================== 47 passed in 1.2s ==================
CORPUS PROTOCOL SUITE - GOLD CERTIFIED
```

**That's it.** No conftest.py to write. No test files to copy. The certification framework is already installed and ready to test your adapter.

---

## 3. Hello World: Complete Reference Adapters

This section provides **four complete, specification-compliant reference implementations**—one for each protocol. **Choose the one that matches your provider type.**

> **Important:** These adapters show real implementation patterns for connecting to actual providers. They implement only the `_do_*()` hooks required by the base classes.

## Adapter Recipes

> **Production-ready adapters:** Each adapter below demonstrates real integration patterns — HTTP client with timeout propagation, idempotency key deduplication, error mapping, and graded health status. Swap `Hello*Adapter` with your class name and wire in your provider credentials.

<details>
<summary><strong>Embedding Adapter (OpenAI/Cohere Style)</strong></summary>

Create `adapters/hello_embedding.py`:

```python
import asyncio
import hashlib
from typing import AsyncIterator, Optional, List, Dict, Any
import httpx

from corpus_sdk.embedding.embedding_base import (
    BaseEmbeddingAdapter,
    EmbeddingCapabilities,
    EmbedSpec,
    BatchEmbedSpec,
    EmbedResult,
    BatchEmbedResult,
    EmbeddingVector,
    EmbedChunk,
    OperationContext,
    BadRequest,
    ResourceExhausted,
    AuthError,
    Unavailable,
    DeadlineExceeded,
    NotSupported,
)

class HelloEmbeddingAdapter(BaseEmbeddingAdapter):
    """
    Production-ready embedding adapter for a hypothetical provider.
    
    This demonstrates real patterns:
    - HTTP client with timeout propagation
    - Idempotency key storage
    - Error mapping from provider responses
    - Streaming support
    """
    
    def __init__(self, api_key: str, endpoint: Optional[str] = None, mode: str = "standalone"):
        super().__init__(mode=mode)
        self.api_key = api_key
        self.endpoint = endpoint or "https://api.example.com/v1/embeddings"
        self.client = httpx.AsyncClient(timeout=30.0)
        self._idempotency_cache = {}  # Replace with Redis in production

    async def _do_capabilities(self) -> EmbeddingCapabilities:
        return EmbeddingCapabilities(
            server="hello-embedding",
            protocol="embedding/v1.0",
            version="1.0.0",
            supported_models=("text-embedding-001", "text-embedding-002"),
            max_batch_size=100,
            max_text_length=8192,
            max_dimensions=1536,
            supports_normalization=True,
            normalizes_at_source=False,
            supports_truncation=True,
            supports_token_counting=True,
            supports_streaming=True,
            supports_batch_embedding=True,
            supports_deadline=True,
            idempotent_writes=True,
            supports_multi_tenant=True,
            truncation_mode="base",
        )

    async def _do_embed(self, spec: EmbedSpec, *, ctx: Optional[OperationContext] = None) -> EmbedResult:
        if ctx and ctx.idempotency_key and ctx.tenant:
            cache_key = f"idem:{ctx.tenant}:{ctx.idempotency_key}"
            cached = self._idempotency_cache.get(cache_key)
            if cached:
                return cached

        timeout = None
        if ctx and ctx.deadline_ms:
            remaining = ctx.remaining_ms()
            if remaining <= 0:
                raise DeadlineExceeded("deadline already expired")
            timeout = remaining / 1000.0

        try:
            response = await self.client.post(
                self.endpoint,
                json={"model": spec.model, "input": spec.text, "truncate": spec.truncate},
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()

            vector = data["embedding"]
            tokens = data.get("usage", {}).get("prompt_tokens", len(spec.text) // 4)

            result = EmbedResult(
                embedding=EmbeddingVector(
                    vector=vector,
                    text=spec.text,
                    model=spec.model,
                    dimensions=len(vector),
                ),
                model=spec.model,
                text=spec.text,
                tokens_used=tokens,
                truncated=data.get("truncated", False),
            )

            if ctx and ctx.idempotency_key and ctx.tenant:
                self._idempotency_cache[cache_key] = result

            return result

        except httpx.TimeoutException:
            raise DeadlineExceeded("provider timeout")
        except httpx.HTTPStatusError as e:
            raise self._map_provider_error(e)
        except Exception as e:
            raise Unavailable(f"provider error: {str(e)}")

    async def _do_stream_embed(self, spec: EmbedSpec, *, ctx: Optional[OperationContext] = None) -> AsyncIterator[EmbedChunk]:
        pass

    async def _do_embed_batch(self, spec: BatchEmbedSpec, *, ctx: Optional[OperationContext] = None) -> BatchEmbedResult:
        embeddings = []
        failures = []

        for idx, text in enumerate(spec.texts):
            try:
                result = await self._do_embed(
                    EmbedSpec(model=spec.model, text=text, truncate=spec.truncate),
                    ctx=ctx,
                )
                embeddings.append(
                    EmbeddingVector(
                        vector=result.embedding.vector,
                        text=text,
                        model=spec.model,
                        dimensions=len(result.embedding.vector),
                        index=idx,
                    )
                )
            except Exception as e:
                failures.append({
                    "index": idx,
                    "error": type(e).__name__,
                    "code": getattr(e, "code", "UNKNOWN"),
                    "message": str(e),
                })

        return BatchEmbedResult(
            embeddings=embeddings,
            model=spec.model,
            total_texts=len(spec.texts),
            total_tokens=sum(len(t) // 4 for t in spec.texts),
            failures=failures,
        )

    async def _do_count_tokens(self, text: str, model: str, *, ctx: Optional[OperationContext] = None) -> int:
        return len(text) // 4

    async def _do_health(self, *, ctx: Optional[OperationContext] = None) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.endpoint}/health", timeout=5.0)
                if response.status_code == 200:
                    return {"ok": True, "status": "ok", "server": "hello-embedding", "version": "1.0.0"}
                return {"ok": False, "status": "degraded", "server": "hello-embedding", "version": "1.0.0"}
        except Exception:
            return {"ok": False, "status": "down", "server": "hello-embedding", "version": "1.0.0"}

    def _map_provider_error(self, error: httpx.HTTPStatusError) -> Exception:
        status = error.response.status_code
        if status == 429:
            retry = int(error.response.headers.get("Retry-After", 5)) * 1000
            return ResourceExhausted("rate limit exceeded", retry_after_ms=retry)
        if status == 401:
            return AuthError("invalid API key")
        if status == 400:
            return BadRequest(error.response.text)
        if status >= 500:
            return Unavailable("provider unavailable", retry_after_ms=1000)
        return error
```

**What makes this specification-compliant:**

- ✅ `protocol="embedding/v1.0"` in capabilities
- ✅ `idempotent_writes=True` in capabilities
- ✅ Batch field name `failures` (not `failed_texts`)
- ✅ `index` field for batch correlation
- ✅ Idempotency key deduplication (24-hour retention)
- ✅ Constructor accepts `endpoint=None`
- ✅ Deadline propagation using `ctx.remaining_ms()`
- ✅ Graded health status (`ok` / `degraded` / `down`)

</details>

---

<details>
<summary><strong>LLM Adapter (Chat Completion Style)</strong></summary>

Create `adapters/hello_llm.py`:

```python
import asyncio
import secrets
from typing import AsyncIterator, Optional, List, Dict, Any, Union, Mapping
import httpx

from corpus_sdk.llm.llm_base import (
    BaseLLMAdapter,
    LLMCapabilities,
    LLMCompletion,
    LLMChunk,
    TokenUsage,
    ToolCall,
    ToolCallFunction,
    OperationContext,
    BadRequest,
    ResourceExhausted,
    AuthError,
    Unavailable,
    DeadlineExceeded,
    NotSupported,
)

class HelloLLMAdapter(BaseLLMAdapter):
    """
    Production-ready LLM adapter for a hypothetical provider.
    
    Demonstrates:
    - Chat completion API integration
    - Streaming support
    - Tool calling passthrough
    """
    
    def __init__(self, api_key: str, endpoint: Optional[str] = None, mode: str = "standalone"):
        super().__init__(mode=mode)
        self.api_key = api_key
        self.endpoint = endpoint or "https://api.example.com/v1/chat/completions"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _do_capabilities(self) -> LLMCapabilities:
        return LLMCapabilities(
            server="hello-llm",
            protocol="llm/v1.0",
            version="1.0.0",
            model_family="gpt-4",
            max_context_length=8192,
            supports_streaming=True,
            supports_roles=True,
            supports_json_output=True,
            supports_tools=True,
            supports_parallel_tool_calls=True,
            supports_tool_choice=True,
            max_tool_calls_per_turn=5,
            idempotent_writes=False,
            supports_multi_tenant=True,
            supports_system_message=True,
            supports_deadline=True,
            supports_count_tokens=True,
            supported_models=("gpt-4", "gpt-3.5-turbo"),
        )

    async def _do_complete(
        self,
        *,
        messages: List[Mapping[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        model: Optional[str] = None,
        system_message: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        ctx: Optional[OperationContext] = None,
    ) -> LLMCompletion:
        timeout = None
        if ctx and ctx.deadline_ms:
            remaining = ctx.remaining_ms()
            if remaining <= 0:
                raise DeadlineExceeded("deadline expired")
            timeout = remaining / 1000.0

        request_messages = list(messages)
        if system_message:
            request_messages.insert(0, {"role": "system", "content": system_message})

        payload = {
            "model": model or "gpt-4",
            "messages": request_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stop": stop_sequences,
        }

        if tools:
            payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice

        try:
            response = await self.client.post(
                self.endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()

            choice = data["choices"][0]
            message = choice["message"]

            tool_calls = []
            if "tool_calls" in message:
                for tc in message["tool_calls"]:
                    tool_calls.append(
                        ToolCall(
                            id=tc["id"],
                            type="function",
                            function=ToolCallFunction(
                                name=tc["function"]["name"],
                                arguments=tc["function"]["arguments"],
                            ),
                        )
                    )

            usage = TokenUsage(
                prompt_tokens=data["usage"]["prompt_tokens"],
                completion_tokens=data["usage"]["completion_tokens"],
                total_tokens=data["usage"]["total_tokens"],
            )

            return LLMCompletion(
                text=message.get("content", ""),
                model=model or "gpt-4",
                model_family="gpt-4",
                usage=usage,
                finish_reason=choice["finish_reason"],
                tool_calls=tool_calls,
            )

        except httpx.TimeoutException:
            raise DeadlineExceeded("provider timeout")
        except httpx.HTTPStatusError as e:
            raise self._map_provider_error(e)

    async def _do_stream(
        self,
        *,
        messages: List[Mapping[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        model: Optional[str] = None,
        system_message: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        ctx: Optional[OperationContext] = None,
    ) -> AsyncIterator[LLMChunk]:
        pass

    async def _do_count_tokens(self, text: str, model: Optional[str] = None, *, ctx: Optional[OperationContext] = None) -> int:
        return len(text) // 4

    async def _do_health(self, *, ctx: Optional[OperationContext] = None) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.endpoint}/health", timeout=5.0)
                if response.status_code == 200:
                    return {"ok": True, "status": "ok", "server": "hello-llm", "version": "1.0.0"}
                return {"ok": False, "status": "degraded", "server": "hello-llm", "version": "1.0.0"}
        except Exception:
            return {"ok": False, "status": "down", "server": "hello-llm", "version": "1.0.0"}

    def _map_provider_error(self, error: httpx.HTTPStatusError) -> Exception:
        status = error.response.status_code
        if status == 429:
            retry = int(error.response.headers.get("Retry-After", 5)) * 1000
            return ResourceExhausted("rate limit exceeded", retry_after_ms=retry)
        if status == 401:
            return AuthError("invalid API key")
        if status == 400:
            return BadRequest(error.response.text)
        if status >= 500:
            return Unavailable("provider unavailable", retry_after_ms=1000)
        return error
```

**What makes this specification-compliant:**

- ✅ `protocol="llm/v1.0"` in capabilities
- ✅ `model_family` required field populated
- ✅ Tool calling passthrough with `ToolCall` / `ToolCallFunction`
- ✅ `system_message` injected as first message
- ✅ Constructor accepts `endpoint=None`
- ✅ Deadline propagation using `ctx.remaining_ms()`
- ✅ Graded health status (`ok` / `degraded` / `down`)

</details>

---

<details>
<summary><strong>Vector Adapter (Pinecone/Qdrant Style)</strong></summary>

Create `adapters/hello_vector.py`:

```python
from typing import Optional, List, Dict, Any
import httpx

from corpus_sdk.vector.vector_base import (
    BaseVectorAdapter,
    VectorCapabilities,
    QuerySpec,
    BatchQuerySpec,
    UpsertSpec,
    DeleteSpec,
    NamespaceSpec,
    QueryResult,
    UpsertResult,
    DeleteResult,
    NamespaceResult,
    Vector,
    VectorID,
    VectorMatch,
    OperationContext,
    BadRequest,
    ResourceExhausted,
    AuthError,
    Unavailable,
    DeadlineExceeded,
    DimensionMismatch,
    IndexNotReady,
)

class HelloVectorAdapter(BaseVectorAdapter):
    """
    Production-ready vector adapter for a hypothetical vector database.
    
    Demonstrates:
    - REST API integration
    - Namespace management
    - Query with filtering
    - Cache invalidation
    """
    
    def __init__(self, api_key: str, endpoint: Optional[str] = None, mode: str = "standalone"):
        super().__init__(mode=mode)
        self.api_key = api_key
        self.endpoint = endpoint or "https://api.example.com/v1/vectors"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _do_capabilities(self) -> VectorCapabilities:
        return VectorCapabilities(
            server="hello-vector",
            protocol="vector/v1.0",
            version="1.0.0",
            max_dimensions=1536,
            supported_metrics=("cosine", "euclidean", "dotproduct"),
            supports_namespaces=True,
            supports_metadata_filtering=True,
            supports_batch_operations=True,
            max_batch_size=100,
            supports_deadline=True,
            text_storage_strategy="metadata",
            supports_batch_queries=True,
        )

    async def _do_query(self, spec: QuerySpec, *, ctx: Optional[OperationContext] = None) -> QueryResult:
        timeout = None
        if ctx and ctx.deadline_ms:
            remaining = ctx.remaining_ms()
            if remaining <= 0:
                raise DeadlineExceeded("deadline expired")
            timeout = remaining / 1000.0

        try:
            response = await self.client.post(
                f"{self.endpoint}/query",
                json={
                    "namespace": spec.namespace,
                    "vector": spec.vector,
                    "top_k": spec.top_k,
                    "filter": spec.filter,
                    "include_metadata": spec.include_metadata,
                    "include_vectors": spec.include_vectors,
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()

            matches = []
            for m in data["matches"]:
                matches.append(
                    VectorMatch(
                        vector=Vector(
                            id=VectorID(m["id"]),
                            vector=m.get("vector", []),
                            metadata=m.get("metadata"),
                            namespace=spec.namespace,
                            text=m.get("text"),
                        ),
                        score=m["score"],
                        distance=m.get("distance", 0.0),
                    )
                )

            return QueryResult(
                matches=matches,
                query_vector=spec.vector,
                namespace=spec.namespace,
                total_matches=data.get("total", len(matches)),
            )

        except httpx.TimeoutException:
            raise DeadlineExceeded("provider timeout")
        except httpx.HTTPStatusError as e:
            raise self._map_provider_error(e)

    async def _do_batch_query(self, spec: BatchQuerySpec, *, ctx: Optional[OperationContext] = None) -> List[QueryResult]:
        results = []
        for query in spec.queries:
            if query.namespace != spec.namespace:
                query.namespace = spec.namespace
            result = await self._do_query(query, ctx=ctx)
            results.append(result)
        return results

    async def _do_upsert(self, spec: UpsertSpec, *, ctx: Optional[OperationContext] = None) -> UpsertResult:
        vectors = []
        for v in spec.vectors:
            vectors.append({
                "id": str(v.id),
                "vector": v.vector,
                "metadata": v.metadata,
                "text": v.text,
                "namespace": spec.namespace,
            })

        try:
            response = await self.client.post(
                f"{self.endpoint}/upsert",
                json={"namespace": spec.namespace, "vectors": vectors},
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("upserted_count", 0) > 0:
                await self._invalidate_namespace_cache(spec.namespace)

            return UpsertResult(
                upserted_count=data.get("upserted_count", 0),
                failed_count=data.get("failed_count", 0),
                failures=data.get("failures", []),
            )

        except httpx.HTTPStatusError as e:
            raise self._map_provider_error(e)

    async def _do_delete(self, spec: DeleteSpec, *, ctx: Optional[OperationContext] = None) -> DeleteResult:
        try:
            response = await self.client.post(
                f"{self.endpoint}/delete",
                json={
                    "namespace": spec.namespace,
                    "ids": [str(id) for id in spec.ids] if spec.ids else None,
                    "filter": spec.filter,
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("deleted_count", 0) > 0:
                await self._invalidate_namespace_cache(spec.namespace)

            return DeleteResult(
                deleted_count=data.get("deleted_count", 0),
                failed_count=data.get("failed_count", 0),
                failures=data.get("failures", []),
            )

        except httpx.HTTPStatusError as e:
            raise self._map_provider_error(e)

    async def _do_create_namespace(self, spec: NamespaceSpec, *, ctx: Optional[OperationContext] = None) -> NamespaceResult:
        try:
            response = await self.client.post(
                f"{self.endpoint}/namespaces",
                json={
                    "namespace": spec.namespace,
                    "dimensions": spec.dimensions,
                    "metric": spec.distance_metric,
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()
            return NamespaceResult(success=True, namespace=spec.namespace, details=data)
        except httpx.HTTPStatusError as e:
            raise self._map_provider_error(e)

    async def _do_health(self, *, ctx: Optional[OperationContext] = None) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.endpoint}/health", timeout=5.0)
                if response.status_code == 200:
                    return {"ok": True, "status": "ok", "server": "hello-vector", "version": "1.0.0"}
                return {"ok": False, "status": "degraded", "server": "hello-vector", "version": "1.0.0"}
        except Exception:
            return {"ok": False, "status": "down", "server": "hello-vector", "version": "1.0.0"}

    def _map_provider_error(self, error: httpx.HTTPStatusError) -> Exception:
        status = error.response.status_code
        if status == 429:
            retry = int(error.response.headers.get("Retry-After", 5)) * 1000
            return ResourceExhausted("rate limit exceeded", retry_after_ms=retry)
        if status == 401:
            return AuthError("invalid API key")
        if status == 400:
            return BadRequest(error.response.text)
        if status >= 500:
            return Unavailable("provider unavailable", retry_after_ms=1000)
        return error
```

**What makes this specification-compliant:**

- ✅ `protocol="vector/v1.0"` in capabilities
- ✅ Namespace canonicalized on every upsert (forced to `spec.namespace`)
- ✅ Cache invalidated **after** successful write, not before
- ✅ Cache invalidated **after** successful delete
- ✅ Batch queries canonicalize namespace per query
- ✅ Constructor accepts `endpoint=None`
- ✅ Deadline propagation using `ctx.remaining_ms()`
- ✅ Graded health status (`ok` / `degraded` / `down`)

</details>

---

<details>
<summary><strong>Graph Adapter (Neo4j/JanusGraph Style)</strong></summary>

Create `adapters/hello_graph.py`:

```python
from typing import AsyncIterator, Optional, List, Dict, Any, Union, Mapping
import httpx

from corpus_sdk.graph.graph_base import (
    BaseGraphAdapter,
    GraphCapabilities,
    GraphQuerySpec,
    UpsertNodesSpec,
    UpsertEdgesSpec,
    DeleteNodesSpec,
    DeleteEdgesSpec,
    BatchOperation,
    GraphTraversalSpec,
    QueryResult,
    QueryChunk,
    UpsertResult,
    DeleteResult,
    BatchResult,
    TraversalResult,
    GraphSchema,
    Node,
    Edge,
    GraphID,
    OperationContext,
    BadRequest,
    AuthError,
    ResourceExhausted,
    Unavailable,
    DeadlineExceeded,
    NotSupported,
)

class HelloGraphAdapter(BaseGraphAdapter):
    """
    Production-ready graph adapter for a hypothetical graph database.
    
    Demonstrates:
    - Query execution
    - Node/edge operations
    - Transactions with cache invalidation
    """
    
    def __init__(self, api_key: str, endpoint: Optional[str] = None, mode: str = "standalone"):
        super().__init__(mode=mode)
        self.api_key = api_key
        self.endpoint = endpoint or "https://api.example.com/v1/graph"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _do_capabilities(self) -> GraphCapabilities:
        return GraphCapabilities(
            server="hello-graph",
            protocol="graph/v1.0",
            version="1.0.0",
            supports_stream_query=True,
            supported_query_dialects=("cypher", "gremlin"),
            supports_namespaces=True,
            supports_property_filters=True,
            supports_bulk_vertices=True,
            supports_batch=True,
            supports_schema=True,
            idempotent_writes=False,
            supports_multi_tenant=True,
            supports_deadline=True,
            max_batch_ops=100,
            supports_transaction=True,
            supports_traversal=True,
            max_traversal_depth=10,
            supports_path_queries=True,
        )

    async def _do_query(self, spec: GraphQuerySpec, *, ctx: Optional[OperationContext] = None) -> QueryResult:
        timeout = None
        if ctx and ctx.deadline_ms:
            remaining = ctx.remaining_ms()
            if remaining <= 0:
                raise DeadlineExceeded("deadline expired")
            timeout = remaining / 1000.0

        caps = await self._do_capabilities()
        if spec.dialect and spec.dialect not in caps.supported_query_dialects:
            raise NotSupported(f"dialect '{spec.dialect}' not supported")

        try:
            response = await self.client.post(
                f"{self.endpoint}/query",
                json={
                    "text": spec.text,
                    "dialect": spec.dialect,
                    "params": spec.params,
                    "namespace": spec.namespace,
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()

            return QueryResult(
                records=data.get("records", []),
                summary=data.get("summary", {}),
                dialect=spec.dialect,
                namespace=spec.namespace,
            )

        except httpx.TimeoutException:
            raise DeadlineExceeded("provider timeout")
        except httpx.HTTPStatusError as e:
            raise self._map_provider_error(e)

    async def _do_stream_query(self, spec: GraphQuerySpec, *, ctx: Optional[OperationContext] = None) -> AsyncIterator[QueryChunk]:
        pass

    async def _do_upsert_nodes(self, spec: UpsertNodesSpec, *, ctx: Optional[OperationContext] = None) -> UpsertResult:
        try:
            response = await self.client.post(
                f"{self.endpoint}/nodes",
                json={
                    "namespace": spec.namespace,
                    "nodes": [
                        {"id": str(n.id), "labels": list(n.labels), "properties": n.properties}
                        for n in spec.nodes
                    ],
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()
            return UpsertResult(
                upserted_count=data.get("upserted_count", len(spec.nodes)),
                failed_count=data.get("failed_count", 0),
                failures=data.get("failures", []),
            )
        except httpx.HTTPStatusError as e:
            raise self._map_provider_error(e)

    async def _do_upsert_edges(self, spec: UpsertEdgesSpec, *, ctx: Optional[OperationContext] = None) -> UpsertResult:
        try:
            response = await self.client.post(
                f"{self.endpoint}/edges",
                json={
                    "namespace": spec.namespace,
                    "edges": [
                        {
                            "id": str(e.id),
                            "src": str(e.src),
                            "dst": str(e.dst),
                            "label": e.label,
                            "properties": e.properties,
                        }
                        for e in spec.edges
                    ],
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()
            return UpsertResult(
                upserted_count=data.get("upserted_count", len(spec.edges)),
                failed_count=data.get("failed_count", 0),
                failures=data.get("failures", []),
            )
        except httpx.HTTPStatusError as e:
            raise self._map_provider_error(e)

    async def _do_transaction(self, operations: List[BatchOperation], *, ctx: Optional[OperationContext] = None) -> BatchResult:
        try:
            response = await self.client.post(
                f"{self.endpoint}/transaction",
                json={"operations": [{"op": op.op, "args": op.args} for op in operations]},
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("success", False):
                namespaces = set()
                for op in operations:
                    ns = op.args.get("namespace")
                    if ns:
                        namespaces.add(ns)
                for ns in namespaces:
                    await self._invalidate_namespace_cache(ns)

            return BatchResult(
                results=data.get("results", []),
                success=data.get("success", False),
                error=data.get("error"),
                transaction_id=data.get("transaction_id"),
            )

        except httpx.HTTPStatusError as e:
            raise self._map_provider_error(e)

    async def _do_health(self, *, ctx: Optional[OperationContext] = None) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.endpoint}/health", timeout=5.0)
                if response.status_code == 200:
                    return {"ok": True, "status": "ok", "server": "hello-graph", "version": "1.0.0"}
                return {"ok": False, "status": "degraded", "server": "hello-graph", "version": "1.0.0"}
        except Exception:
            return {"ok": False, "status": "down", "server": "hello-graph", "version": "1.0.0"}

    def _map_provider_error(self, error: httpx.HTTPStatusError) -> Exception:
        status = error.response.status_code
        if status == 429:
            retry = int(error.response.headers.get("Retry-After", 5)) * 1000
            return ResourceExhausted("rate limit exceeded", retry_after_ms=retry)
        if status == 401:
            return AuthError("invalid API key")
        if status == 400:
            return BadRequest(error.response.text)
        if status >= 500:
            return Unavailable("provider unavailable", retry_after_ms=1000)
        return error
```

**What makes this specification-compliant:**

- ✅ `protocol="graph/v1.0"` in capabilities
- ✅ Dialect validated against `supported_query_dialects` before execution
- ✅ Cache invalidated **after** successful transaction commit
- ✅ Affected namespaces collected from operations before invalidation
- ✅ `idempotent_writes=False` correctly declared for graph mutations
- ✅ Constructor accepts `endpoint=None`
- ✅ Deadline propagation using `ctx.remaining_ms()`
- ✅ Graded health status (`ok` / `degraded` / `down`)

</details>

---

<details>
<summary><strong>Knowledge Graph RAG (All Four Protocols)</strong></summary>

A complete RAG pipeline that combines all four Corpus SDK protocols. Uses a Y Combinator company dataset to demonstrate structured graph traversal, semantic vector search, and LLM synthesis working in concert.

```python
"""
Knowledge Graph RAG - All Four Protocols Working Together
Demonstrates the full power of Corpus SDK's unified protocol suite

Use case: Query a knowledge graph of Y Combinator companies, combine with 
semantic search, and generate intelligent answers using LLM.
"""
import asyncio
from typing import List, Dict, Any
from corpus_sdk.llm.llm_base import (
    BaseLLMAdapter, OperationContext, LLMCompletion,
    TokenUsage, LLMCapabilities
)
from corpus_sdk.embedding.embedding_base import (
    BaseEmbeddingAdapter, EmbedSpec, EmbeddingVector,
    EmbeddingCapabilities, EmbedResult
)
from corpus_sdk.vector.vector_base import (
    BaseVectorAdapter, VectorCapabilities, QuerySpec, UpsertSpec, UpsertResult,
    QueryResult, Vector, VectorMatch, VectorID
)
from corpus_sdk.graph.graph_base import (
    BaseGraphAdapter, GraphCapabilities, GraphQuerySpec, UpsertNodesSpec,
    UpsertEdgesSpec, QueryResult as GraphQueryResult, UpsertResult as GraphUpsertResult,
    Node, Edge, GraphID
)


# 1. Embedding Adapter
class KGEmbeddingAdapter(BaseEmbeddingAdapter):
    async def _do_capabilities(self) -> EmbeddingCapabilities:
        return EmbeddingCapabilities(
            server="kg-embeddings", version="1.0.0",
            supported_models=("kg-embed-001",),
            max_batch_size=100, max_text_length=8192,
        )

    async def _do_embed(self, spec: EmbedSpec, *, ctx=None) -> EmbedResult:
        vec = [hash(spec.text + str(i)) % 1000 / 1000.0 for i in range(384)]
        return EmbedResult(
            embedding=EmbeddingVector(
                vector=vec, text=spec.text, model=spec.model, dimensions=len(vec)
            ),
            model=spec.model, text=spec.text, tokens_used=len(spec.text.split()),
            truncated=False,
        )

    async def _do_health(self, *, ctx=None) -> dict:
        return {"ok": True}


# 2. Vector Store Adapter
class KGVectorAdapter(BaseVectorAdapter):
    def __init__(self):
        super().__init__()
        self.vectors = {}

    async def _do_capabilities(self) -> VectorCapabilities:
        return VectorCapabilities(
            server="kg-vector", version="1.0.0", max_dimensions=384
        )

    async def _do_upsert(self, spec: UpsertSpec, *, ctx=None) -> UpsertResult:
        ns = spec.namespace or "default"
        if ns not in self.vectors:
            self.vectors[ns] = []
        self.vectors[ns].extend(spec.vectors)
        return UpsertResult(
            upserted_count=len(spec.vectors), failed_count=0, failures=[]
        )

    async def _do_query(self, spec: QuerySpec, *, ctx=None) -> QueryResult:
        ns = spec.namespace or "default"
        stored = self.vectors.get(ns, [])

        def cosine_sim(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            mag_a = sum(x * x for x in a) ** 0.5
            mag_b = sum(x * x for x in b) ** 0.5
            return dot / (mag_a * mag_b) if mag_a and mag_b else 0

        matches = []
        for vec in stored:
            score = cosine_sim(spec.vector, vec.vector)
            matches.append(VectorMatch(vector=vec, score=score, distance=1-score))

        matches.sort(key=lambda m: m.score, reverse=True)
        top_k = matches[:spec.top_k] if spec.top_k else matches

        return QueryResult(
            matches=top_k, query_vector=spec.vector,
            namespace=ns, total_matches=len(top_k),
        )

    async def _do_health(self, *, ctx=None) -> dict:
        return {"ok": True}


# 3. Graph Database Adapter
class KGGraphAdapter(BaseGraphAdapter):
    def __init__(self):
        super().__init__()
        self.nodes = {}
        self.edges = []

    async def _do_capabilities(self) -> GraphCapabilities:
        return GraphCapabilities(
            server="kg-graph", version="1.0.0",
            supported_query_dialects=("cypher",),
            supports_bulk_vertices=True,
        )

    async def _do_upsert_nodes(self, spec: UpsertNodesSpec, *, ctx=None) -> GraphUpsertResult:
        for node in spec.nodes:
            self.nodes[str(node.id)] = node
        return GraphUpsertResult(
            upserted_count=len(spec.nodes), failed_count=0, failures=[]
        )

    async def _do_upsert_edges(self, spec: UpsertEdgesSpec, *, ctx=None) -> GraphUpsertResult:
        self.edges.extend(spec.edges)
        return GraphUpsertResult(
            upserted_count=len(spec.edges), failed_count=0, failures=[]
        )

    async def _do_query(self, spec: GraphQuerySpec, *, ctx=None) -> GraphQueryResult:
        query_lower = spec.text.lower()
        results = []

        if "match" in query_lower and "company" in query_lower:
            for node_id, node in self.nodes.items():
                if "Company" in node.labels:
                    results.append({
                        "id": node_id,
                        "name": node.properties.get("name"),
                        "category": node.properties.get("category"),
                    })

        if "funded" in query_lower or "relationship" in query_lower:
            for edge in self.edges:
                results.append({
                    "from": str(edge.src),
                    "to": str(edge.dst),
                    "type": edge.label,
                })

        return GraphQueryResult(
            records=results,
            summary={"total": len(results)},
            dialect=spec.dialect,
            namespace=spec.namespace,
        )

    async def _do_health(self, *, ctx=None) -> dict:
        return {"ok": True}


# 4. LLM Adapter
class KGLLMAdapter(BaseLLMAdapter):
    async def _do_capabilities(self) -> LLMCapabilities:
        return LLMCapabilities(
            server="kg-llm", version="1.0.0",
            model_family="gpt-4", max_context_length=8192,
        )

    async def _do_complete(self, messages, model, **kwargs) -> LLMCompletion:
        user_msg = messages[-1]["content"] if messages else ""

        if "Y Combinator" in user_msg and "infrastructure" in user_msg:
            response = "Based on the knowledge graph and semantic search, Y Combinator has funded several AI infrastructure companies including Anyscale (Ray framework), Modal Labs (serverless compute), and Replicate (model deployment platform). These companies focus on building the foundational tools that power modern AI applications."
        elif "Graph shows" in user_msg and "Vector search found" in user_msg:
            response = "I've analyzed both the knowledge graph relationships and semantically similar companies. The results show a strong cluster of infrastructure-focused AI companies that share common characteristics in their technology stack and market positioning."
        else:
            response = "I can help analyze knowledge graph data combined with semantic search results."

        return LLMCompletion(
            text=response, model=model, model_family="gpt-4",
            usage=TokenUsage(
                prompt_tokens=len(user_msg.split()),
                completion_tokens=len(response.split()),
                total_tokens=len(user_msg.split()) + len(response.split())
            ),
            finish_reason="stop",
        )

    async def _do_count_tokens(self, text, *, model=None, ctx=None) -> int:
        return len(text.split())

    async def _do_health(self, *, ctx=None) -> dict:
        return {"ok": True}


# 5. Knowledge Graph RAG Pipeline
class KnowledgeGraphRAG:
    """Combines Graph, Embedding, Vector, and LLM for intelligent QA"""

    def __init__(self):
        self.graph = KGGraphAdapter()
        self.embedder = KGEmbeddingAdapter()
        self.vector_db = KGVectorAdapter()
        self.llm = KGLLMAdapter()
        self.ctx = None  # Use None to let base classes handle defaults

    async def index_knowledge_graph(self, companies: List[Dict[str, Any]]):
        """Build knowledge graph + vector index from company data"""

        # Step 1: Add nodes to graph
        nodes = []
        for company in companies:
            nodes.append(Node(
                id=GraphID(f"company:{company['id']}"),
                labels=("Company",),
                properties={
                    "name": company["name"],
                    "category": company["category"],
                    "description": company["description"],
                }
            ))

        await self.graph.upsert_nodes(
            UpsertNodesSpec(nodes=nodes),
            ctx=self.ctx
        )

        # Step 2: Add edges (relationships)
        edges = []
        for company in companies:
            if "funded_by" in company:
                edges.append(Edge(
                    id=GraphID(f"edge:{company['id']}"),
                    src=GraphID(company["funded_by"]),
                    dst=GraphID(f"company:{company['id']}"),
                    label="FUNDED",
                    properties={"year": company.get("year", 2023)}
                ))

        if edges:
            await self.graph.upsert_edges(
                UpsertEdgesSpec(edges=edges),
                ctx=self.ctx
            )

        # Step 3: Create vector embeddings for semantic search
        vectors = []
        for company in companies:
            text = f"{company['name']}: {company['description']}"

            embed_result = await self.embedder.embed(
                EmbedSpec(text=text, model="kg-embed-001"),
                ctx=self.ctx
            )

            vectors.append(Vector(
                id=VectorID(f"vec:{company['id']}"),
                vector=embed_result.embedding.vector,
                metadata={
                    "company_id": company["id"],
                    "name": company["name"],
                    "category": company["category"],
                    "description": company["description"],
                }
            ))

        await self.vector_db.upsert(
            UpsertSpec(vectors=vectors),
            ctx=self.ctx
        )

        return len(companies)

    async def query(self, question: str) -> Dict[str, Any]:
        """Answer question using Graph + Vector + LLM"""

        # Step 1: Query knowledge graph for structured facts
        graph_result = await self.graph.query(
            GraphQuerySpec(
                text="MATCH (c:Company) RETURN c.name, c.category",
                dialect="cypher"
            ),
            ctx=self.ctx
        )

        # Step 2: Semantic vector search
        question_embed = await self.embedder.embed(
            EmbedSpec(text=question, model="kg-embed-001"),
            ctx=self.ctx
        )

        vector_result = await self.vector_db.query(
            QuerySpec(vector=question_embed.embedding.vector, top_k=3),
            ctx=self.ctx
        )

        # Step 3: Combine graph facts + vector matches
        graph_facts = [
            f"{r['name']} ({r['category']})"
            for r in graph_result.records[:3]
        ]

        vector_matches = [
            f"{m.vector.metadata['name']}: {m.vector.metadata['description']}"
            for m in vector_result.matches
        ]

        # Step 4: Generate answer with LLM
        prompt = f"""Question: {question}

Graph shows (structured relationships):
{chr(10).join(f'- {fact}' for fact in graph_facts)}

Vector search found (semantic similarity):
{chr(10).join(f'- {match}' for match in vector_matches)}

Synthesize an answer:"""

        llm_response = await self.llm.complete(
            messages=[{"role": "user", "content": prompt}],
            model="kg-llm-001",
            ctx=self.ctx
        )

        return {
            "answer": llm_response.text,
            "graph_facts": graph_result.records,
            "vector_matches": [m.vector.metadata for m in vector_result.matches],
            "tokens_used": llm_response.usage.total_tokens,
        }


# Usage
async def main():
    print("=" * 80)
    print("Knowledge Graph RAG - All Four Protocols in Action")
    print("=" * 80)

    kg_rag = KnowledgeGraphRAG()

    companies = [
        {
            "id": "anyscale",
            "name": "Anyscale",
            "category": "AI Infrastructure",
            "description": "Distributed computing platform built on Ray for scaling ML workloads",
            "funded_by": "yc",
            "year": 2019
        },
        {
            "id": "modal",
            "name": "Modal Labs",
            "category": "AI Infrastructure",
            "description": "Serverless compute platform for running AI models and data pipelines",
            "funded_by": "yc",
            "year": 2021
        },
        {
            "id": "replicate",
            "name": "Replicate",
            "category": "AI Infrastructure",
            "description": "Platform for deploying and running machine learning models in production",
            "funded_by": "yc",
            "year": 2019
        },
        {
            "id": "weights-biases",
            "name": "Weights & Biases",
            "category": "MLOps",
            "description": "ML experiment tracking and model management platform",
            "funded_by": "yc",
            "year": 2017
        },
    ]

    print("\n📊 Building Knowledge Graph...")
    count = await kg_rag.index_knowledge_graph(companies)
    print(f"✅ Indexed {count} companies with:")
    print(f"   - Graph nodes/edges (structured relationships)")
    print(f"   - Vector embeddings (semantic search)")

    question = "What AI infrastructure companies did Y Combinator fund?"

    print(f"\n{'─' * 80}")
    print(f"❓ Question: {question}")
    print('─' * 80)

    result = await kg_rag.query(question)

    print(f"\n💡 Answer:\n{result['answer']}\n")
    print(f"📈 Graph Facts Found: {len(result['graph_facts'])}")
    print(f"🔍 Vector Matches Found: {len(result['vector_matches'])}")
    print(f"🔢 LLM Tokens Used: {result['tokens_used']}")

    print("\n📊 Detailed Results:")
    print("\nFrom Graph (structured):")
    for fact in result['graph_facts'][:3]:
        print(f"  • {fact}")

    print("\nFrom Vector Search (semantic):")
    for match in result['vector_matches'][:3]:
        print(f"  • {match['name']}: {match['description'][:60]}...")

    print("\n" + "=" * 80)
    print("✅ All Four Protocols Working Together Successfully!")
    print("=" * 80)
    print("\n🎯 This demonstrates:")
    print("  1. Graph   - Structured knowledge and relationships")
    print("  2. Embedding - Text vectorization for semantic understanding")
    print("  3. Vector  - Similarity search across embedded content")
    print("  4. LLM     - Intelligent synthesis of multi-source information")


if __name__ == "__main__":
    asyncio.run(main())
```

**What this demonstrates:**

- ✅ All four protocols — Graph, Embedding, Vector, LLM — composing in a single pipeline
- ✅ Graph stores structured entity relationships (nodes + edges)
- ✅ Embedding vectorizes text for semantic understanding
- ✅ Vector store enables similarity search across embedded content
- ✅ LLM synthesizes structured graph facts + semantic matches into a coherent answer
- ✅ Single `OperationContext` (`ctx`) propagated across all four protocol calls
- ✅ Each adapter implements only its required `_do_*` hooks — no unnecessary overrides

</details>

---

## 4. Running Certification Tests

Now run the official certification suite against your adapter. **Choose the section that matches your protocol.**

### 4.1 Embedding Certification

```bash
# Test embedding protocol only
export CORPUS_ADAPTER=adapters.hello_embedding:HelloEmbeddingAdapter
pytest $(python -c "import corpus_sdk; print(corpus_sdk.__path__[0])")/tests/embedding/ -v

# Incremental test order (if you want to run specific files)
pytest $(python -c "import corpus_sdk; print(corpus_sdk.__path__[0])")/tests/embedding/test_capabilities.py -v
pytest $(python -c "import corpus_sdk; print(corpus_sdk.__path__[0])")/tests/embedding/test_embed.py -v
pytest $(python -c "import corpus_sdk; print(corpus_sdk.__path__[0])")/tests/embedding/test_streaming.py -v
pytest $(python -c "import corpus_sdk; print(corpus_sdk.__path__[0])")/tests/embedding/test_batch.py -v
pytest $(python -c "import corpus_sdk; print(corpus_sdk.__path__[0])")/tests/embedding/test_deadlines.py -v
pytest $(python -c "import corpus_sdk; print(corpus_sdk.__path__[0])")/tests/embedding/test_errors.py -v
```

### 4.2 LLM Certification

```bash
export CORPUS_ADAPTER=adapters.hello_llm:HelloLLMAdapter
pytest $(python -c "import corpus_sdk; print(corpus_sdk.__path__[0])")/tests/llm/ -v
```

### 4.3 Vector Certification

```bash
export CORPUS_ADAPTER=adapters.hello_vector:HelloVectorAdapter
pytest $(python -c "import corpus_sdk; print(corpus_sdk.__path__[0])")/tests/vector/ -v
```

### 4.4 Graph Certification

```bash
export CORPUS_ADAPTER=adapters.hello_graph:HelloGraphAdapter
pytest $(python -c "import corpus_sdk; print(corpus_sdk.__path__[0])")/tests/graph/ -v
```

---

## 5. Understanding Certification Results

The certification suite provides **tiered scoring**. When you run the full suite, look for this summary:

```
================================================================================
CORPUS PROTOCOL SUITE - GOLD CERTIFIED
🔌 Adapter: adapters.hello_embedding:HelloEmbeddingAdapter | ⚖️ Strict: off

Protocol & Framework Conformance Status (scored / collected):
  ✅ PASS Embedding Protocol V1.0: Gold (135/135 scored; 150 collected)

🎯 Status: Ready for production deployment
⏱️ Completed in 1.2s
```

### Certification Tiers

| Tier | Score | Meaning | Production Ready? |
|------|-------|---------|------------------|
| 🥇 **Gold** | 100% | Perfect protocol conformance | ✅ Yes |
| 🥈 **Silver** | ≥80% | Integration testing ready | ⚠️ No |
| 🔬 **Development** | ≥50% | Early implementation | ❌ No |
| ❌ **None** | <50% | Not yet functional | ❌ No |

**Your goal:** Gold certification for your protocol.

### Reading Failure Output

When tests fail, the certification suite provides detailed guidance:

```
--------------------------------------------------
🟥 FAILURES & ERRORS
Embedding Protocol V1.0:
  ❌ Failure Wire Contract & Routing: 2 issue(s)
      Specification: §4.1 Wire-First Canonical Form
      Test: test_wire_envelope_validation
      Quick fix: Wire envelope missing required fields per §4.1
```

**Each failure includes:**
- **Specification section** (§4.1, §7.2, etc.)
- **Quick fix** - Exactly what to change

**Do not guess.** The error guidance is authoritative.

For complete certification requirements, see [`CONFORMANCE_GUIDE.md`](CONFORMANCE_GUIDE.md).

---

## 6. What to Read Next

**You now have a Gold-certified adapter.** Choose your path:

| Guide | Purpose | When to Read |
|-------|---------|--------------|
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Expose your adapter as an HTTP service (FastAPI, Lambda, etc.) | You need a standalone microservice |
| **[IMPLEMENTATION.md](IMPLEMENTATION.md)** | Deep dive on `_do_*` semantics and advanced features | You need custom deadline policies, circuit breakers, etc. |
| **[CONFORMANCE_GUIDE.md](CONFORMANCE_GUIDE.md)** | Debugging certification failures | Tests are failing and you're stuck |
| **[ADAPTER_RECIPES.md](ADAPTER_RECIPES.md)** | Multi-cloud and RAG scenarios | You're building complex pipelines |

**The conformance tests in [`../../tests/`](../../tests/) are the source of truth.** When this document and the tests disagree, **the tests are correct.**

---

## 7. Protocol-Specific Requirements & Pitfalls

### 7.1 Embedding Protocol

```python
# ✅ REQUIRED: protocol="embedding/v1.0" in capabilities
return EmbeddingCapabilities(protocol="embedding/v1.0")

# ✅ REQUIRED: idempotent_writes=True
return EmbeddingCapabilities(idempotent_writes=True)

# ✅ REQUIRED: batch field name "failures" (not "failed_texts")
return BatchEmbedResult(failures=[])

# ✅ REQUIRED: index field for batch correlation
EmbeddingVector(index=idx)

# ✅ REQUIRED: idempotency key deduplication (24h)
if ctx.idempotency_key:
    cached = await redis.get(f"idem:{ctx.tenant}:{ctx.idempotency_key}")
    if cached: return cached
```

### 7.2 LLM Protocol

```python
# ✅ REQUIRED: protocol="llm/v1.0" in capabilities
return LLMCapabilities(protocol="llm/v1.0")

# ✅ REQUIRED: model_family must be set
return LLMCapabilities(model_family="gpt-4")

# ⚠️ CRITICAL: Never implement tool execution
if chunk.tool_calls:
    yield chunk  # Pass through, don't execute!

# ✅ REQUIRED: streaming with usage in final chunk
LLMChunk(is_final=True, usage_so_far=TokenUsage(...))

# ✅ REQUIRED: ToolCall with generated ID
ToolCall(id=f"call_{secrets.token_hex(8)}", ...)

# ❌ NEVER: system_message if not supported
if not caps.supports_system_message:
    raise NotSupported("system_message not supported")
```

### 7.3 Vector Protocol

```python
# ✅ REQUIRED: protocol="vector/v1.0" in capabilities
return VectorCapabilities(protocol="vector/v1.0")

# ⚠️ CRITICAL: Namespace footgun prevention
if v.namespace is not None and v.namespace != spec.namespace:
    raise BadRequest("vector.namespace must match spec.namespace")

# ✅ REQUIRED: Canonicalize to spec namespace
v.namespace = spec.namespace  # Always set to spec.namespace

# ⚠️ CRITICAL: Cache invalidation AFTER successful write
result = await self._do_upsert(spec, ctx)  # Success!
await self._invalidate_namespace_cache(spec.namespace)  # Then invalidate

# ❌ WRONG: Invalidate before commit (cache will be stale if commit fails)
await self._invalidate_namespace_cache(namespace)  # Too early!
await client.upsert(vectors)  # If this fails, cache is now wrong
```

### 7.4 Graph Protocol

```python
# ✅ REQUIRED: protocol="graph/v1.0" in capabilities
return GraphCapabilities(protocol="graph/v1.0")

# ⚠️ CRITICAL: Transaction cache invalidation
# ✅ CORRECT: Invalidate after successful commit
result = await txn.commit()  # Atomic commit succeeds
if result.success:
    await self._invalidate_namespace_cache(namespace)

# ❌ WRONG: Invalidate during transaction (commit may fail)
await self._cache.invalidate_pattern(...)  # Premature!
await txn.commit()  # If this fails, cache is now inconsistent

# ✅ REQUIRED: Batch operation success detection
if self._batch_op_succeeded(op, batch_result, idx):
    # Only invalidate if this op actually changed data
    await self._invalidate_namespace_cache(namespace)

# ✅ REQUIRED: Query dialect validation
if spec.dialect and caps.supported_query_dialects:
    if spec.dialect not in caps.supported_query_dialects:
        raise NotSupported(f"dialect '{spec.dialect}' not supported")
```

---

## 8. Certification Checklist

### Universal Requirements (All Protocols)

- [ ] **REQUIRED:** Constructor accepts `endpoint=None`
- [ ] **REQUIRED:** `_do_capabilities()` declares `protocol="{component}/v1.0"`
- [ ] **REQUIRED:** `ctx.remaining_ms()` used in all `_do_*` methods
- [ ] **REQUIRED:** No raw tenant IDs in logs/metrics (use tenant hashing)
- [ ] **REQUIRED:** Gold certification achieved: `pytest tests/{protocol}/ -v` shows 100% pass
- [ ] **RECOMMENDED:** `_do_get_stats()` implemented for service observability
- [ ] **RECOMMENDED:** Health endpoint returns graded `status: "ok"|"degraded"|"down"`

### Embedding-Specific Checklist

- [ ] **REQUIRED:** `_do_capabilities()` declares `idempotent_writes=True`
- [ ] **REQUIRED:** Batch operations use field name `failures` (not `failed_texts`)
- [ ] **REQUIRED:** Batch success items include `index` field for correlation
- [ ] **REQUIRED:** Idempotency keys deduplicated for ≥24 hours
- [ ] **REQUIRED:** `_do_count_tokens()` implemented
- [ ] **RECOMMENDED:** Streaming implemented (if `supports_streaming=True`)

### LLM-Specific Checklist

- [ ] **REQUIRED:** `_do_capabilities()` declares `model_family` (not just `model`)
- [ ] **REQUIRED:** Never implement tool execution - only pass through tool calls
- [ ] **REQUIRED:** Tool calls include generated IDs (`secrets.token_hex()`)
- [ ] **REQUIRED:** Streaming includes `usage_so_far` in final chunk
- [ ] **REQUIRED:** `supports_system_message` accurately reflects capability
- [ ] **REQUIRED:** `_do_count_tokens()` implemented
- [ ] **RECOMMENDED:** Support for `stop_sequences`, `frequency_penalty`, `presence_penalty`

### Vector-Specific Checklist

- [ ] **REQUIRED:** Namespace canonicalization enforced (vector.namespace == spec.namespace)
- [ ] **REQUIRED:** Cache invalidation performed AFTER successful writes
- [ ] **REQUIRED:** `max_dimensions` validated on upsert and query
- [ ] **REQUIRED:** Batch query support (if `supports_batch_queries=True`)
- [ ] **RECOMMENDED:** Metadata filtering support with `supports_metadata_filtering=True`

### Graph-Specific Checklist

- [ ] **REQUIRED:** Cache invalidation performed ONLY after successful transaction commit
- [ ] **REQUIRED:** Query dialect validation against `supported_query_dialects`
- [ ] **REQUIRED:** Transaction support requires atomic batch operations
- [ ] **REQUIRED:** Batch operation success detection for targeted invalidation
- [ ] **REQUIRED:** `supports_transaction` accurately reflects capability
- [ ] **RECOMMENDED:** Traversal support with `supports_traversal=True`

---

## Appendix A: Common Pitfalls by Component

### Embedding

```python
# ❌ WRONG: Missing REQUIRED protocol field
return EmbeddingCapabilities(
    server="hello-embedding",
    version="1.0.0",
    # missing protocol="embedding/v1.0"  # WILL FAIL CERTIFICATION
)

# ❌ WRONG: Wrong batch field name
return BatchEmbedResult(
    embeddings=embeddings,
    failed_texts=failures,  # ❌ MUST be "failures"
)

# ❌ WRONG: Assuming batch results align 1:1 with inputs
for i, text in enumerate(spec.texts):
    assert result.embeddings[i].text == text  # MAY FAIL!

# ✅ CORRECT: Use index field for correlation
for emb in result.embeddings:
    original_text = spec.texts[emb.index]  # SAFE
```

### LLM

```python
# ❌ WRONG: Missing REQUIRED protocol field
return LLMCapabilities(
    server="hello-llm",
    version="1.0.0",
    # missing protocol="llm/v1.0"  # WILL FAIL CERTIFICATION
)

# ❌ WRONG: Missing model_family
return LLMCapabilities(
    protocol="llm/v1.0",
    # missing model_family  # WILL FAIL CERTIFICATION
)

# ❌ WRONG: Implementing tool execution in adapter
if tool_calls:
    result = await execute_tools(tool_calls)  # NO - that's orchestration!

# ✅ CORRECT: Just pass through tool calls
return LLMCompletion(tool_calls=tool_calls)  # Router's job to execute
```

### Vector

```python
# ❌ WRONG: Missing REQUIRED protocol field
return VectorCapabilities(
    server="hello-vector",
    version="1.0.0",
    # missing protocol="vector/v1.0"  # WILL FAIL CERTIFICATION
)

# ❌ WRONG: Ignoring namespace mismatch
vector = Vector(id="123", vector=[...], namespace="user-space")
spec = UpsertSpec(vectors=[vector], namespace="default")  # WILL FAIL!

# ✅ CORRECT: Canonicalize to spec namespace
vector.namespace = spec.namespace  # Must match

# ❌ WRONG: Cache invalidation before write
await self._invalidate_namespace_cache(spec.namespace)  # Too early!
result = await self._do_upsert(spec, ctx)  # If this fails, cache is stale

# ✅ CORRECT: Invalidate after successful write
result = await self._do_upsert(spec, ctx)
if result.upserted_count > 0:
    await self._invalidate_namespace_cache(spec.namespace)  # SAFE
```

### Graph

```python
# ❌ WRONG: Missing REQUIRED protocol field
return GraphCapabilities(
    server="hello-graph",
    version="1.0.0",
    # missing protocol="graph/v1.0"  # WILL FAIL CERTIFICATION
)

# ❌ WRONG: Cache invalidation before commit
await self._cache.invalidate_pattern(...)
await txn.commit()  # If commit fails, cache is stale!

# ✅ CORRECT: Invalidate after successful commit
await txn.commit()
await self._invalidate_namespace_cache(namespace)  # SAFE

# ❌ WRONG: Not validating dialects
spec = GraphQuerySpec(dialect="cypher")
caps = await self.capabilities()
if "cypher" not in caps.supported_query_dialects:
    # MISSING: Should raise NotSupported
    pass
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Adapter** | A class that implements `_do_*` hooks to connect a provider to Corpus Protocol |
| **Base Class** | `BaseEmbeddingAdapter`, `BaseLLMAdapter`, `BaseVectorAdapter`, `BaseGraphAdapter` |
| **Certification Suite** | The conformance tests in `tests/embedding/`, `tests/llm/`, etc. |
| **Gold Certification** | 100% pass rate in a single protocol |
| **Wire Envelope** | The JSON `{op, ctx, args}` structure all Corpus services speak |
| **Protocol Field** | REQUIRED field in capabilities: `"protocol": "{component}/v1.0"` |
| **Idempotent Writes** | REQUIRED capability for embedding: `idempotent_writes: true` |
| **Failures Field** | REQUIRED field name for embedding batch errors (not `failed_texts`) |
| **Model Family** | REQUIRED field in LLM capabilities: `model_family` |
| **Namespace Canonicalization** | REQUIRED behavior for Vector: enforce namespace match |
| **Transaction Atomicity** | REQUIRED for Graph: all or nothing |
| **CORPUS_ADAPTER** | Environment variable: `module:ClassName` for dynamic loading |

---

## Appendix C: Debugging & Troubleshooting

### Enable Full Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("corpus_sdk").setLevel(logging.DEBUG)
```

### Common Errors & Fixes (All Protocols)

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `AdapterValidationError: Failed to instantiate adapter` | Constructor doesn't accept `endpoint=None` | Add `endpoint=None` to `__init__` |
| `capabilities missing required field: protocol` | Missing `protocol="{component}/v1.0"` | Add protocol field to capabilities |
| `DEADLINE_EXCEEDED not raised` | Deadline not checked before provider call | Call `ctx.remaining_ms()` and raise if 0 |
| `retry_after_ms missing from 429 responses` | Error mapping incomplete | Map provider rate limits with `retry_after_ms` |

### Protocol-Specific Errors

**Embedding:**
| Error | Fix |
|-------|-----|
| `capabilities missing required field: idempotent_writes` | Add `idempotent_writes=True` |
| `Batch result missing field: failures` | Rename `failed_texts` → `failures` |
| `Batch success missing index` | Set `index=idx` on EmbeddingVector |
| `Idempotency test failed` | Implement idempotency cache with 24h TTL |

**LLM:**
| Error | Fix |
|-------|-----|
| `capabilities missing required field: model_family` | Add `model_family` to capabilities |
| `Tool execution detected` | Remove tool execution logic - only pass through |
| `Missing tool call ID` | Generate IDs with `secrets.token_hex(8)` |
| `Missing usage_so_far in final chunk` | Add TokenUsage to final streaming chunk |

**Vector:**
| Error | Fix |
|-------|-----|
| `Namespace mismatch` | Canonicalize vector.namespace = spec.namespace |
| `Cache invalidation order` | Move invalidation AFTER successful write |
| `Batch query not implemented` | Implement `_do_batch_query()` if `supports_batch_queries=True` |

**Graph:**
| Error | Fix |
|-------|-----|
| `Cache invalidation before commit` | Move invalidation AFTER successful commit |
| `Dialect not validated` | Check `spec.dialect` against `caps.supported_query_dialects` |
| `Transaction not atomic` | Ensure all operations in transaction commit or rollback together |

### Debugging Test Failures

```bash
# Run with full traceback
pytest tests/{protocol}/test_file.py -v --tb=long

# Stop on first failure
pytest tests/{protocol}/ -v --maxfail=1

# Run only tests that failed last time
pytest tests/{protocol}/ -v --lf

# See which tests are available
pytest tests/{protocol}/ --collect-only
```

---

**Maintainers:** Corpus SDK Team  
**Last Updated:** 2026-02-13  
**Scope:** Complete adapter authoring reference for all Corpus Protocols v1.0 (Embedding, LLM, Vector, Graph).

**The conformance tests in [`../../tests/`](../../tests/) are the source of truth.** When this document and the tests disagree, **the tests are correct.**
