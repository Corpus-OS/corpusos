# SPDX-License-Identifier: Apache-2.0
"""
Unit tests for the MiniMax provider adapter.

These tests use a fake transport so no network access is required. They cover
the capabilities contract, regional endpoint selection, completion parsing,
streaming SSE parsing, token counting and error mapping.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Mapping
from typing import Dict, List, Optional

import pytest

from corpus_sdk.llm.llm_base import (
    AuthError,
    BadRequest,
    LLMCapabilities,
    LLMChunk,
    LLMCompletion,
    ResourceExhausted,
    TokenUsage,
)
from corpus_sdk.llm.providers.minimax import (
    MINIMAX_MODELS,
    MINIMAX_REGIONS,
    MiniMaxAdapter,
)

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Fake transport
# ---------------------------------------------------------------------------


class FakeTransport:
    """Records the last request and returns canned line streams."""

    def __init__(self, *, lines: Optional[List[bytes]] = None, error: Optional[Exception] = None):
        self._lines = lines or []
        self._error = error
        self.calls: List[Dict[str, object]] = []

    async def __call__(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
        body: Optional[bytes],
        stream: bool,
    ) -> AsyncIterator[bytes]:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers),
                "body": body,
                "stream": stream,
            }
        )
        if self._error is not None:
            raise self._error

        async def _gen() -> AsyncIterator[bytes]:
            for line in self._lines:
                yield line

        return _gen()


def _completion_body(
    *,
    text: str = "hello",
    model: str = "MiniMax-M3",
    finish: str = "stop",
    tool_calls: Optional[List[Dict]] = None,
) -> bytes:
    message: Dict[str, object] = {"role": "assistant", "content": text}
    if tool_calls:
        message["tool_calls"] = tool_calls
    payload = {
        "id": "cmpl-1",
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": finish,
            }
        ],
        "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
    }
    return (json.dumps(payload) + "\n").encode("utf-8")


def _sse_lines(events: List[Dict]) -> List[bytes]:
    out: List[bytes] = []
    for ev in events:
        out.append(b"data: " + json.dumps(ev).encode("utf-8") + b"\n")
        out.append(b"\n")
    out.append(b"data: [DONE]\n")
    return out


# ---------------------------------------------------------------------------
# Construction & capabilities
# ---------------------------------------------------------------------------


async def test_capabilities_advertise_models_and_contexts():
    transport = FakeTransport()
    adapter = MiniMaxAdapter(api_key="k", transport=transport)
    caps = await adapter.capabilities()
    assert isinstance(caps, LLMCapabilities)
    assert caps.server == "minimax"
    assert caps.model_family == "minimax"
    assert caps.supports_streaming is True
    assert caps.supports_tools is True
    assert "MiniMax-M3" in caps.supported_models
    assert "MiniMax-M2.7" in caps.supported_models
    assert caps.max_context_length == 1000000


async def test_registry_matches_capabilities():
    ids = [spec.model_id for spec in MINIMAX_MODELS]
    assert ids == ["MiniMax-M3", "MiniMax-M2.7"]
    m3 = MINIMAX_MODELS[0]
    assert m3.context_window == 1000000
    assert "image" in m3.input_modalities
    assert "video" in m3.input_modalities
    m27 = MINIMAX_MODELS[1]
    assert m27.context_window == 204800
    assert m27.input_modalities == ("text",)
    assert m27.thinking == ("always_on",)


async def test_unknown_region_rejected():
    with pytest.raises(BadRequest):
        MiniMaxAdapter(api_key="k", region="eu_fr")


async def test_unknown_default_model_rejected():
    with pytest.raises(BadRequest):
        MiniMaxAdapter(api_key="k", model="nope")


async def test_regional_endpoints_cover_global_and_cn():
    assert "global_en" in MINIMAX_REGIONS
    assert "cn_zh" in MINIMAX_REGIONS
    assert MINIMAX_REGIONS["global_en"]["openai_base_url"].startswith("https://api.minimax.io")
    assert MINIMAX_REGIONS["cn_zh"]["openai_base_url"].startswith("https://api.minimaxi.com")


async def test_region_selects_endpoint_url():
    transport = FakeTransport(lines=[_completion_body()])
    adapter = MiniMaxAdapter(api_key="k", region="cn_zh", transport=transport)
    await adapter.complete(messages=[{"role": "user", "content": "hi"}], model="MiniMax-M3")
    call = transport.calls[-1]
    assert "api.minimaxi.com" in str(call["url"])


# ---------------------------------------------------------------------------
# Completion
# ---------------------------------------------------------------------------


async def test_complete_parses_payload_and_usage():
    transport = FakeTransport(lines=[_completion_body(text="hello world")])
    adapter = MiniMaxAdapter(api_key="k", transport=transport)
    res = await adapter.complete(messages=[{"role": "user", "content": "hi"}], model="MiniMax-M3")
    assert isinstance(res, LLMCompletion)
    assert res.text == "hello world"
    assert res.model == "MiniMax-M3"
    assert res.model_family == "minimax"
    assert res.finish_reason == "stop"
    assert isinstance(res.usage, TokenUsage)
    assert res.usage.total_tokens == 8
    assert res.usage.prompt_tokens + res.usage.completion_tokens == res.usage.total_tokens


async def test_complete_forwards_auth_and_json_headers():
    transport = FakeTransport(lines=[_completion_body()])
    adapter = MiniMaxAdapter(api_key="secret-token", transport=transport)
    await adapter.complete(messages=[{"role": "user", "content": "hi"}])
    headers = transport.calls[-1]["headers"]
    assert headers["Authorization"] == "Bearer secret-token"
    assert headers["Content-Type"] == "application/json"


async def test_complete_includes_system_message_and_params():
    transport = FakeTransport(lines=[_completion_body()])
    adapter = MiniMaxAdapter(api_key="k", transport=transport)
    await adapter.complete(
        messages=[{"role": "user", "content": "hi"}],
        model="MiniMax-M3",
        system_message="be brief",
        temperature=0.2,
        top_p=0.9,
        max_tokens=42,
        stop_sequences=["\n"],
    )
    body = json.loads(transport.calls[-1]["body"])  # type: ignore[arg-type]
    assert body["messages"][0] == {"role": "system", "content": "be brief"}
    assert body["temperature"] == 0.2
    assert body["top_p"] == 0.9
    assert body["max_tokens"] == 42
    assert body["stop"] == ["\n"]


async def test_complete_parses_tool_calls():
    tool_calls = [
        {
            "id": "call_1",
            "type": "function",
            "function": {"name": "get_weather", "arguments": '{"city":"sf"}'},
        }
    ]
    transport = FakeTransport(
        lines=[_completion_body(text="", finish="tool_calls", tool_calls=tool_calls)]
    )
    adapter = MiniMaxAdapter(api_key="k", transport=transport)
    res = await adapter.complete(
        messages=[{"role": "user", "content": "weather?"}],
        tools=[{"type": "function", "function": {"name": "get_weather"}}],
    )
    assert res.finish_reason == "tool_calls"
    assert res.tool_calls and len(res.tool_calls) == 1
    call = res.tool_calls[0]
    assert call.id == "call_1"
    assert call.function.name == "get_weather"
    assert call.function.arguments == '{"city":"sf"}'


async def test_complete_uses_default_model_when_omitted():
    transport = FakeTransport(lines=[_completion_body(model="MiniMax-M3")])
    adapter = MiniMaxAdapter(api_key="k", model="MiniMax-M3", transport=transport)
    res = await adapter.complete(messages=[{"role": "user", "content": "hi"}])
    body = json.loads(transport.calls[-1]["body"])  # type: ignore[arg-type]
    assert body["model"] == "MiniMax-M3"
    assert res.model == "MiniMax-M3"


async def test_complete_rejects_unknown_model():
    adapter = MiniMaxAdapter(api_key="k", transport=FakeTransport(lines=[_completion_body()]))
    with pytest.raises(BadRequest):
        await adapter.complete(messages=[{"role": "user", "content": "hi"}], model="bogus")


async def test_complete_empty_choices_raises_unavailable():
    from corpus_sdk.llm.llm_base import Unavailable

    transport = FakeTransport(lines=[(json.dumps({"model": "MiniMax-M3"}) + "\n").encode()])
    adapter = MiniMaxAdapter(api_key="k", transport=transport)
    with pytest.raises(Unavailable):
        await adapter.complete(messages=[{"role": "user", "content": "hi"}])


# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------


async def test_stream_yields_deltas_and_final_chunk():
    events = [
        {"choices": [{"index": 0, "delta": {"content": "hel"}, "finish_reason": None}]},
        {"choices": [{"index": 0, "delta": {"content": "lo"}, "finish_reason": None}]},
        {
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 2, "completion_tokens": 2, "total_tokens": 4},
        },
    ]
    transport = FakeTransport(lines=_sse_lines(events))
    adapter = MiniMaxAdapter(api_key="k", transport=transport)
    chunks: List[LLMChunk] = []
    async for chunk in adapter.stream(
        messages=[{"role": "user", "content": "hi"}], model="MiniMax-M3"
    ):
        chunks.append(chunk)
    assert chunks
    assert "".join(c.text for c in chunks) == "hello"
    assert chunks[-1].is_final is True
    assert chunks[-1].usage_so_far is not None
    assert chunks[-1].usage_so_far.total_tokens == 4


async def test_stream_payload_requests_stream_true():
    transport = FakeTransport(lines=_sse_lines([]))
    adapter = MiniMaxAdapter(api_key="k", transport=transport)
    async for _ in adapter.stream(
        messages=[{"role": "user", "content": "hi"}], model="MiniMax-M2.7"
    ):
        pass
    body = json.loads(transport.calls[-1]["body"])  # type: ignore[arg-type]
    assert body["stream"] is True
    assert body["model"] == "MiniMax-M2.7"


async def test_stream_handles_missing_choices_gracefully():
    events = [{"usage": {"prompt_tokens": 1, "completion_tokens": 0, "total_tokens": 1}}]
    transport = FakeTransport(lines=_sse_lines(events))
    adapter = MiniMaxAdapter(api_key="k", transport=transport)
    chunks: List[LLMChunk] = []
    async for chunk in adapter.stream(messages=[{"role": "user", "content": "hi"}]):
        chunks.append(chunk)
    assert chunks[-1].is_final is True


# ---------------------------------------------------------------------------
# Token counting & health
# ---------------------------------------------------------------------------


async def test_count_tokens_positive_for_text():
    adapter = MiniMaxAdapter(api_key="k", transport=FakeTransport())
    assert await adapter.count_tokens(text="") == 0
    n = await adapter.count_tokens(text="one two three four")
    assert n > 0


async def test_health_reports_region_and_endpoint():
    adapter = MiniMaxAdapter(api_key="k", region="global_en", transport=FakeTransport())
    health = await adapter.health()
    assert health["ok"] is True
    assert health["server"] == "minimax"
    # The public health() wrapper normalizes to {ok, server, version};
    # region/endpoint are exposed on _do_health and the adapter directly.
    detailed = await adapter._do_health()
    assert detailed["region"] == "global_en"
    assert "api.minimax.io" in detailed["endpoint"]


# ---------------------------------------------------------------------------
# Error mapping
# ---------------------------------------------------------------------------


async def test_http_error_401_maps_to_auth_error():
    from corpus_sdk.llm.providers.minimax import _map_http_error

    err = _map_http_error(401, "unauthorized")
    assert isinstance(err, AuthError)


async def test_http_error_429_maps_to_resource_exhausted():
    from corpus_sdk.llm.providers.minimax import _map_http_error

    err = _map_http_error(429, "slow down")
    assert isinstance(err, ResourceExhausted)


async def test_http_error_500_maps_to_unavailable():
    from corpus_sdk.llm.llm_base import Unavailable
    from corpus_sdk.llm.providers.minimax import _map_http_error

    err = _map_http_error(500, "boom")
    assert isinstance(err, Unavailable)


async def test_adapter_satisfies_protocol_contract():
    from corpus_sdk.llm.llm_base import LLMProtocolV1

    adapter = MiniMaxAdapter(api_key="k", transport=FakeTransport())
    assert isinstance(adapter, LLMProtocolV1)
