# corpus_sdk/llm/providers/minimax.py
# SPDX-License-Identifier: Apache-2.0
"""
MiniMax provider adapter for LLMProtocolV1.

This module implements a concrete ``BaseLLMAdapter`` that talks to the
MiniMax text model HTTP API. MiniMax exposes an OpenAI-compatible
``/chat/completions`` surface at both the global endpoint
(``https://api.minimax.io/v1``) and the China endpoint
(``https://api.minimaxi.com/v1``), as well as an Anthropic-compatible
endpoint. This adapter uses the OpenAI-compatible surface so that streaming,
tool calling, and token accounting map cleanly onto ``LLMCompletion`` /
``LLMChunk``.

Design notes
------------
- **No third-party HTTP dependency**: the default transport uses the
  standard-library ``urllib`` stack wrapped with ``asyncio.to_thread`` so the
  package keeps zero runtime dependencies.
- **Pluggable transport**: callers (and tests) can inject a transport callable
  to short-circuit network I/O. This keeps the adapter deterministic and
  network-free under conformance tests.
- **Regional endpoints**: the adapter selects between the global
  (``global_en``) and China (``cn_zh``) MiniMax deployments; both base URLs are
  sourced from the MiniMax regional endpoint configuration.
- **Model registry**: context windows, input modalities, thinking modes and
  pricing are advertised from a small frozen registry so capabilities stay
  aligned with the upstream MiniMax model lineup.

The adapter raises the normalized error taxonomy from
:mod:`corpus_sdk.llm.llm_base` (``BadRequest``, ``AuthError``,
``ResourceExhausted``, ``TransientNetwork``, ``Unavailable``).
"""

from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.request
from collections.abc import AsyncIterator, Awaitable, Mapping
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

from corpus_sdk.llm.llm_base import (
    AuthError,
    BadRequest,
    BaseLLMAdapter,
    DeadlinePolicy,
    LLMCapabilities,
    LLMChunk,
    LLMCompletion,
    MetricsSink,
    OperationContext,
    ResourceExhausted,
    TokenUsage,
    ToolCall,
    ToolCallFunction,
    TransientNetwork,
    Unavailable,
)

# ---------------------------------------------------------------------------
# MiniMax model registry
#
# Values are sourced from the MiniMax model configuration: context windows,
# input modalities, thinking modes and per-million-token pricing.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MiniMaxModelSpec:
    """Static description of a MiniMax text model."""

    model_id: str
    context_window: int
    input_modalities: Tuple[str, ...]
    thinking: Tuple[str, ...]
    pricing_usd_per_million_tokens: Mapping[str, Optional[float]]


MINIMAX_MODELS: Tuple[MiniMaxModelSpec, ...] = (
    MiniMaxModelSpec(
        model_id="MiniMax-M3",
        context_window=1000000,
        input_modalities=("text", "image", "video"),
        thinking=("adaptive", "disabled"),
        pricing_usd_per_million_tokens={
            "input": 0.6,
            "output": 2.4,
            "cache_read": 0.12,
            "cache_write": None,
        },
    ),
    MiniMaxModelSpec(
        model_id="MiniMax-M2.7",
        context_window=204800,
        input_modalities=("text",),
        thinking=("always_on",),
        pricing_usd_per_million_tokens={
            "input": 0.3,
            "output": 1.2,
            "cache_read": 0.06,
            "cache_write": 0.375,
        },
    ),
)

# ---------------------------------------------------------------------------
# MiniMax regional endpoints
#
# The global deployment (api.minimax.io) and the China deployment
# (api.minimaxi.com) expose OpenAI- and Anthropic-compatible roots.
# ---------------------------------------------------------------------------

MINIMAX_REGIONS: Mapping[str, Mapping[str, str]] = {
    "global_en": {
        "openai_base_url": "https://api.minimax.io/v1",
        "anthropic_base_url": "https://api.minimax.io/anthropic",
        "docs_root": "https://platform.minimax.io/docs",
    },
    "cn_zh": {
        "openai_base_url": "https://api.minimaxi.com/v1",
        "anthropic_base_url": "https://api.minimaxi.com/anthropic",
        "docs_root": "https://platform.minimaxi.com/docs",
    },
}

DEFAULT_REGION = "global_en"
DEFAULT_MODEL = "MiniMax-M3"
SERVER = "minimax"
VERSION = "1.0.0"
MODEL_FAMILY = "minimax"

