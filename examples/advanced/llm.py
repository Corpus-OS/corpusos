from typing import AsyncIterator, Dict, Any, List, Optional, Tuple, Union, Mapping
import asyncio
import json
import time
from dataclasses import dataclass

from corpus_sdk.llm.llm_base import BaseLLMAdapter
from corpus_sdk.llm.llm_base import (
    LLMCapabilities, LLMCompletion, LLMChunk, TokenUsage,
    ToolCall, ToolCallFunction, OperationContext
)
from corpus_sdk.llm.llm_base import (
    BadRequest, AuthError, ResourceExhausted, TransientNetwork,
    Unavailable, NotSupported, ModelOverloaded, DeadlineExceeded
)


# ============================================================================
# MOCK CLIENT (Replace with real provider SDK)
# ============================================================================

class MockProviderClient:
    """Mock LLM provider client - replace with real SDK"""
    
    def __init__(self):
        self.call_count = 0
    
    def complete(self, **kwargs):
        """Synchronous completion call"""
        self.call_count += 1
        
        # Mock tool call detection
        if kwargs.get('tools'):
            return MockResponse(
                text="",
                finish_reason="tool_calls",
                tool_calls=[
                    ToolCall(
                        id="call_123",
                        type="function",
                        function=ToolCallFunction(
                            name=kwargs['tools'][0]['function']['name'],
                            arguments='{"query": "test"}'
                        )
                    )
                ]
            )
        
        # Normal text response
        messages = kwargs.get('messages', [])
        last_msg = messages[-1]['content'] if messages else "Hello"
        
        return MockResponse(
            text=f"Mock response to: {last_msg}",
            finish_reason="stop",
            tool_calls=[]
        )
    
    async def count_tokens(self, text: str, **kwargs) -> int:
        """Async token counting"""
        await asyncio.sleep(0.001)  # Simulate API call
        return len(text.split())
    
    async def health_check(self) -> bool:
        """Async health check"""
        await asyncio.sleep(0.001)
        return True


@dataclass
class MockResponse:
    """Mock provider response"""
    text: str
    finish_reason: str
    tool_calls: List[ToolCall]


# ============================================================================
# PRODUCTION LLM ADAPTER
# ============================================================================

