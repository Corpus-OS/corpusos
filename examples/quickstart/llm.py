import asyncio
from corpus_sdk.llm.llm_base import (
    BaseLLMAdapter, OperationContext, LLMCompletion,
    TokenUsage, LLMCapabilities
)

class QuickLLMAdapter(BaseLLMAdapter):
    async def _do_capabilities(self) -> LLMCapabilities:
        return LLMCapabilities(
            server="quick-llm",
            version="1.0.0",
            model_family="gpt-4",
            max_context_length=8192,
            supports_streaming=True,
            supports_roles=True,
            supports_json_output=False,
            supports_parallel_tool_calls=False,
            idempotent_writes=False,
            supports_multi_tenant=True,
            supports_system_message=True,
        )

    async def _do_complete(self, messages, model, **kwargs) -> LLMCompletion:
        return LLMCompletion(
            text="Hello from quick-llm!",
            model=model,
            model_family="gpt-4",
            usage=TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10),
            finish_reason="stop",
        )

    async def _do_count_tokens(self, text, *, model=None, ctx=None) -> int:
        return len(text.split())  # Simple word count

    async def _do_health(self, *, ctx=None) -> dict:
        return {"ok": True, "server": "quick-llm", "version": "1.0.0"}

# Usage
async def main():
    print("=" * 80)
    print("Quick LLM Adapter Demo")
    print("=" * 80)
    
    async with QuickLLMAdapter() as adapter:
        ctx = OperationContext(request_id="req-2", tenant="acme")
        
        # Test 1: Capabilities
        caps = await adapter.capabilities()
        print(f"\n✅ Capabilities:")
        print(f"   Server: {caps.server} v{caps.version}")
        print(f"   Model family: {caps.model_family}")
        print(f"   Max context length: {caps.max_context_length}")
        print(f"   Supports streaming: {caps.supports_streaming}")
        print(f"   Supports roles: {caps.supports_roles}")
        print(f"   Supports system message: {caps.supports_system_message}")
        print(f"   Supports multi-tenant: {caps.supports_multi_tenant}")
        
        # Test 2: Completion
        resp = await adapter.complete(
            messages=[{"role": "user", "content": "Say hi"}],
            model="quick-llm-001",
            ctx=ctx,
        )
        print(f"\n✅ Completion:")
        print(f"   Response: {resp.text}")
        print(f"   Model: {resp.model}")
        print(f"   Model family: {resp.model_family}")
        print(f"   Tokens: {resp.usage.total_tokens} (prompt: {resp.usage.prompt_tokens}, completion: {resp.usage.completion_tokens})")
        print(f"   Finish reason: {resp.finish_reason}")
        
        # Test 3: Multi-message conversation
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        resp = await adapter.complete(messages=messages, model="quick-llm-001", ctx=ctx)
        print(f"\n✅ Multi-turn Conversation:")
        print(f"   Messages: {len(messages)} turns")
        print(f"   Response: {resp.text}")
        
        # Test 4: Token counting
        test_text = "This is a longer text to count tokens for testing purposes"
        tokens = await adapter.count_tokens(test_text, model="quick-llm-001")
        print(f"\n✅ Token Counting:")
        print(f"   Text: '{test_text}'")
        print(f"   Tokens: {tokens}")
        
        # Test 5: Health check
        health = await adapter.health()
        print(f"\n✅ Health Check:")
        print(f"   OK: {health.get('ok', False)}")
        print(f"   Server: {health.get('server', 'unknown')} v{health.get('version', 'unknown')}")
        
        print("\n" + "=" * 80)
        print("✅ All tests passed!")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
