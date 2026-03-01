import asyncio
from corpus_sdk.embedding.embedding_base import (
    BaseEmbeddingAdapter, EmbedSpec, OperationContext,
    EmbeddingVector, EmbeddingCapabilities, EmbedResult
)

class QuickEmbeddingAdapter(BaseEmbeddingAdapter):
    async def _do_capabilities(self) -> EmbeddingCapabilities:
        return EmbeddingCapabilities(
            server="quick-embeddings",
            version="1.0.0",
            supported_models=("quick-embed-001",),
            max_batch_size=128,
            max_text_length=8192,
            supports_normalization=True,
            normalizes_at_source=False,
            supports_deadline=True,
            supports_token_counting=False,
        )

    async def _do_embed(self, spec: EmbedSpec, *, ctx=None) -> EmbedResult:
        vec = [0.1, 0.2, 0.3]
        return EmbedResult(
            embedding=EmbeddingVector(
                vector=vec,
                text=spec.text,
                model=spec.model,
                dimensions=len(vec)
            ),
            model=spec.model,
            text=spec.text,
            tokens_used=None,
            truncated=False,
        )

    async def _do_health(self, *, ctx=None) -> dict:
        return {"ok": True, "server": "quick-embeddings", "version": "1.0.0"}

# Usage
async def main():
    print("=" * 80)
    print("Quick Embedding Adapter Demo")
    print("=" * 80)
    
    async with QuickEmbeddingAdapter() as adapter:
        ctx = OperationContext(request_id="req-1", tenant="acme")
        
        # Test 1: Capabilities
        caps = await adapter.capabilities()
        print(f"\n✅ Capabilities:")
        print(f"   Server: {caps.server} v{caps.version}")
        print(f"   Supported models: {caps.supported_models}")
        print(f"   Max batch size: {caps.max_batch_size}")
        print(f"   Max text length: {caps.max_text_length}")
        print(f"   Supports normalization: {caps.supports_normalization}")
        print(f"   Supports deadline: {caps.supports_deadline}")
        
        # Test 2: Embedding
        res = await adapter.embed(
            EmbedSpec(text="hello world", model="quick-embed-001"), ctx=ctx
        )
        print(f"\n✅ Embedding:")
        print(f"   Text: '{res.text}'")
        print(f"   Vector: {res.embedding.vector}")
        print(f"   Dimensions: {res.embedding.dimensions}")
        print(f"   Model: {res.model}")
        print(f"   Truncated: {res.truncated}")
        
        # Test 3: Multiple embeddings
        texts = ["first text", "second text", "third text"]
        print(f"\n✅ Multiple Embeddings:")
        for i, text in enumerate(texts, 1):
            res = await adapter.embed(
                EmbedSpec(text=text, model="quick-embed-001"), ctx=ctx
            )
            print(f"   {i}. '{text}' → {res.embedding.dimensions}D vector")
        
        # Test 4: Health check
        health = await adapter.health()
        print(f"\n✅ Health Check:")
        print(f"   OK: {health.get('ok', False)}")
        print(f"   Server: {health.get('server', 'unknown')} v{health.get('version', 'unknown')}")
        
        print("\n" + "=" * 80)
        print("✅ All tests passed!")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