# Default context window advertised in capabilities when no model is selected.
_MAX_CONTEXT = max(spec.context_window for spec in MINIMAX_MODELS)


def _model_spec(model_id: str) -> Optional[MiniMaxModelSpec]:
    for spec in MINIMAX_MODELS:
        if spec.model_id == model_id:
            return spec
    return None


def _supported_model_ids() -> Tuple[str, ...]:
    return tuple(spec.model_id for spec in MINIMAX_MODELS)


# ---------------------------------------------------------------------------
# Transport abstraction
#
# A transport is an async callable that performs an HTTP request and returns an
# async iterator of raw line bytes. The same shape serves unary responses
# (the adapter buffers the whole body then JSON-parses) and streaming
# responses (the adapter parses Server-Sent-Events line by line).
# ---------------------------------------------------------------------------

TransportLines = AsyncIterator[bytes]
TransportCallable = Callable[
    [str, str, Mapping[str, str], Optional[bytes], bool],
    Awaitable[TransportLines],
]


async def _default_transport(
    method: str,
    url: str,
    headers: Mapping[str, str],
    body: Optional[bytes],
    stream: bool,
) -> TransportLines:
    """Stdlib ``urllib`` transport wrapped in a worker thread.

    Yields raw response body bytes line by line. HTTP errors are raised as
    :class:`TransientNetwork` / :class:`Unavailable` so the adapter can map
    them into the normalized taxonomy.
    """

    req = urllib.request.Request(url=url, data=body, method=method)
    for k, v in headers.items():
        req.add_header(k, v)

    try:
        response = await asyncio.to_thread(urllib.request.urlopen, req, None)
    except urllib.error.HTTPError as exc:  # pragma: no cover - network path
        raise _map_http_error(exc.code, exc.reason) from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network path
        raise TransientNetwork(f"MiniMax transport failure: {exc.reason}") from exc

    async def _lines() -> AsyncIterator[bytes]:
        try:
            while True:
                chunk = await asyncio.to_thread(response.readline)
                if not chunk:
                    break
                yield chunk
        finally:
            await asyncio.to_thread(response.close)

    return _lines()


def _map_http_error(code: int, reason: str) -> Exception:
    """Map an upstream HTTP status code onto the normalized error taxonomy."""
    if code == 400 or code == 422:
        return BadRequest(f"MiniMax rejected the request: {reason}")
    if code in (401, 403):
        return AuthError(f"MiniMax authentication failed: {reason}")
    if code == 429:
        return ResourceExhausted(f"MiniMax rate limit hit: {reason}")
    if 500 <= code < 600:
        return Unavailable(f"MiniMax upstream unavailable: {reason}")
    return BadRequest(f"MiniMax HTTP {code}: {reason}")


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