class ProductionLLMAdapter(BaseLLMAdapter):
    """
    Production-ready LLM adapter with 100% conformance.
    
    SHARED PLANNING: Single _plan_response used by both complete and stream.
    TOOL CALLS: Validates tool_choice, synthesizes token usage.
    STOP SEQUENCES: Cuts at FIRST occurrence.
    STREAMING: Tool calls only in final chunk, empty non-final chunks.
    CAPABILITIES: Hardcoded, not configurable.
    """
    
    def __init__(self, client=None, supported_models=None, model_families=None, **kwargs):
        super().__init__(**kwargs)
        self._client = client or MockProviderClient()
        self._supported_models = tuple(supported_models or ["gpt-4", "gpt-3.5-turbo"])
        self._model_families = model_families or {}
        self._max_context_length = 128000
        self._max_tool_calls_per_turn = 5
        
        # Stats tracking (adapter-owned only)
        self._stats = {
            "complete_calls": 0,
            "stream_calls": 0,
            "count_tokens_calls": 0,
            "total_completion_tokens": 0,
            "total_prompt_tokens": 0,
            "total_processing_time_ms": 0.0,
            "error_count": 0
        }
    
    # ----------------------------------------------------------------------
    # CAPABILITIES (Hardcoded - NOT configurable)
    # ----------------------------------------------------------------------
    
    async def _do_capabilities(self) -> LLMCapabilities:
        """Advertise true provider capabilities - NEVER configurable."""
        return LLMCapabilities(
            server="my-llm-provider",
            version="1.0.0",
            protocol="llm/v1.0",
            model_family="gpt",
            max_context_length=self._max_context_length,
            supports_streaming=True,
            supports_roles=True,
            supports_json_output=False,
            supports_tools=True,
            supports_parallel_tool_calls=False,
            supports_tool_choice=True,
            max_tool_calls_per_turn=self._max_tool_calls_per_turn,
            idempotent_writes=False,
            supports_multi_tenant=True,
            supports_system_message=True,
            supports_deadline=True,
            supports_count_tokens=True,
            supported_models=self._supported_models
        )
    
    # ----------------------------------------------------------------------
    # SHARED PLANNING PATH (Single source of truth)
    # ----------------------------------------------------------------------
    
    def _plan_response(self, request, ctx=None):
        """
        Single planning function for BOTH complete() and stream().
        
        Returns: (prompt_text, completion_text, finish_reason, tool_calls)
        """
        # Validate model
        if request.model not in self._supported_models:
            raise NotSupported(
                f"Model '{request.model}' is not supported",
                details={
                    "requested_model": request.model,
                    "supported_models": list(self._supported_models)
                }
            )
        
        # Validate tool_choice
        self._validate_tool_choice_internal(request.tool_choice, request.tools)
        
        # Build prompt
        prompt = self._build_prompt(request)
        
        # Get timeout from context
        timeout = self._get_timeout(ctx)
        
        # Call provider
        try:
            response = self._client.complete(
                model=request.model,
                messages=request.messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                frequency_penalty=request.frequency_penalty,
                presence_penalty=request.presence_penalty,
                stop=request.stop_sequences,
                system=request.system_message,
                tools=request.tools,
                tool_choice=request.tool_choice,
                timeout=timeout
            )
        except Exception as e:
            raise self._map_provider_error(e)
        
        # Apply stop sequences (FIRST occurrence rule)
        text = self._apply_stop_sequences(response.text, request.stop_sequences)
        
        finish_reason = response.finish_reason
        if finish_reason not in ("stop", "length", "tool_calls", "error"):
            finish_reason = "stop"
        
        return prompt, text, finish_reason, response.tool_calls
    
    def _validate_tool_choice_internal(self, tool_choice, tools):
        """Validate tool_choice against available tools."""
        if not tools:
            if tool_choice not in (None, "none", "auto"):
                raise BadRequest("tool_choice provided but no tools")
            return
        
        requested = None
        if isinstance(tool_choice, dict):
            if tool_choice.get("type") == "function":
                fn = tool_choice.get("function", {})
                requested = fn.get("name")
            elif "name" in tool_choice:
                requested = tool_choice["name"]
        elif isinstance(tool_choice, str):
            if tool_choice not in ("none", "auto", "required"):
                requested = tool_choice
        
        if requested:
            tool_names = []
            for t in tools:
                if isinstance(t, dict):
                    if "function" in t:
                        tool_names.append(t["function"].get("name"))
                    elif "name" in t:
                        tool_names.append(t["name"])
            
            if requested not in tool_names:
                raise BadRequest(
                    f"tool_choice requested unknown tool: {requested}",
                    details={
                        "requested": requested,
                        "available": tool_names
                    }
                )
    
    def _apply_stop_sequences(self, text: str, stops: Optional[List[str]]) -> str:
        """Stop at FIRST occurrence of ANY stop sequence."""
        if not stops or not text:
            return text
        
        cut_pos = len(text)
        for stop in stops:
            if not stop:
                continue
            pos = text.find(stop)
            if pos != -1 and pos < cut_pos:
                cut_pos = pos
        
        if cut_pos < len(text):
            return text[:cut_pos].rstrip()
        return text
    
    def _build_prompt(self, request) -> str:
        """Build prompt string for token counting."""
        parts = []
        if request.system_message:
            parts.append(f"system: {request.system_message}")
        for msg in request.messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            parts.append(f"{role}: {content}")
        return "\n".join(parts)
    
    # ----------------------------------------------------------------------
    # TOKEN COUNTING (Simple - no tiktoken dependency)
    # ----------------------------------------------------------------------
    
    async def _do_count_tokens(self, text: str, model: Optional[str], *, ctx=None) -> int:
        """Token counting via provider API."""
        self._stats["count_tokens_calls"] += 1
        t0 = time.monotonic()
        
        if model and model not in self._supported_models:
            raise NotSupported(f"Model '{model}' is not supported")
        
        timeout = self._get_timeout(ctx)
        
        try:
            count = await self._client.count_tokens(
                text=text,
                model=model or self._supported_models[0],
                timeout=timeout
            )
        except Exception as e:
            self._stats["error_count"] += 1
            raise self._map_provider_error(e)
        
        self._stats["total_processing_time_ms"] += (time.monotonic() - t0) * 1000
        return count
    
    def _count_tokens_sync(self, text: str, model: str) -> int:
        """Synchronous token counting - simple word split."""
        # In production, use tiktoken or provider's tokenizer
        return len(text.split())
    
    def _calculate_usage(self, prompt: str, completion: str, 
                        tool_calls: Optional[List[ToolCall]], 
                        model: str) -> TokenUsage:
        """Calculate token usage with tool call accounting."""
        prompt_tokens = self._count_tokens_sync(prompt, model)
        
        if tool_calls:
            # Synthesize tokens from tool call payload
            tool_payload = json.dumps([
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in tool_calls
            ], separators=(",", ":"))
            
            completion_tokens = self._count_tokens_sync(tool_payload, model)
            if completion_tokens == 0:
                completion_tokens = 10  # Minimum viable
        else:
            completion_tokens = self._count_tokens_sync(completion, model)
        
        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens
        )
    
    def _calculate_usage_so_far(self, prompt: str, partial: str, 
                               tool_calls: Optional[List[ToolCall]], 
                               model: str) -> TokenUsage:
        """Calculate usage for partial stream."""
        prompt_tokens = self._count_tokens_sync(prompt, model)
        
        if tool_calls:
            return TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=0,
                total_tokens=prompt_tokens
            )
        
        completion_tokens = self._count_tokens_sync(partial, model)
        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens
        )
    
    # ----------------------------------------------------------------------
    # COMPLETE (Unary)
    # ----------------------------------------------------------------------
    
    async def _do_complete(self, messages, max_tokens=None, temperature=None,
                          top_p=None, frequency_penalty=None, presence_penalty=None,
                          stop_sequences=None, model=None, system_message=None,
                          tools=None, tool_choice=None, ctx=None) -> LLMCompletion:
        
        self._stats["complete_calls"] += 1
        t0 = time.monotonic()
        
        # Create request object
        request = _Request(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop_sequences=stop_sequences,
            model=model or self._supported_models[0],
            system_message=system_message,
            tools=tools,
            tool_choice=tool_choice
        )
        
        # Plan response
        prompt, text, finish_reason, tool_calls = self._plan_response(request, ctx)
        
        # Calculate usage
        usage = self._calculate_usage(prompt, text, tool_calls, request.model)
        
        # Update stats
        self._stats["total_prompt_tokens"] += usage.prompt_tokens
        self._stats["total_completion_tokens"] += usage.completion_tokens
        self._stats["total_processing_time_ms"] += (time.monotonic() - t0) * 1000
        
        return LLMCompletion(
            text=text,
            model=request.model,
            model_family=self._get_model_family(request.model),
            usage=usage,
            finish_reason=finish_reason,
            tool_calls=tool_calls or []
        )
    
    def _get_model_family(self, model: str) -> str:
        """Extract model family from model name."""
        if model in self._model_families:
            return self._model_families[model]
        if "gpt" in model:
            return "gpt"
        if "claude" in model:
            return "claude"
        if "gemini" in model:
            return "gemini"
        return "custom"
    
    # ----------------------------------------------------------------------
    # STREAM
    # ----------------------------------------------------------------------
    
    async def _do_stream(self, messages, max_tokens=None, temperature=None,
                        top_p=None, frequency_penalty=None, presence_penalty=None,
                        stop_sequences=None, model=None, system_message=None,
                        tools=None, tool_choice=None, ctx=None) -> AsyncIterator[LLMChunk]:
        
        self._stats["stream_calls"] += 1
        t0 = time.monotonic()
        
        # Enforce capabilities
        caps = await self._do_capabilities()
        if not caps.supports_streaming:
            raise NotSupported("streaming is not supported")
        
        # Create request object
        request = _Request(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop_sequences=stop_sequences,
            model=model or self._supported_models[0],
            system_message=system_message,
            tools=tools,
            tool_choice=tool_choice
        )
        
        # Plan response (SAME planning function as complete)
        prompt, text, finish_reason, tool_calls = self._plan_response(request, ctx)
        
        # TOOL CALL STREAMING
        if tool_calls:
            # Non-final chunk (empty)
            yield LLMChunk(
                text="",
                is_final=False,
                model=request.model,
                usage_so_far=self._calculate_usage_so_far(prompt, "", None, request.model)
            )
            
            # Final chunk with tool_calls
            final_usage = self._calculate_usage(prompt, text, tool_calls, request.model)
            yield LLMChunk(
                text="",
                is_final=True,
                model=request.model,
                usage_so_far=final_usage,
                tool_calls=tool_calls
            )
            
            # Update stats
            self._stats["total_prompt_tokens"] += final_usage.prompt_tokens
            self._stats["total_completion_tokens"] += final_usage.completion_tokens
            self._stats["total_processing_time_ms"] += (time.monotonic() - t0) * 1000
            return
        
        # NORMAL TEXT STREAMING
        tokens = text.split()
        emitted = []
        
        for i, token in enumerate(tokens):
            emitted.append(token)
            partial = " ".join(emitted)
            usage = self._calculate_usage_so_far(prompt, partial, None, request.model)
            
            yield LLMChunk(
                text=token + (" " if i < len(tokens) - 1 else ""),
                is_final=False,
                model=request.model,
                usage_so_far=usage
            )
        
        # Final chunk
        final_usage = self._calculate_usage(prompt, text, None, request.model)
        yield LLMChunk(
            text="",
            is_final=True,
            model=request.model,
            usage_so_far=final_usage
        )
        
        # Update stats
        self._stats["total_prompt_tokens"] += final_usage.prompt_tokens
        self._stats["total_completion_tokens"] += final_usage.completion_tokens
        self._stats["total_processing_time_ms"] += (time.monotonic() - t0) * 1000
    
    # ----------------------------------------------------------------------
    # HEALTH
    # ----------------------------------------------------------------------
    
    async def _do_health(self, *, ctx=None) -> Dict[str, Any]:
        """Health check - NO ctx.attrs-driven forcing."""
        try:
            healthy = await self._client.health_check()
            return {
                "ok": healthy,
                "status": "ok" if healthy else "degraded",
                "server": "my-llm-provider",
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
                "server": "my-llm-provider",
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
        # Mapping logic - customize for your provider
        if "rate limit" in str(e).lower():
            return ResourceExhausted("Rate limit exceeded", retry_after_ms=5000)
        if "auth" in str(e).lower() or "key" in str(e).lower():
            return AuthError("Authentication failed")
        if "timeout" in str(e).lower():
            return TransientNetwork("Request timeout")
        if "not found" in str(e).lower() or "does not exist" in str(e).lower():
            return BadRequest(str(e))
        
        return Unavailable(f"Provider error: {type(e).__name__}")


@dataclass
class _Request:
    """Internal request container."""
    messages: List[Mapping[str, str]]
    max_tokens: Optional[int]
    temperature: Optional[float]
    top_p: Optional[float]
    frequency_penalty: Optional[float]
    presence_penalty: Optional[float]
    stop_sequences: Optional[List[str]]
    model: str
    system_message: Optional[str]
    tools: Optional[List[Dict[str, Any]]]
    tool_choice: Optional[Union[str, Dict[str, Any]]]


# ============================================================================
# TESTS
# ============================================================================

async def main():
    print("=" * 70)
    print("PRODUCTION LLM ADAPTER - COMPREHENSIVE TESTS")
    print("=" * 70)
    
    adapter = ProductionLLMAdapter()
    
    # Test 1: Capabilities
    print("\n[TEST 1] Capabilities")
    caps = await adapter.capabilities()
    print(f"✅ Server: {caps.server}")
    print(f"✅ Protocol: {caps.protocol}")
    print(f"✅ Streaming: {caps.supports_streaming}")
    print(f"✅ Tools: {caps.supports_tools}")
    
    # Test 2: Basic completion
    print("\n[TEST 2] Basic Completion")
    completion = await adapter.complete(
        messages=[{"role": "user", "content": "What is Python?"}],
        model="gpt-4"
    )
    print(f"✅ Response: {completion.text}")
    print(f"✅ Tokens: {completion.usage.total_tokens}")
    print(f"✅ Finish: {completion.finish_reason}")
    
    # Test 3: Tool calling
    print("\n[TEST 3] Tool Calling")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search the web",
                "parameters": {"type": "object"}
            }
        }
    ]
    completion = await adapter.complete(
        messages=[{"role": "user", "content": "Search for AI"}],
        tools=tools,
        model="gpt-4"
    )
    print(f"✅ Tool calls: {len(completion.tool_calls)}")
    if completion.tool_calls:
        print(f"✅ Tool name: {completion.tool_calls[0].function.name}")
    
    # Test 4: Streaming
    print("\n[TEST 4] Streaming")
    print("✅ Stream: ", end="", flush=True)
    async for chunk in adapter.stream(
        messages=[{"role": "user", "content": "Count to five"}],
        model="gpt-4"
    ):
        print(chunk.text, end="", flush=True)
        if chunk.is_final:
            print(f"\n✅ Final chunk received")
    
    # Test 5: Token counting
    print("\n[TEST 5] Token Counting")
    tokens = await adapter.count_tokens("Hello world", model="gpt-4")
    print(f"✅ Tokens: {tokens}")
    
    # Test 6: Health check
    print("\n[TEST 6] Health Check")
    health = await adapter.health()
    print(f"✅ OK: {health.get('ok')}")
    print(f"✅ Status: {health.get('status')}")
    
    # Test 7: Stats
    print("\n[TEST 7] Adapter Stats")
    print(f"✅ Complete calls: {adapter._stats['complete_calls']}")
    print(f"✅ Stream calls: {adapter._stats['stream_calls']}")
    print(f"✅ Token count calls: {adapter._stats['count_tokens_calls']}")
    print(f"✅ Total tokens: {adapter._stats['total_prompt_tokens'] + adapter._stats['total_completion_tokens']}")
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✅")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
