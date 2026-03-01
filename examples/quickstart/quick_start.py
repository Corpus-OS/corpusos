import asyncio
from corpus_sdk.llm.llm_base import (
    BaseLLMAdapter, OperationContext, LLMCompletion,
    LLMCapabilities, TokenUsage
)

class QuickAdapter(BaseLLMAdapter):
    async def _do_capabilities(self) -> LLMCapabilities:
        return LLMCapabilities(
            server="quick-demo",
            version="1.0.0",
            model_family="demo",
            max_context_length=4096,
        )
    
    async def _do_complete(self, messages, model=None, **kwargs) -> LLMCompletion:
        return LLMCompletion(
            text="Hello from CORPUS!",
            model=model or "quick-demo",
            model_family="demo",
            usage=TokenUsage(prompt_tokens=2, completion_tokens=3, total_tokens=5),
            finish_reason="stop",
        )
    
    async def _do_count_tokens(self, text, *, model=None, ctx=None) -> int:
        return len(text.split())  # Simple word count
    
    async def _do_health(self, *, ctx=None) -> dict:
        return {"ok": True, "server": "quick-demo"}

# Usage
async def main():
    print("=" * 80)
    print("Quick LLM Adapter Demo")
    print("=" * 80)
    
    adapter = QuickAdapter()
    ctx = OperationContext(request_id="test-123")
    
    # Test 1: Capabilities
    caps = await adapter.capabilities()
    print(f"\n✅ Capabilities:")
    print(f"   Server: {caps.server} v{caps.version}")
    print(f"   Model family: {caps.model_family}")
    print(f"   Max context: {caps.max_context_length}")
    
    # Test 2: Completion
    result = await adapter.complete(
        messages=[{"role": "user", "content": "Hi"}], 
        ctx=ctx
    )
    print(f"\n✅ Completion:")
    print(f"   Response: {result.text}")
    print(f"   Model: {result.model}")
    print(f"   Tokens used: {result.usage.total_tokens} (prompt: {result.usage.prompt_tokens}, completion: {result.usage.completion_tokens})")
    print(f"   Finish reason: {result.finish_reason}")
    
    # Test 3: Token counting
    tokens = await adapter.count_tokens("This is a test message")
    print(f"\n✅ Token Counting:")
    print(f"   Text: 'This is a test message'")
    print(f"   Tokens: {tokens}")
    
    # Test 4: Health check
    health = await adapter.health()
    print(f"\n✅ Health Check:")
    print(f"   OK: {health.get('ok', False)}")
    print(f"   Server: {health.get('server', 'unknown')}")
    
    print("\n" + "=" * 80)
    print("✅ All tests passed!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