class MiniMaxAdapter(BaseLLMAdapter):
    """Concrete MiniMax adapter implementing :class:`LLMProtocolV1`.

    Parameters
    ----------
    api_key:
        Bearer token used for ``Authorization``. Falls back to the
        ``MINIMAX_API_KEY`` environment variable when omitted.
    region:
        One of the keys in :data:`MINIMAX_REGIONS` (``global_en`` or
        ``cn_zh``). Selects the deployment the adapter targets.
    model:
        Default model id used when callers omit ``model=``. Must be one of
        :data:`MINIMAX_MODELS`.
    transport:
        Optional async callable replacing the default stdlib HTTP transport.
        Useful for tests and offline environments.
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        region: str = DEFAULT_REGION,
        model: str = DEFAULT_MODEL,
        transport: Optional[TransportCallable] = None,
        metrics: Optional[MetricsSink] = None,
        mode: str = "thin",
        deadline_policy: Optional[DeadlinePolicy] = None,
        tag_model_in_metrics: bool = True,
        cache_ttl_s: int = 60,
        stream_deadline_check_every_n_chunks: int = 10,
    ) -> None:
        if region not in MINIMAX_REGIONS:
            raise BadRequest(f"unknown MiniMax region: {region!r}")
        if _model_spec(model) is None:
            raise BadRequest(f"unknown MiniMax model: {model!r}")

        super().__init__(
            metrics=metrics,
            mode=mode,
            deadline_policy=deadline_policy,
            tag_model_in_metrics=tag_model_in_metrics,
            cache_ttl_s=cache_ttl_s,
            stream_deadline_check_every_n_chunks=stream_deadline_check_every_n_chunks,
        )

        self._api_key = api_key or os.environ.get("MINIMAX_API_KEY")
        self._region = region
        self._default_model = model
        self._transport: TransportCallable = transport or _default_transport  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def region(self) -> str:
        return self._region

    def _openai_base_url(self) -> str:
        return MINIMAX_REGIONS[self._region]["openai_base_url"]

    def _resolve_model(self, model: Optional[str]) -> str:
        resolved = model or self._default_model
        spec = _model_spec(resolved)
        if spec is None:
            raise BadRequest(f"unknown MiniMax model: {resolved!r}")
        return resolved

    def _auth_headers(self) -> Dict[str, str]:
        token = self._api_key or ""
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _build_messages(
        messages: List[Mapping[str, Any]],
        system_message: Optional[str],
    ) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        if system_message:
            out.append({"role": "system", "content": system_message})
        out.extend({k: v for k, v in m.items()} for m in messages)
        return out

    @staticmethod
    def _parse_tool_calls(
        raw_calls: Optional[List[Mapping[str, Any]]],
    ) -> List[ToolCall]:
        calls: List[ToolCall] = []
        for raw in raw_calls or []:
            fn = raw.get("function") or {}
            calls.append(
                ToolCall(
                    id=str(raw.get("id") or ""),
                    type=str(raw.get("type") or "function"),
                    function=ToolCallFunction(
                        name=str(fn.get("name") or ""),
                        arguments=str(fn.get("arguments") or ""),
                    ),
                )
            )
        return calls

    def _build_payload(
        self,
        *,
        messages: List[Mapping[str, Any]],
        model: str,
        max_tokens: Optional[int],
        temperature: Optional[float],
        top_p: Optional[float],
        frequency_penalty: Optional[float],
        presence_penalty: Optional[float],
        stop_sequences: Optional[List[str]],
        system_message: Optional[str],
        tools: Optional[List[Dict[str, Any]]],
        tool_choice: Optional[Union[str, Dict[str, Any]]],
        stream: bool,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": self._build_messages(messages, system_message),
            "stream": stream,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop_sequences:
            payload["stop"] = stop_sequences
        if tools:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        return payload

    async def _request_lines(
        self,
        payload: Dict[str, Any],
        *,
        stream: bool,
    ) -> AsyncIterator[bytes]:
        body = json.dumps(payload).encode("utf-8")
        url = f"{self._openai_base_url()}/chat/completions"
        headers = self._auth_headers()
        return await self._transport("POST", url, headers, body, stream)

    # ------------------------------------------------------------------
    # Capabilities & health
    # ------------------------------------------------------------------

    async def _do_capabilities(self) -> LLMCapabilities:
        return LLMCapabilities(
            server=SERVER,
            version=VERSION,
            model_family=MODEL_FAMILY,
            max_context_length=_MAX_CONTEXT,
            supports_streaming=True,
            supports_roles=True,
            supports_json_output=True,
            supports_tools=True,
            supports_parallel_tool_calls=True,
            supports_tool_choice=True,
            max_tool_calls_per_turn=4,
            idempotent_writes=False,
            supports_multi_tenant=True,
            supports_system_message=True,
            supports_deadline=True,
            supports_count_tokens=True,
            supported_models=_supported_model_ids(),
        )

    async def _do_health(self, *, ctx: Optional[OperationContext] = None) -> Mapping[str, Any]:
        return {
            "ok": True,
            "status": "healthy",
            "server": SERVER,
            "version": VERSION,
            "region": self._region,
            "endpoint": self._openai_base_url(),
        }

    # ------------------------------------------------------------------
    # Completion
    # ------------------------------------------------------------------

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
        resolved = self._resolve_model(model)
        payload = self._build_payload(
            messages=messages,
            model=resolved,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop_sequences=stop_sequences,
            system_message=system_message,
            tools=tools,
            tool_choice=tool_choice,
            stream=False,
        )

        lines = await self._request_lines(payload, stream=False)
        body = await _read_all(lines)
        data = _parse_json_body(body)
        if not isinstance(data, Mapping):
            raise Unavailable("MiniMax returned a non-object completion response")

        return self._completion_from_payload(data, resolved)

    def _completion_from_payload(
        self,
        data: Mapping[str, Any],
        resolved_model: str,
    ) -> LLMCompletion:
        choices = data.get("choices") or []
        if not choices:
            raise Unavailable("MiniMax completion had no choices")
        choice = choices[0]
        message = choice.get("message") or {}
        text = str(message.get("content") or "")
        finish_reason = str(choice.get("finish_reason") or "stop")
        tool_calls = self._parse_tool_calls(message.get("tool_calls"))

        usage_raw = data.get("usage") or {}
        prompt = int(usage_raw.get("prompt_tokens") or 0)
        completion = int(usage_raw.get("completion_tokens") or 0)
        total = int(usage_raw.get("total_tokens") or (prompt + completion))

        return LLMCompletion(
            text=text,
            model=resolved_model,
            model_family=MODEL_FAMILY,
            usage=TokenUsage(
                prompt_tokens=prompt,
                completion_tokens=completion,
                total_tokens=total,
            ),
            finish_reason=finish_reason,
            tool_calls=tool_calls,
        )

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------

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
        resolved = self._resolve_model(model)
        payload = self._build_payload(
            messages=messages,
            model=resolved,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop_sequences=stop_sequences,
            system_message=system_message,
            tools=tools,
            tool_choice=tool_choice,
            stream=True,
        )

        lines = await self._request_lines(payload, stream=True)

        saw_final = False
        async for chunk in _iter_sse_objects(lines):
            choices = chunk.get("choices") or []
            delta = choices[0].get("delta") if choices else {}
            text = str(delta.get("content") or "")
            finish_reason = choices[0].get("finish_reason") if choices else None

            usage_raw = chunk.get("usage")
            usage: Optional[TokenUsage] = None
            if usage_raw:
                p = int(usage_raw.get("prompt_tokens") or 0)
                c = int(usage_raw.get("completion_tokens") or 0)
                usage = TokenUsage(
                    prompt_tokens=p,
                    completion_tokens=c,
                    total_tokens=int(usage_raw.get("total_tokens") or (p + c)),
                )

            is_final = bool(finish_reason) or usage is not None
            if is_final:
                saw_final = True
            yield LLMChunk(
                text=text,
                is_final=is_final,
                model=resolved,
                usage_so_far=usage,
                tool_calls=[],
            )

        # Guarantee a final sentinel chunk even if the upstream omitted one.
        if not saw_final:
            yield LLMChunk(text="", is_final=True, model=resolved, usage_so_far=None)

    # ------------------------------------------------------------------
    # Token counting
    # ------------------------------------------------------------------

    async def _do_count_tokens(
        self,
        text: str,
        *,
        model: Optional[str] = None,
        ctx: Optional[OperationContext] = None,
    ) -> int:
        """Best-effort token approximation.

        MiniMax does not expose a public token-counting endpoint, so the adapter
        approximates with a whitespace + punctuation heuristic. Callers that
        need exact counts should use the ``usage`` field on ``LLMCompletion``.
        """
        if not text:
            return 0
        return _approx_tokens(text)


# ---------------------------------------------------------------------------
# Body parsing helpers
# ---------------------------------------------------------------------------


async def _read_all(lines: AsyncIterator[bytes]) -> bytes:
    chunks: List[bytes] = []
    async for line in lines:
        chunks.append(line)
    return b"".join(chunks)


def _parse_json_body(body: bytes) -> Any:
    text = body.decode("utf-8", errors="replace").strip()
    if not text:
        raise Unavailable("MiniMax returned an empty completion body")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise BadRequest(f"MiniMax returned non-JSON body: {exc.msg}") from exc


async def _iter_sse_objects(lines: AsyncIterator[bytes]) -> AsyncIterator[Dict[str, Any]]:
    """Yield parsed JSON objects from a Server-Sent-Events byte stream."""
    pending = ""
    async for raw in lines:
        line = raw.decode("utf-8", errors="replace").rstrip("\n").rstrip("\r")
        if line == "":
            if pending:
                obj = _parse_sse_pending(pending)
                if obj is not None:
                    yield obj
                pending = ""
            continue
        if line.startswith("data:"):
            data_str = line[5:].strip()
            if data_str == "[DONE]":
                return
            pending = data_str
    if pending:
        obj = _parse_sse_pending(pending)
        if obj is not None:
            yield obj


def _parse_sse_pending(pending: str) -> Optional[Dict[str, Any]]:
    try:
        obj = json.loads(pending)
    except json.JSONDecodeError:
        return None
    if isinstance(obj, Mapping):
        return dict(obj)  # type: ignore[return-value]
    return None


def _approx_tokens(text: str) -> int:
    """Rough token estimate: ~1.3 tokens per whitespace-delimited token."""
    tokens = text.split()
    if not tokens:
        return 0
    # Heuristic: punctuation adds tokens; round up.
    return max(1, int(len(tokens) * 1.3))
