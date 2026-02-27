# LLM FRAMEWORK ADAPTERS SPECIFICATION

**specification_version:** `1.1.0`   
**protocol_version:** `1.0.0`

---

## Abstract

This specification defines the Corpus Framework Adapter Suite for LLM operations: a standardized set of production‑grade adapters that bridge the Corpus LLM Protocol V1.0 with five leading AI orchestration frameworks—AutoGen, CrewAI, LangChain, LlamaIndex, and Semantic Kernel. The suite provides consistent patterns for context propagation, error handling, observability, resource management, and streaming across frameworks while preserving each framework's native interfaces. This document includes normative contracts for adapter behavior, cross‑framework patterns, error taxonomy integration, observability requirements, and implementation guidelines for enterprise‑scale LLM operations.

> **Keywords:** Framework Adapters, AutoGen, CrewAI, LangChain, LlamaIndex, Semantic Kernel, LLM, Chat Completion, Streaming, Context Propagation, Error Normalization, Observability, Multi‑Framework, Protocol Bridge, Production Hardening

---

## Table of Contents

* [1. Introduction](#1-introduction)
  * [1.1. Motivation](#11-motivation)
  * [1.2. Scope](#12-scope)
  * [1.3. Design Philosophy](#13-design-philosophy)
* [2. Requirements Language](#2-requirements-language)
* [3. Terminology](#3-terminology)
* [4. Common Foundation Across All Adapters](#4-common-foundation-across-all-adapters)
  * [4.1. Protocol‑First Design (MUST)](#41-protocolfirst-design-must)
  * [4.2. Framework Resilience Strategy](#42-framework-resilience-strategy)
  * [4.3. Error Context Attachment (MUST)](#43-error-context-attachment-must)
  * [4.4. Dynamic Context Extraction Pattern](#44-dynamic-context-extraction-pattern)
  * [4.5. Message Normalization (MUST)](#45-message-normalization-must)
  * [4.6. Thread‑Safe Translator Initialization (MUST)](#46-threadsafe-translator-initialization-must)
  * [4.7. Resource Cleanup Patterns](#47-resource-cleanup-patterns)
  * [4.8. Event Loop Guards (MUST)](#48-event-loop-guards-must)
  * [4.9. Sampling Parameter Resolution (MUST)](#49-sampling-parameter-resolution-must)
  * [4.10. Streaming Semantics (MUST)](#410-streaming-semantics-must)
  * [4.11. Token Counting (MUST)](#411-token-counting-must)
  * [4.12. SIEM‑Safe Observability (MUST)](#412-siemsafe-observability-must)
  * [4.13. Testing Accommodations (INFORMATIVE)](#413-testing-accommodations-informative)
  * [4.14. Adapter Lifecycle Patterns](#414-adapter-lifecycle-patterns)
  * [4.15. Framework Context Building (MUST)](#415-framework-context-building-must)
* [5. Shared Utility Layer](#5-shared-utility-layer)
  * [5.1. Validation Utilities](#51-validation-utilities)
    * [5.1.1. Message Validation](#511-message-validation)
    * [5.1.2. Sampling Parameter Validation](#512-sampling-parameter-validation)
  * [5.2. Snapshot Utilities](#52-snapshot-utilities)
  * [5.3. Operation Context Detection](#53-operation-context-detection)
  * [5.4. Token Usage Coercion](#54-token-usage-coercion)
  * [5.5. Resource Cleanup Helpers](#55-resource-cleanup-helpers)
  * [5.6. Error Context Decorator Factory](#56-error-context-decorator-factory)
  * [5.7. Capabilities Normalization](#57-capabilities-normalization)
  * [5.8. Streaming Iterator Normalization](#58-streaming-iterator-normalization)
* [6. Cross‑Adapter Patterns](#6-crossadapter-patterns)
  * [6.1. Unified Error Taxonomy Integration](#61-unified-error-taxonomy-integration)
  * [6.2. Consistent Observability](#62-consistent-observability)
  * [6.3. Operation Context Propagation](#63-operation-context-propagation)
  * [6.4. Idempotency Semantics](#64-idempotency-semantics)
  * [6.5. Partial Failure Reporting](#65-partial-failure-reporting)
  * [6.6. Backpressure Integration](#66-backpressure-integration)
  * [6.7. LLM Determinism (MUST)](#67-llm-determinism-must)
  * [6.8. Translator Shim Equivalence (MUST)](#68-translator-shim-equivalence-must)
  * [6.9. Tool Passthrough Pattern](#69-tool-passthrough-pattern)
  * [6.10. System Message Handling](#610-system-message-handling)
* [7. AutoGen Adapter Specification](#7-autogen-adapter-specification)
  * [7.1. Overview](#71-overview)
  * [7.2. Framework‑Specific Challenges](#72-frameworkspecific-challenges)
  * [7.3. Data Types](#73-data-types)
  * [7.4. Core Class: `CorpusAutoGenChatClient`](#74-core-class-corpusautogenchatclient)
    * [7.4.1. OpenAI‑Style Compatibility Surface](#741-openai-style-compatibility-surface)
    * [7.4.2. Initialization](#742-initialization)
    * [7.4.3. Context Translation](#743-context-translation)
    * [7.4.4. Operations](#744-operations)
    * [7.4.5. Sync/Async Bridge](#745-syncasync-bridge)
  * [7.5. Integration Helpers](#75-integration-helpers)
    * [7.5.1. `create_autogen_chat_completion_client()`](#751-create_autogen_chat_completion_client)
    * [7.5.2. `_autogen_tools_to_openai()`](#752-_autogen_tools_to_openai)
  * [7.6. Error Codes](#76-error-codes)
  * [7.7. AutoGen‑Specific Context](#77-autogenspecific-context)
* [8. CrewAI Adapter Specification](#8-crewai-adapter-specification)
  * [8.1. Overview](#81-overview)
  * [8.2. Framework‑Specific Challenges](#82-frameworkspecific-challenges)
  * [8.3. Data Types](#83-data-types)
  * [8.4. Core Class: `CorpusCrewAILLM`](#84-core-class-corpuscrewailm)
    * [8.4.1. Initialization](#841-initialization)
    * [8.4.2. Context Translation](#842-context-translation)
    * [8.4.3. Operations](#843-operations)
    * [8.4.4. Streaming Iterator Wrapping](#844-streaming-iterator-wrapping)
  * [8.5. Integration Helpers](#85-integration-helpers)
    * [8.5.1. `_ensure_crewai_installed()`](#851-_ensure_crewai_installed)
  * [8.6. Error Codes](#86-error-codes)
  * [8.7. CrewAI‑Specific Context](#87-crewaispecific-context)
* [9. LangChain Adapter Specification](#9-langchain-adapter-specification)
  * [9.1. Overview](#91-overview)
  * [9.2. Framework‑Specific Challenges](#92-frameworkspecific-challenges)
  * [9.3. Data Types](#93-data-types)
  * [9.4. Core Class: `CorpusLangChainLLM`](#94-core-class-corpuslangchainllm)
    * [9.4.1. Pydantic Integration](#941-pydantic-integration)
    * [9.4.2. Initialization](#942-initialization)
    * [9.4.3. Callback Manager Integration](#943-callback-manager-integration)
    * [9.4.4. Operations](#944-operations)
    * [9.4.5. Event Loop Safety](#945-event-loop-safety)
  * [9.5. Integration Helpers](#95-integration-helpers)
    * [9.5.1. Message Normalization](#951-message-normalization)
    * [9.5.2. Result Shaping](#952-result-shaping)
  * [9.6. Error Codes](#96-error-codes)
  * [9.7. LangChain‑Specific Context](#97-langchainspecific-context)
* [10. LlamaIndex Adapter Specification](#10-llamaindex-adapter-specification)
  * [10.1. Overview](#101-overview)
  * [10.2. Framework‑Specific Challenges](#102-frameworkspecific-challenges)
  * [10.3. Data Types](#103-data-types)
  * [10.4. Core Class: `CorpusLlamaIndexLLM`](#104-core-class-corpusllamaindexllm)
    * [10.4.1. Pydantic Initialization Order (CRITICAL)](#1041-pydantic-initialization-order-critical)
    * [10.4.2. Initialization](#1042-initialization)
    * [10.4.3. Metadata Construction](#1043-metadata-construction)
    * [10.4.4. Operations](#1044-operations)
    * [10.4.5. Callback Manager Context Translation](#1045-callback-manager-context-translation)
  * [10.5. Integration Helpers](#105-integration-helpers)
    * [10.5.1. Message Block Handling](#1051-message-block-handling)
    * [10.5.2. Response Building](#1052-response-building)
  * [10.6. Error Codes](#106-error-codes)
  * [10.7. LlamaIndex‑Specific Context](#107-llamaindexspecific-context)
* [11. Semantic Kernel Adapter Specification](#11-semantic-kernel-adapter-specification)
  * [11.1. Overview](#111-overview)
  * [11.2. Framework‑Specific Challenges](#112-frameworkspecific-challenges)
  * [11.3. Data Types](#113-data-types)
  * [11.4. Core Class: `CorpusSemanticKernelChatCompletion`](#114-core-class-corpus-semantic-kernel-chat-completion)
    * [11.4.1. Initialization](#1141-initialization)
    * [11.4.2. Settings Context Translation](#1142-settings-context-translation)
    * [11.4.3. Operations](#1143-operations)
    * [11.4.4. Sync Alias Bridging](#1144-sync-alias-bridging)
  * [11.5. Integration Helpers](#115-integration-helpers)
    * [11.5.1. Chat History Conversion](#1151-chat-history-conversion)
  * [11.6. Error Codes](#116-error-codes)
  * [11.7. Semantic Kernel‑Specific Context](#117-semantic-kernelspecific-context)
* [12. Error Handling and Resilience](#12-error-handling-and-resilience)
  * [12.1. Error Code Mapping Table (Normative)](#121-error-code-mapping-table-normative)
  * [12.2. Retry Semantics](#122-retry-semantics)
  * [12.3. Circuit Breaking Guidance](#123-circuit-breaking-guidance)
* [13. Observability and Monitoring](#13-observability-and-monitoring)
  * [13.1. Metrics Taxonomy (MUST)](#131-metrics-taxonomy-must)
  * [13.2. Structured Logging (MUST)](#132-structured-logging-must)
  * [13.3. Distributed Tracing (SHOULD)](#133-distributed-tracing-should)
* [14. Security Considerations](#14-security-considerations)
  * [14.1. Tenant Isolation (MUST)](#141-tenant-isolation-must)
  * [14.2. Credential Handling (MUST)](#142-credential-handling-must)
  * [14.3. Log Redaction (MUST)](#143-log-redaction-must)
* [15. Performance Characteristics](#15-performance-characteristics)
  * [15.1. Latency Targets (Indicative)](#151-latency-targets-indicative)
  * [15.2. Concurrency Considerations](#152-concurrency-considerations)
  * [15.3. Caching Strategies](#153-caching-strategies)
* [16. Implementation Guidelines](#16-implementation-guidelines)
  * [16.1. Adapter Implementation Order](#161-adapter-implementation-order)
  * [16.2. Validation Requirements (MUST)](#162-validation-requirements-must)
  * [16.3. Testing](#163-testing)
    * [16.3.1. Conformance Test Suite](#1631-conformance-test-suite)
    * [16.3.2. Framework‑Specific Tests](#1632-frameworkspecific-tests)
    * [16.3.3. Cross‑Adapter Tests](#1633-crossadapter-tests)
* [17. Versioning and Compatibility](#17-versioning-and-compatibility)
  * [17.1. Semantic Versioning (MUST)](#171-semantic-versioning-must)
  * [17.2. Framework Version Compatibility](#172-framework-version-compatibility)
  * [17.3. Deprecation Policy](#173-deprecation-policy)
* [18. References](#18-references)
  * [18.1. Normative References](#181-normative-references)
  * [18.2. Informative References](#182-informative-references)
* [Appendix A — Comparison Matrix: Framework‑Specific Challenges](#appendix-a--comparison-matrix-framework-specific-challenges)
* [Appendix B — Code Pattern Catalog (Normative)](#appendix-b--code-pattern-catalog-normative)
  * [B.1. Context Building Patterns](#b1-context-building-patterns)
  * [B.2. Error Context Decorator Patterns](#b2-error-context-decorator-patterns)
  * [B.3. Event Loop Safety Patterns](#b3-event-loop-safety-patterns)
  * [B.4. Streaming Iterator Patterns](#b4-streaming-iterator-patterns)
  * [B.5. Resource Cleanup Patterns](#b5-resource-cleanup-patterns)
  * [B.6. Pydantic Initialization Patterns](#b6-pydantic-initialization-patterns)
  * [B.7. Token Counting Patterns](#b7-token-counting-patterns)
* [Appendix C — End‑to‑End Usage Examples](#appendix-c--end-to-end-usage-examples)
  * [C.1. AutoGen Agent with Chat Client](#c1-autogen-agent-with-chat-client)
  * [C.2. CrewAI Agent with LLM](#c2-crewai-agent-with-llm)
  * [C.3. LangChain Chain with Chat Model](#c3-langchain-chain-with-chat-model)
  * [C.4. LlamaIndex Query Engine with LLM](#c4-llamaindex-query-engine-with-llm)
  * [C.5. Semantic Kernel Plugin Registration](#c5-semantic-kernel-plugin-registration)
* [Appendix D — Error Code Reference](#appendix-d--error-code-reference)
* [Appendix E — Implementation Status (Non‑Normative)](#appendix-e--implementation-status-non-normative)
* [Appendix F — Migration from Existing Framework Adapters (Informative)](#appendix-f--migration-from-existing-framework-adapters-informative)

---

## 1. Introduction

### 1.1. Motivation

The AI framework landscape has fragmented into five dominant orchestration layers—AutoGen for multi‑agent systems, CrewAI for role‑based agent teams, LangChain for chain‑of‑thought pipelines, LlamaIndex for RAG and indexing, and Semantic Kernel for enterprise AI integration. Each framework defines its own LLM interface with subtly different expectations:

- **AutoGen** requires OpenAI‑style chat clients with `create`/`acreate` methods and struggles with sync/async boundaries in agent loops.
- **CrewAI** expects LLMs attached to agents but provides no shared runtime context across agent executions.
- **LangChain** defines `BaseChatModel` with callback integration and complex streaming requirements.
- **LlamaIndex** implements `LLM` with metadata requirements (context window, num_output) for RAG components.
- **Semantic Kernel** uses `ChatCompletionClientBase` with `PromptExecutionSettings` and multiple streaming variants.

Building and maintaining separate adapters for each framework duplicates effort, fragments observability, and creates inconsistent error handling across an organization's AI stack. Framework‑specific edge cases—like AutoGen’s sync `__call__` from async contexts, or LlamaIndex’s Pydantic initialization order—cause production outages that are difficult to debug without deep framework expertise.

The Corpus Framework Adapter Suite for LLM solves this by providing a single, battle‑tested implementation of each framework's LLM interface, backed by the Corpus LLM Protocol. Each adapter encapsulates the framework‑specific hardening required for production deployments while sharing a common foundation for error handling, observability, and resource management. Organizations can standardize on Corpus LLM operations once and use them across any supported framework without rebuilding adapter logic.

### 1.2. Scope

This specification defines five framework adapters for LLM operations:

1. **AutoGen Adapter** — Implements OpenAI‑style chat client with `create`/`acreate` methods, context extraction from conversation objects, and optional `create_autogen_chat_completion_client()` wrapper for AutoGen Core integration with usage tracking.

2. **CrewAI Adapter** — Implements CrewAI‑compatible LLM with `complete`/`acomplete` and `stream`/`astream` methods, context extraction from task objects, and proper streaming iterator wrapping.

3. **LangChain Adapter** — Implements `BaseChatModel` with full callback manager integration (`on_llm_start`, `on_llm_new_token`, `on_llm_end`, `on_llm_error`), Pydantic v2 compatibility, and event‑loop safety.

4. **LlamaIndex Adapter** — Implements `LLM` with correct Pydantic initialization order, metadata construction (context window, num_output), and support for both legacy (`.content`) and modern (`.blocks`) message formats.

5. **Semantic Kernel Adapter** — Implements `ChatCompletionClientBase` with `PromptExecutionSettings` context translation, sync alias bridging, and proper streaming chunk handling.

All adapters share:

- **Context propagation** — Framework‑specific context (conversation, task, config, callback_manager, settings) flows into `OperationContext` and framework_ctx.
- **Error normalization** — All exceptions are enriched with `attach_context()` using framework‑specific error codes and lazy dynamic context extraction.
- **Observability** — Dynamic context extraction captures message counts, role distributions, content length, sampling parameters, and routing fields.
- **Streaming support** — Both sync and async streaming with proper iterator cleanup and error wrapping.
- **Resource management** — Framework-appropriate cleanup patterns, with support for both context managers and explicit close methods.
- **Token counting** — Centralized via `LLMTranslator.count_tokens_for_messages()` with consistent return type handling.
- **Sampling parameter resolution** — Consistent precedence: explicit kwargs → settings (when present) → instance defaults.
- **Thread safety** — All adapters are safe for concurrent use, whether using eager or lazy initialization.

### 1.3. Design Philosophy

- **Protocol‑First (MUST).** Adapters require only duck‑typed LLM adapters implementing `LLMProtocolV1`, not strict inheritance. This allows minimal test doubles and lightweight integrations.

- **Framework Resilience (MUST).** Adapters defend against framework evolution by filtering context, normalizing inputs, and never assuming internal APIs remain stable. Static compatibility methods satisfy framework probes without leaking implementation details.

- **Observability‑First (MUST).** Every LLM operation attaches rich error context: framework identity, model info, message counts, role distributions, content length, and sampling parameters. Exceptions crossing framework boundaries carry enough context to debug without log scraping.

- **Fail‑Safe Context Translation (MUST).** Context translation from framework‑specific structures to `OperationContext` must never break LLM operations. If translation fails, adapters attach diagnostic snapshots and raise appropriately.

- **Translator‑Centric (MUST).** All LLM operations (completion, streaming, token counting, health, capabilities) MUST go through the shared `LLMTranslator`. Direct adapter calls are forbidden to ensure consistent behavior across frameworks.

- **Async‑Safe Sync Usage (MUST).** Sync APIs enforce guard rails preventing calls from inside active event loops. When bridging is required, adapters use controlled worker‑thread execution.

- **Streaming Robustness (MUST).** Streaming methods must properly wrap iterators to attach error context during iteration, and must clean up resources in `finally` blocks.

- **Deterministic Results (MUST).** All adapters MUST produce identical completions for the same inputs, within floating‑point tolerance, regardless of which framework is used.

- **Production Hardening (MUST).** Thread‑safe initialization, resource cleanup hierarchies, SIEM‑safe logging, and consistent parameter resolution are non‑negotiable requirements.

---

## 2. Requirements Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [RFC2119] [RFC8174] when, and only when, they appear in all capitals.

**Example:**  
- "The adapter MUST reject empty message sequences" indicates a strict requirement that must be implemented and verified.  
- "The adapter SHOULD log warnings for unusually long messages" indicates a recommendation that may be deviated from only with good reason.

**Justified Deviation Example:**  
A developer might choose to disable message validation in a controlled environment where they have verified all inputs are valid, and where the performance cost of validation is significant. This deviation MUST be documented in the code, explaining why it is safe and what assumptions are being made. The adapter MUST still provide a way to re‑enable strict validation via configuration.

---

## 3. Terminology

**Adapter** — Concrete implementation of a framework‑specific LLM interface backed by a Corpus LLM Protocol V1 implementation.

**LLM Adapter** — The underlying LLM implementation that provides the `LLMProtocolV1` interface (`complete`, `stream`, `count_tokens`, `health`, `capabilities`).

**Operation Context** — Core context object containing `request_id`, `idempotency_key`, `deadline_ms`, `traceparent`, `tenant`, and `attrs`.

**Framework Context** — Framework‑specific context dictionary passed to the translator alongside core context (e.g., agent role, task ID, callback manager).

**Translator** — `LLMTranslator` instance that orchestrates LLM operations, handling message normalization, batching, retries, and streaming.

**Framework Translator** — `LLMFrameworkTranslator` implementation that handles framework‑specific translation of messages and results.

**Message Normalization** — Conversion of framework‑specific message objects into a format the translator expects (typically generic dicts with `role` and `content` fields, but may vary by framework).

**Sampling Parameters** — Generation parameters: model, temperature, max_tokens, top_p, frequency_penalty, presence_penalty, stop_sequences.

**Event Loop Guard** — Runtime check preventing sync methods from being called inside an active asyncio event loop.

**SIEM‑Safe** — Observability that excludes PII, raw content, and tenant identifiers, using hashes and structural metadata instead.

---

## 4. Common Foundation Across All Adapters

### 4.1. Protocol‑First Design (MUST)

All adapters MUST accept an `llm_adapter` parameter that implements `LLMProtocolV1`. Strict `isinstance` checks are NOT REQUIRED; behavioral duck typing suffices.

```python
# Valid llm_adapter implementations:
class MinimalLLMAdapter:
    def complete(self, raw_messages, **kwargs): ...
    def stream(self, raw_messages, **kwargs): ...
    def count_tokens(self, raw_messages, **kwargs): ...
    def health(self): ...
    def capabilities(self): ...

class FullLLMAdapter:
    async def acomplete(self, raw_messages, op_ctx=None, framework_ctx=None): ...
    async def astream(self, raw_messages, op_ctx=None, framework_ctx=None): ...
    def count_tokens_for_messages(self, raw_messages, model, op_ctx=None, framework_ctx=None): ...
    async def ahealth(self): ...
    async def acapabilities(self): ...
```

Adapters MUST validate at initialization that the provided adapter has the required methods:

```python
required = ["complete", "stream", "count_tokens", "health", "capabilities"]
missing = [m for m in required if not callable(getattr(llm_adapter, m, None))]
if missing:
    raise TypeError(f"llm_adapter must implement LLMProtocolV1; missing: {missing}")
```

### 4.2. Framework Resilience Strategy

All adapters implement three defensive layers:

1. **Context Filtering** — Extract only known, stable fields from framework‑specific context objects. Unknown keys are ignored (see §4.4). Unknown fields are snapshotted for observability but not relied upon for correctness.

2. **Normalized Error Attachment** — All exceptions are enriched with `attach_context()` using framework‑specific error codes and dynamic context (message counts, role distributions, sampling parameters).

3. **Forward‑Compatible Method Signatures** — Methods accept `**kwargs` and gracefully handle unsupported parameters by ignoring them, ensuring compatibility as frameworks evolve.

### 4.3. Error Context Attachment (MUST)

Every adapter MUST decorate its core LLM methods with error‑context decorators that capture:

- Operation name (`complete`, `stream`, `acomplete`, `astream`, `chat`, `get_chat_message_content`)
- Framework identity
- Model identifier
- Message count and role distribution (when metrics enabled)
- Total content length (when metrics enabled)
- Sampling parameters (temperature, max_tokens, etc.)
- Streaming flag
- Request identifiers (request_id, tenant)

*Note:* Framework version MAY be attached but is not required if present elsewhere (e.g., in `OperationContext` or `framework_ctx`).

```python
@with_llm_error_context("complete")
def complete(self, messages, **kwargs): ...

@with_async_llm_error_context("astream")
async def astream(self, messages, **kwargs): ...
```

### 4.4. Dynamic Context Extraction Pattern

All adapters implement dynamic context extraction that computes metrics *only on errors*:

```python
def _extract_dynamic_context(self, args, kwargs, operation):
    ctx = {
        "framework": self._framework_name,
        "model": getattr(self, "model", "unknown"),
        "operation": operation,
    }
    
    # Message metrics (if enabled)
    if getattr(self, "_enable_metrics_flag", True) and args:
        messages = self._extract_messages_from_args(args[0])
        if messages:
            ctx["messages_count"] = len(messages)
            roles, chars = self._analyze_message_metrics(messages)
            ctx["roles_distribution"] = roles
            ctx["total_content_chars"] = chars
    
    # Sampling parameters
    for param in ("temperature", "max_tokens", "top_p", "stream"):
        if param in kwargs:
            ctx[param] = kwargs[param]
    
    # Framework-specific fields (examples)
    if hasattr(self, "_extract_framework_context"):
        ctx.update(self._extract_framework_context(args, kwargs))
    
    return ctx
```

### 4.5. Message Normalization (MUST)

All adapters MUST convert framework‑specific message inputs into a format that the translator expects. The RECOMMENDED target format is a list of generic dicts with `role` and `content` fields, but variations are permitted and MUST be documented.

**Examples of compliant approaches:**

```python
# Approach 1: Generic dicts (RECOMMENDED)
def _to_translator_messages(self, messages):
    result = []
    for msg in messages:
        if isinstance(msg, Mapping):
            result.append(dict(msg))
        elif hasattr(msg, "role") and hasattr(msg, "content"):
            result.append({
                "role": str(getattr(msg, "role", "user")),
                "content": str(getattr(msg, "content", ""))
            })
        elif isinstance(msg, str):
            result.append({"role": "user", "content": msg})
    return result

# Approach 2: Framework-native types (LangChain)
def _normalize_messages(self, messages):
    # Returns List[BaseMessage]
    normalized = []
    for msg in messages:
        if isinstance(msg, BaseMessage):
            normalized.append(msg)
        elif isinstance(msg, Mapping):
            role = msg.get("role", "user")
            if role in {"assistant", "ai"}:
                normalized.append(AIMessage(content=msg.get("content", "")))
            else:
                normalized.append(HumanMessage(content=msg.get("content", "")))
    return normalized

# Approach 3: Passthrough (AutoGen - assumes OpenAI dicts)
def _validate_messages(self, messages):
    # Only validates, no transformation needed
    for msg in messages:
        if not isinstance(msg, Mapping) or "role" not in msg or "content" not in msg:
            raise TypeError(...)
```

### 4.6. Thread‑Safe Translator Initialization (MUST)

Translators MUST be initialized in a way that is thread‑safe for concurrent use. Two patterns are acceptable:

**Pattern A: Lazy Initialization with Lock (RECOMMENDED)**
```python
@cached_property
def _translator(self) -> LLMTranslator:
    """Lazily construct and cache LLMTranslator with thread safety."""
    with self._lock:
        if self._translator_cache is None:
            self._translator_cache = create_llm_translator(...)
        return self._translator_cache
```

**Pattern B: Eager Initialization in `__init__` (Compliant)**
```python
def __init__(self, ..., translator=None):
    # translator is built eagerly
    self._translator = translator or create_llm_translator(...)
    # Object is fully constructed before being shared
```

With eager initialization, the translator MUST be immutable after construction, and the adapter object MUST NOT be published until `__init__` completes successfully.

### 4.7. Resource Cleanup Patterns

Adapters MUST ensure that underlying adapter resources are cleaned up appropriately. Two patterns are recognized as compliant:

**Pattern 1: Full Lifecycle Pattern (RECOMMENDED for stateful adapters)**
- Implements explicit `close()`/`aclose()` methods
- Maintains lifecycle state (`UNINITIALIZED` → `INITIALIZED` → `CLOSED`)
- Uses locks for idempotent cleanup
- Raises `RuntimeError` for operations after close

```python
def close(self) -> None:
    with self._close_lock:
        if self._closed:
            return
        self._closed = True
        _maybe_close_sync(self._translator_cache)
        _maybe_close_sync(self._llm_adapter)
```

**Pattern 2: Context-Manager-Only Pattern (Compliant for thin adapters)**
- Implements `__enter__`/`__exit__` and/or `__aenter__`/`__aexit__`
- No explicit `close`/`aclose` methods
- No lifecycle state machine
- Best-effort cleanup on context exit
- No guarantee that operations after exit will fail

```python
def __exit__(self, exc_type, exc, tb):
    _maybe_close_sync(self._llm_adapter)  # translator not closed

async def __aexit__(self, exc_type, exc, tb):
    await _maybe_close_async(self._llm_adapter)
```

**Framework-Specific Implementations:**
- **Semantic Kernel**: Implements Pattern 1 (full lifecycle)
- **AutoGen, CrewAI, LangChain, LlamaIndex**: Implement Pattern 2 (context-manager-only)

### 4.8. Event Loop Guards (MUST)

Sync methods that invoke blocking LLM work (completions, streams) MUST prevent execution inside running event loops. Non-latency-critical methods (`health`, `capabilities`, `count_tokens`) SHOULD also be guarded but this is not mandatory.

```python
def _ensure_not_in_event_loop(sync_api_name: str, async_api_name: Optional[str] = None) -> None:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return
    
    hint = f" Use {async_api_name} instead." if async_api_name else ""
    raise RuntimeError(
        f"{sync_api_name} called from active event loop.{hint} "
        f"[SYNC_WRAPPER_CALLED_IN_EVENT_LOOP]"
    )
```

The symbolic error code MAY be embedded in the exception message rather than being a separate attribute.

### 4.9. Sampling Parameter Resolution (MUST)

All adapters MUST implement consistent precedence for sampling parameters:

1. **Explicit kwargs** — If provided directly to the method call, highest precedence
2. **Settings object** — Framework‑specific settings (`PromptExecutionSettings`, etc.) if the framework provides one
3. **Instance defaults** — Values set during initialization (model, temperature, max_tokens)

For frameworks without a settings object (AutoGen, CrewAI), only levels 1 and 3 apply.

```python
def _build_sampling_params(self, settings, kwargs):
    # Model resolution
    model = (
        kwargs.get("model") or
        (getattr(settings, "model_id", None) if settings else None) or
        getattr(settings, "model", None) or
        self.model
    )
    
    # Temperature resolution
    temperature = (
        kwargs.get("temperature") or
        (getattr(settings, "temperature", None) if settings else None) or
        self.temperature
    )
    
    return {
        "model": model,
        "temperature": temperature,
        # ... other parameters
    }
```

**Validation requirements:**
- Instance defaults MUST be validated at construction time (e.g., `0 ≤ temperature ≤ 2`)
- Per-call overrides MAY be passed through without revalidation; adapters SHOULD log warnings for obviously out-of-range values

### 4.10. Streaming Semantics (MUST)

All async streaming methods MUST:
- Return an `AsyncIterator` directly (not an awaitable that resolves to one)
- Wrap iteration to attach error context on exceptions
- Clean up resources in `finally` blocks (call `.aclose()` when available)
- Handle both mapping chunks and object chunks uniformly

```python
async def astream(self, messages, **kwargs):
    agen = self._translator.arun_stream(...)
    try:
        async for chunk in agen:
            yield self._normalize_chunk(chunk)
    except Exception as exc:
        attach_context(exc, ...)
        raise
    finally:
        if hasattr(agen, "aclose"):
            await agen.aclose()
```

### 4.11. Token Counting (MUST)

All adapters MUST implement token counting via `LLMTranslator.count_tokens_for_messages()`. The return type handling MAY vary by adapter:

```python
def count_tokens(self, messages, **kwargs) -> int:
    """Count tokens for messages."""
    if not messages:
        return 0
    
    normalized = self._to_translator_messages(messages)
    ctx, params, framework_ctx = self._build_request_context(
        kwargs, operation="count_tokens", stream=False
    )
    
    result = self._translator.count_tokens_for_messages(
        raw_messages=normalized,
        model=params.get("model", self.model),
        op_ctx=ctx,
        framework_ctx=framework_ctx,
    )
    
    # Pattern A: Accept only int (AutoGen, LlamaIndex)
    if isinstance(result, int):
        return result
    raise TypeError(f"Unexpected token count result: {type(result)}")
    
    # Pattern B: Accept int or Mapping (CrewAI, LangChain, Semantic Kernel)
    if isinstance(result, int):
        return result
    if isinstance(result, Mapping):
        for key in ("tokens", "total_tokens", "count"):
            if key in result and isinstance(result[key], int):
                return result[key]
    raise TypeError(f"Unexpected token count result: {type(result)}")
```

**Important:** Character-based heuristic fallbacks are NOT required in v1.0. If provided, they MUST be clearly documented as fallback behavior.

### 4.12. SIEM‑Safe Observability (MUST)

All logging MUST:

- Never log raw message content, prompts, or tenant identifiers
- Use truncation for long strings and containers
- Include `tenant_hash` instead of raw tenant
- Log operation completion with dimensions and latency

```python
logger.debug(
    "Chat completion completed: model=%s messages=%d tokens=%d latency_ms=%.2f",
    model, msg_count, token_count, elapsed_ms
)
```

**Important:** Raw tenant identifiers MAY be included in structured error context passed to `attach_context()`, as the logging layer is responsible for redaction.

### 4.13. Testing Accommodations (INFORMATIVE)

Adapters SHOULD support test injection:
- Translator can be injected via `translator` parameter
- Context building can be overridden in test subclasses
- Error codes are exposed for assertion
- Internal state (`_closed`, `_translator_cache`) is observable where applicable

### 4.14. Adapter Lifecycle Patterns

Adapters MAY implement a formal lifecycle state machine, but this is not required. When implemented, the following states are RECOMMENDED:

- **`UNINITIALIZED`** (initial state after `__init__`, before any lazy initialization)
- **`INITIALIZED`** (after first use, lazy resources created)
- **`CLOSED`** (after `close()` or `aclose()` is called)

**Valid Transitions:**
- `UNINITIALIZED` → `INITIALIZED`: automatically when any operation is first invoked
- `UNINITIALIZED` → `CLOSED`: via `close()` or `aclose()`
- `INITIALIZED` → `CLOSED`: via `close()` or `aclose()`
- `CLOSED` → (no transitions allowed; instance is dead)

**Illegal States:**
- Attempting any operation after `CLOSED` MUST raise `RuntimeError`
- Calling `close()` or `aclose()` multiple times is allowed and MUST be idempotent

**Partial Initialization Failure:**  
If an exception occurs during `__init__` after some resources have been allocated (e.g., a lock created but validation fails), the adapter MUST clean up any successfully allocated resources before propagating the exception.

### 4.15. Framework Context Building (MUST)

All adapters MUST build a `framework_ctx` dict containing framework‑specific metadata:

```python
def _build_framework_ctx(self, *, operation: str, stream: bool, **kwargs) -> Dict[str, Any]:
    """Build framework context for translator."""
    ctx = {
        "framework": self._framework_name,
        "framework_version": self._framework_version,
        "operation": operation,
        "stream": stream,
    }
    
    # Add framework‑specific fields
    if hasattr(self, "_extract_framework_context"):
        ctx.update(self._extract_framework_context(kwargs))
    
    return ctx
```

Tools and system messages MAY be passed either via `framework_ctx` or as top-level parameters to the translator (see §6.9).

---

## 5. Shared Utility Layer

### 5.1. Validation Utilities

#### 5.1.1. Message Validation

```python
def validate_messages(messages: Sequence[Any], *, op_name: str) -> None:
    """Validate that messages is a non‑empty sequence of valid message objects."""
    if not messages:
        raise ValueError(f"{op_name} messages cannot be empty")
    
    for i, msg in enumerate(messages):
        if isinstance(msg, Mapping):
            if "role" not in msg and "author_role" not in msg:
                raise ValueError(f"{op_name}[{i}] missing role field")
            if "content" not in msg and "items" not in msg:
                raise ValueError(f"{op_name}[{i}] missing content")
        elif hasattr(msg, "role") or hasattr(msg, "author_role"):
            if not (hasattr(msg, "content") or hasattr(msg, "items")):
                raise ValueError(f"{op_name}[{i}] missing content")
        else:
            raise TypeError(f"{op_name}[{i}] unsupported message type: {type(msg)}")
```

#### 5.1.2. Sampling Parameter Validation

```python
def validate_temperature(value: float) -> None:
    """Validate temperature is within [0.0, 2.0]."""
    if not isinstance(value, (int, float)) or not (0.0 <= float(value) <= 2.0):
        raise ValueError(f"temperature must be between 0.0 and 2.0, got {value}")

def validate_max_tokens(value: Optional[int]) -> None:
    """Validate max_tokens is positive if provided."""
    if value is not None and (not isinstance(value, int) or value < 1):
        raise ValueError(f"max_tokens must be positive, got {value}")
```

### 5.2. Snapshot Utilities

```python
def _safe_snapshot(value: Any, *, max_items: int = 200, max_str: int = 5000) -> Any:
    """Convert any value to a safe‑to‑log snapshot."""
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value if len(value) <= max_str else f"{value[:max_str]}... [truncated]"
    if isinstance(value, Mapping):
        return {k: _safe_snapshot(v) for k, v in list(value.items())[:max_items]}
    if isinstance(value, (list, tuple)):
        return [_safe_snapshot(v) for v in value[:max_items]]
    return repr(value)
```

### 5.3. Operation Context Detection

```python
def _looks_like_operation_context(obj: Any) -> bool:
    """Structural check for OperationContext‑like objects."""
    if obj is None:
        return False
    return any(hasattr(obj, attr) for attr in (
        "request_id", "idempotency_key", "deadline_ms", "traceparent"
    ))
```

### 5.4. Token Usage Coercion

```python
@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

def coerce_token_usage(result: Any, *, framework: str, error_codes, logger) -> TokenUsage:
    """Extract token usage from completion result."""
    usage_dict = {}
    
    if isinstance(result, Mapping):
        usage = result.get("usage") or {}
        if isinstance(usage, Mapping):
            usage_dict = usage
    elif hasattr(result, "usage"):
        usage = getattr(result, "usage")
        if hasattr(usage, "to_dict"):
            usage_dict = usage.to_dict()
        elif isinstance(usage, Mapping):
            usage_dict = usage
    
    return TokenUsage(
        prompt_tokens=int(usage_dict.get("prompt_tokens", 0)),
        completion_tokens=int(usage_dict.get("completion_tokens", 0)),
        total_tokens=int(usage_dict.get("total_tokens", 0)),
    )
```

### 5.5. Resource Cleanup Helpers

```python
def _maybe_close_sync(obj: Any) -> None:
    """Best‑effort sync cleanup."""
    if obj is None:
        return
    
    close_fn = getattr(obj, "close", None)
    if callable(close_fn):
        try:
            close_fn()
        except Exception as e:
            logger.debug("Failed to close object: %s", e)

async def _maybe_close_async(obj: Any) -> None:
    """Best‑effort async cleanup, falling back to sync close."""
    if obj is None:
        return
    
    aclose_fn = getattr(obj, "aclose", None)
    if callable(aclose_fn):
        try:
            await aclose_fn()
            return
        except Exception as e:
            logger.debug("Failed to async‑close object: %s", e)
    
    _maybe_close_sync(obj)
```

### 5.6. Error Context Decorator Factory

```python
def create_llm_error_context_decorator(
    framework: str,
    is_async: bool,
) -> Callable:
    """Create decorator that attaches rich error context to LLM operations."""
    def decorator(operation: str, **static_context):
        def wrap(func):
            if is_async:
                @functools.wraps(func)
                async def async_wrapper(self, *args, **kwargs):
                    try:
                        result = func(self, *args, **kwargs)
                        if hasattr(result, "__aiter__"):
                            return result
                        return await result
                    except Exception as e:
                        dynamic = _extract_dynamic_context(self, args, kwargs, operation)
                        attach_context(
                            e,
                            framework=framework,
                            operation=f"llm_{operation}",
                            **static_context,
                            **dynamic,
                        )
                        raise
                return async_wrapper
            else:
                @functools.wraps(func)
                def sync_wrapper(self, *args, **kwargs):
                    try:
                        return func(self, *args, **kwargs)
                    except Exception as e:
                        dynamic = _extract_dynamic_context(self, args, kwargs, operation)
                        attach_context(
                            e,
                            framework=framework,
                            operation=f"llm_{operation}",
                            **static_context,
                            **dynamic,
                        )
                        raise
                return sync_wrapper
        return wrap
    return decorator
```

### 5.7. Capabilities Normalization

```python
def llm_capabilities_to_dict(caps: Any) -> Dict[str, Any]:
    """Normalize capabilities response to dictionary."""
    if hasattr(caps, "to_dict"):
        return caps.to_dict()
    if isinstance(caps, dict):
        return caps
    try:
        return dict(caps)
    except Exception:
        return {"raw": str(caps)}
```

### 5.8. Streaming Iterator Normalization

```python
def _is_async_iterator(obj: Any) -> bool:
    """Return True if object implements AsyncIterator protocol."""
    return hasattr(obj, "__aiter__") and hasattr(obj, "__anext__")

async def _cleanup_async_iterator(agen: Optional[AsyncIterator]) -> None:
    """Best‑effort cleanup of async iterator."""
    if agen is None:
        return
    aclose = getattr(agen, "aclose", None)
    if callable(aclose):
        try:
            await aclose()
        except Exception as e:
            logger.debug("Failed to close async iterator: %s", e)
```

---

## 6. Cross‑Adapter Patterns

### 6.1. Unified Error Taxonomy Integration

All adapters map framework‑specific exceptions to the Corpus error taxonomy:

```python
try:
    result = await self._translator.arun_complete(...)
except BadRequest as e:
    if e.code == "CONTENT_FILTERED":
        raise ContentFilteredError("Content filtered by safety system") from e
    raise
except RateLimitExceeded as e:
    attach_context(e, retry_after_ms=e.retry_after_ms)
    raise
```

**Note:** Adapters are not required to define every error code from the global taxonomy in their local `ErrorCodes` class. Event-loop violations, for example, MAY be raised as plain `RuntimeError` with the symbolic code embedded in the message.

### 6.2. Consistent Observability

All adapters emit:
- One metric per operation (including streaming)
- Structured logs with `tenant_hash`, operation, model, latency
- Distributed trace context via `traceparent`

### 6.3. Operation Context Propagation

Framework‑specific context flows into `OperationContext` via translation helpers:

```
framework_context → context_from_framework() → OperationContext
```

For health and capabilities calls, adapters MAY omit building an `OperationContext` and delegate directly to the translator.

### 6.4. Idempotency Semantics

When `idempotency_key` is provided in operation context, adapters MUST ensure exactly‑once semantics for completion operations. The underlying translator handles deduplication.

### 6.5. Partial Failure Reporting

LLM operations typically don't have partial failures (unlike batch graph operations). However, streaming may be interrupted. The adapter MUST:

- Log the interruption with sufficient context
- Not raise an exception if partial content was already delivered
- Ensure the stream iterator terminates cleanly

### 6.6. Backpressure Integration

Adapters SHOULD:
- Surface `RateLimitExceeded` with `retry_after_ms` when rate‑limited
- Include `throttle_scope` in error details
- Propagate backpressure hints from underlying provider

### 6.7. LLM Determinism (MUST)

This section defines what “deterministic” means in the context of LLM adapters and what guarantees apply in deterministic vs. non-deterministic configurations.

#### 6.7.1 Deterministic vs. Non-Deterministic Configurations

* **Deterministic configuration** (for the underlying LLM adapter) means:

  * Sampling parameters are set to deterministic values (for example, `temperature = 0` and no stochastic sampling, or a fixed random seed where supported), **and**
  * The backing provider is configured such that it does not introduce additional randomness or non-determinism (for example, a single model endpoint with deterministic decoding).
* **Non-deterministic configuration** means:

  * Any configuration where the provider or adapter can legitimately return different results for the same input (for example, `temperature > 0`, nucleus sampling, approximate backends, sharded / load-balanced deployments, etc.).

#### 6.7.2 Adapter Requirements in Deterministic Configurations (MUST)

In deterministic configurations, adapters:

* MUST NOT introduce any additional non-determinism beyond what the underlying `LLMProtocolV1` implementation would produce for the same inputs.
* MUST produce **observationally equivalent** results across frameworks when given:

  * The same normalized messages,
  * The same sampling parameters (model, temperature, max_tokens, top_p, stop sequences, etc.), and
  * The same operation type (completion vs. streaming completion).

Concretely:

* **Completion equivalence:** For the same input messages and sampling parameters, the **final response text** and **token usage counts** returned via different framework adapters MUST match those returned by the underlying `LLMProtocolV1` implementation (within normal floating-point tolerance for usage fields).
* **Streaming equivalence:** For streaming operations, the concatenation of all streamed text chunks MUST be identical to the non-streaming completion text that would be returned for the same inputs. Chunk boundaries MAY differ; adapters MUST NOT drop, duplicate, or mutate text relative to the underlying translator output.

#### 6.7.3 Adapter Requirements in Non-Deterministic Configurations (MUST)

In non-deterministic configurations, adapters:

* MUST still NOT introduce any additional source of randomness or non-determinism (for example, they MUST NOT randomly reorder messages, alter sampling parameters, or post-process output in a way that changes the effective distribution of responses).
* MUST ensure that, for a fixed `LLMProtocolV1` implementation and configuration, different framework adapters are **distribution-equivalent**:

  * Given the same sequence of normalized messages and sampling parameters, the statistical distribution of generated responses observed over many runs MUST match that of the underlying adapter (up to sampling noise), even if individual runs differ.
* MUST ensure that streaming vs. non-streaming behavior remains consistent with the underlying translator:

  * Streaming MUST yield exactly the text produced by the translator, in the same order and without modification, even when the underlying provider itself is non-deterministic.

#### 6.7.4 Token Counting Equivalence (MUST)

Regardless of deterministic or non-deterministic configuration, adapters:

* MUST call a single shared token counting implementation (`LLMTranslator.count_tokens_for_messages()` or equivalent).
* MUST return identical token counts for the same normalized messages, model, and context across all framework adapters.
* MUST treat token counts as a pure, deterministic function of (messages, model, context); token counting MUST NOT depend on any stochastic sampling behavior.

### 6.8. Translator Shim Equivalence (MUST)

The `LLMTranslator` and `LLMFrameworkTranslator` layers MUST ensure that observable behavior is **equivalent** regardless of which underlying LLM adapter implementation is used. This means:

- Completion results must have identical text and structure
- Streaming chunks must concatenate to identical text
- Error types and codes must be consistent
- Token counts must be identical

### 6.9. Tool Passthrough Pattern

All adapters that support tool calling MUST pass tool definitions through to the translator. This may be done via **either**:

1. **Framework Context** (recommended for cross-framework observability)
2. **Top-level Parameters** (as used by AutoGen and CrewAI)

```python
# Option 1: Via framework_ctx
def _build_framework_ctx(self, kwargs):
    return {
        "framework": self._framework_name,
        "tools": kwargs.get("tools"),
        "tool_choice": kwargs.get("tool_choice"),
    }

# Option 2: Via top-level parameters
params = self._build_sampling_params(kwargs)
tools = kwargs.get("tools")
tool_choice = kwargs.get("tool_choice")
result = self._translator.arun_complete(..., tools=tools, tool_choice=tool_choice, **params)
```

**Framework-Specific Notes:**
- **AutoGen, CrewAI, LangChain, Semantic Kernel**: Support tool calling (v1)
- **LlamaIndex**: Does not support tool calling in v1 (MAY be added in future versions)

**Handling Unsupported Tools:**  
If the underlying translator or LLM adapter does not support tool calling, the adapter MUST raise a `NotSupportedError` (or framework‑specific equivalent) with a clear error message indicating that tools are not supported.

### 6.10. System Message Handling

Adapters SHOULD extract system messages into a separate `system_message` parameter where the translator expects it. Frameworks whose translators accept system messages inside the messages list (like the AutoGen client) MAY leave them untouched.

```python
def _to_translator_messages(self, messages, kwargs):
    result = []
    system_parts = []
    for msg in messages:
        role = self._extract_role(msg)
        if role == "system":
            system_parts.append(self._extract_content(msg))
        else:
            result.append({"role": role, "content": self._extract_content(msg)})
    
    if system_parts:
        # Build new kwargs, do not mutate original
        kwargs = dict(kwargs)
        kwargs["system_message"] = "\n".join(system_parts)
    
    return result, kwargs
```

**Important:** Adapters MUST NOT mutate the input `kwargs` dictionary. Instead, they should build a new dictionary for the translator.

---

## 7. AutoGen Adapter Specification

### 7.1. Overview

The AutoGen adapter exposes Corpus LLM operations as OpenAI‑style chat clients, enabling agent‑based LLM access. It solves the fundamental impedance mismatch between AutoGen's async agent runtime and synchronous LLM operations.

### 7.2. Framework‑Specific Challenges

| Challenge | Solution |
|-----------|----------|
| AutoGen expects OpenAI‑style `create`/`acreate` methods | `CorpusAutoGenChatClient` implements exactly this interface |
| Context must propagate from conversation objects | `core_ctx_from_autogen()` extracts OperationContext |
| Tool calling requires OpenAI tool schema | `_autogen_tools_to_openai()` converts AutoGen tools |
| Usage tracking across agent conversations | Optional wrapper with `total_usage()` and `reset_usage()` |

### 7.3. Data Types

```python
class AutoGenContext(TypedDict, total=False):
    agent_name: Optional[str]
    conversation_id: Optional[str]
    workflow_type: Optional[str]
    retriever_name: Optional[str]
    request_id: Optional[str]
    user_id: Optional[str]
```

### 7.4. Core Class: `CorpusAutoGenChatClient`

#### 7.4.1. OpenAI‑Style Compatibility Surface

```python
class CorpusAutoGenChatClient:
    """
    OpenAI‑style chat client backed by Corpus LLM protocol.
    
    Implements:
    - async def acreate(self, messages, **kwargs)
    - def create(self, messages, **kwargs)
    - def __call__(self, messages, **kwargs)  # alias for create
    """
```

#### 7.4.2. Initialization

```python
def __init__(
    self,
    *,
    llm_adapter: LLMProtocolV1,
    config: Optional[AutoGenClientConfig] = None,
    framework: str = "autogen",
    translator: Optional[LLMTranslator] = None,
    **kwargs,
):
    # Validate adapter
    # Store configuration
    # Initialize translator eagerly (thread-safe as object not yet published)
    # Set up resource management flags
```

#### 7.4.3. Context Translation

```python
def _build_ctx(
    self,
    *,
    conversation: Optional[Any] = None,
    extra_context: Optional[Mapping] = None,
) -> Optional[OperationContext]:
    """Translate AutoGen conversation to OperationContext."""
    return core_ctx_from_autogen(
        conversation,
        framework_version=self._config.framework_version,
        **(extra_context or {})
    )
```

#### 7.4.4. Operations

```python
@with_async_llm_error_context("acreate")
async def acreate(self, messages, **kwargs):
    # Validate messages (assumes OpenAI-style dicts)
    # Build context and parameters
    # Call translator.arun_complete or .arun_stream
    # Shape response as OpenAI‑style completion/chunks

@with_llm_error_context("create")
def create(self, messages, **kwargs):
    _ensure_not_in_event_loop("create", "acreate")  # Guarded
    # Sync implementation
```

*Note:* `health`, `capabilities`, and `count_tokens` are NOT guarded by event-loop checks (compliant with §4.8).

#### 7.4.5. Sync/Async Bridge

For Chroma compatibility (optional):

```python
_CHROMA_BRIDGE_EXECUTOR = ThreadPoolExecutor(max_workers=4, daemon=True)

def __call__(self, input):
    """Chroma embedding function interface."""
    if not _is_running_event_loop() or not self._allow_chromadb_in_event_loop:
        return self.embed_documents(list(input))
    return _CHROMA_BRIDGE_EXECUTOR.submit(
        lambda: self.embed_documents(list(input))
    ).result()
```

### 7.5. Integration Helpers

#### 7.5.1. `create_autogen_chat_completion_client()`

```python
def create_autogen_chat_completion_client(
    inner: CorpusAutoGenChatClient,
    *,
    tools: Sequence[Any] = (),
    capabilities_filter: Optional[Callable] = None,
) -> Any:
    """
    Create AutoGen Core‑compatible wrapper with usage tracking.
    
    Returns a client that:
    - Implements AutoGen's ChatCompletionClient protocol
    - Tracks token usage:
        * total_usage() -> RequestUsage: cumulative usage since wrapper creation
        * actual_usage() -> RequestUsage: usage since last reset_usage() call
        * reset_usage() -> None: resets actual usage counters to zero
        * remaining_tokens(messages, tools) -> int: estimates remaining context tokens
          (returns 0 if context window unknown)
    - Handles tool conversion via _autogen_tools_to_openai()
    - Provides remaining_tokens() for budgeting (subtracts counted tokens from
      max_context_tokens from capabilities, falls back to 10_000 if unknown)
    """
```

**Important:** `CreateResult.usage` is populated with the wrapper's internal counters (`actual_usage` at completion time). Callers that need per-call isolation SHOULD call `reset_usage()` before each logical operation.

#### 7.5.2. `_autogen_tools_to_openai()`

```python
def _autogen_tools_to_openai(tools: Sequence[Any]) -> List[Dict[str, Any]]:
    """Convert AutoGen tool objects to OpenAI tool schema."""
    # Best‑effort conversion, never raises
    # Extracts name, description, parameters from various tool shapes
```

### 7.6. Error Codes

```python
class ErrorCodes:
    BAD_OPERATION_CONTEXT = "AUTOGEN_LLM_BAD_OPERATION_CONTEXT"
    BAD_INIT_CONFIG = "AUTOGEN_LLM_BAD_INIT_CONFIG"
    BAD_COMPLETION_RESULT = "AUTOGEN_LLM_BAD_COMPLETION_RESULT"
    BAD_STREAM_CHUNK = "AUTOGEN_LLM_BAD_STREAM_CHUNK"
    BAD_USAGE_RESULT = "AUTOGEN_LLM_BAD_USAGE_RESULT"
```

*Note:* Event-loop violations raise `RuntimeError` with the symbolic code embedded in the message. `TOOL_NOT_SUPPORTED` may be raised by the translator, not by this adapter directly.

### 7.7. AutoGen‑Specific Context

The adapter extracts these fields from `conversation`:
- `agent_name` — Current agent identifier
- `conversation_id` — Active conversation
- `workflow_type` — Type of agent workflow
- `retriever_name` — Name of retriever component

---

## 8. CrewAI Adapter Specification

### 8.1. Overview

The CrewAI adapter exposes Corpus LLM operations as CrewAI‑compatible LLM wrappers, enabling role‑based agent teams to access LLM capabilities. It solves context propagation across agents that operate without a shared runtime.

### 8.2. Framework‑Specific Challenges

| Challenge | Solution |
|-----------|----------|
| No shared runtime context across agents | Extract context from per‑call `task` parameter |
| Streaming must work with CrewAI's expectations | Wrap iterators and attach error context |
| Message types vary (string, dict, CrewAI message) | `_to_translator_messages()` handles all cases |
| Optional dependency | `_ensure_crewai_installed()` guard |

### 8.3. Data Types

```python
class CrewAIContext(TypedDict, total=False):
    agent_role: Optional[str]
    agent_goal: Optional[str]
    task_description: Optional[str]
    crew_id: Optional[str]
    crew_name: Optional[str]
    process_id: Optional[str]
    task_id: Optional[str]
```

### 8.4. Core Class: `CorpusCrewAILLM`

#### 8.4.1. Initialization

```python
def __init__(
    self,
    *,
    llm_adapter: LLMProtocolV1,
    model: str = "default",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    framework_version: Optional[str] = None,
    config: Optional[CrewAILLMConfig] = None,
    translator: Optional[LLMFrameworkTranslator] = None,
):
    _ensure_crewai_installed()
    # Validate adapter
    # Build translator eagerly
```

#### 8.4.2. Context Translation

```python
def _build_operation_context(self, kwargs: Mapping[str, Any]) -> OperationContext:
    """Build OperationContext from CrewAI kwargs."""
    task = kwargs.get("task")
    ctx = core_ctx_from_crewai(
        task=task,
        framework_version=self._framework_version,
        **{k: v for k, v in kwargs.items() if k in CREWAI_CONTEXT_KEYS}
    )
    return ctx
```

#### 8.4.3. Operations

```python
@with_async_llm_error_context("acomplete")
async def acomplete(self, messages, **kwargs):
    # Normalize messages
    # Build context, params, framework_ctx
    return await self._translator.arun_complete(...)

@with_llm_error_context("complete")
def complete(self, messages, **kwargs):
    _ensure_not_in_event_loop("complete", "acomplete")  # Guarded
    # Sync implementation
```

*Note:* `health` and `capabilities` are also guarded in this adapter (stricter than required by §4.8).

#### 8.4.4. Streaming Iterator Wrapping

```python
@with_async_llm_error_context("astream")
async def astream(self, messages, **kwargs):
    agen = self._translator.arun_stream(...)
    try:
        async for chunk in agen:
            yield chunk
    finally:
        await _cleanup_async_iterator(agen)
```

### 8.5. Integration Helpers

#### 8.5.1. `_ensure_crewai_installed()`

```python
def _ensure_crewai_installed() -> None:
    """Raise helpful error if CrewAI not installed."""
    if _CREWAI_IMPORT_ERROR:
        raise RuntimeError(
            "CrewAI required. Install with: pip install crewai"
        ) from _CREWAI_IMPORT_ERROR
```

### 8.6. Error Codes

```python
class ErrorCodes:
    BAD_OPERATION_CONTEXT = "CREWAI_LLM_BAD_OPERATION_CONTEXT"
    BAD_INIT_CONFIG = "CREWAI_LLM_BAD_INIT_CONFIG"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "CREWAI_LLM_SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
    TOOL_NOT_SUPPORTED = "CREWAI_LLM_TOOL_NOT_SUPPORTED"
```

*Note:* Event-loop violations raise `RuntimeError` with the symbolic code embedded in the message.

### 8.7. CrewAI‑Specific Context

The adapter extracts from `task`:
- `agent_role` — Role of the current agent
- `agent_goal` — Agent's goal
- `task_description` — Description of the current task
- `crew_id` — Crew identifier
- `task_id` — Task identifier

---

## 9. LangChain Adapter Specification

### 9.1. Overview

The LangChain adapter implements `BaseChatModel` with full callback integration, enabling Corpus LLMs to be used in LangChain chains, agents, and retrievers.

### 9.2. Framework‑Specific Challenges

| Challenge | Solution |
|-----------|----------|
| Pydantic v2 constraints (no undeclared attributes) | `PrivateAttr` for internal state |
| Callback manager integration | `on_llm_start`, `on_llm_new_token`, `on_llm_end`, `on_llm_error` |
| Sync methods called from async contexts | Event‑loop guards |
| Multiple LangChain versions | Lazy imports with shims |

### 9.3. Data Types

```python
class LangChainContext(TypedDict, total=False):
    run_id: Optional[str]
    run_name: Optional[str]
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    configurable: Optional[Dict[str, Any]]
```

### 9.4. Core Class: `CorpusLangChainLLM`

#### 9.4.1. Pydantic Integration

```python
class CorpusLangChainLLM(BaseChatModel):
    model: str = "default"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    _translator: LLMTranslator = PrivateAttr()
    _llm_adapter: LLMProtocolV1 = PrivateAttr()
    _framework_version: Optional[str] = PrivateAttr()
```

#### 9.4.2. Initialization

```python
def __init__(self, **data):
    # Validate presence of LangChain
    # Validate llm_adapter
    super().__init__(**data)
    # Set private attributes with object.__setattr__
```

#### 9.4.3. Callback Manager Integration

```python
async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
    if run_manager:
        await run_manager.on_llm_start(...)
    try:
        result = await self._translator.arun_complete(...)
        chat_result = self._to_chat_result(result)
        if run_manager:
            await run_manager.on_llm_end(chat_result)
        return chat_result
    except Exception as e:
        if run_manager:
            await run_manager.on_llm_error(e)
        raise
```

#### 9.4.4. Operations

```python
@with_async_llm_error_context("agenerate")
async def _agenerate(self, messages, **kwargs):
    # Implementation

@with_llm_error_context("generate")
def _generate(self, messages, **kwargs):
    _ensure_not_in_event_loop("_generate", "_agenerate")  # Guarded
    # Sync implementation
```

*Note:* `health` and `capabilities` are NOT guarded in this adapter (compliant with §4.8).

#### 9.4.5. Event Loop Safety

```python
def _generate(self, ...):
    try:
        _ensure_not_in_event_loop("_generate")
        # normal sync call
    except RuntimeError:
        # fallback: run in thread
        return asyncio.run_coroutine_threadsafe(
            self._agenerate(...), loop
        ).result()
```

### 9.5. Integration Helpers

#### 9.5.1. Message Normalization

```python
def _normalize_messages(self, messages: Sequence[Any]) -> List[BaseMessage]:
    """Convert inputs to LangChain BaseMessages."""
    normalized = []
    for msg in messages:
        if isinstance(msg, BaseMessage):
            normalized.append(msg)
        elif isinstance(msg, Mapping):
            role = msg.get("role") or msg.get("type") or "user"
            content = msg.get("content", "")
            if str(role).lower() in {"assistant", "ai"}:
                normalized.append(AIMessage(content=str(content)))
            else:
                normalized.append(HumanMessage(content=str(content)))
        else:
            raise TypeError(...)
    return normalized
```

#### 9.5.2. Result Shaping

```python
def _to_chat_result(self, result):
    """Convert translator result to LangChain ChatResult."""
    # Extract text, usage, etc.
```

### 9.6. Error Codes

```python
class ErrorCodes:
    BAD_OPERATION_CONTEXT = "LANGCHAIN_LLM_BAD_OPERATION_CONTEXT"
    BAD_INIT_CONFIG = "LANGCHAIN_LLM_BAD_INIT_CONFIG"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "LANGCHAIN_LLM_SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
    TOOL_NOT_SUPPORTED = "LANGCHAIN_LLM_TOOL_NOT_SUPPORTED"
```

### 9.7. LangChain‑Specific Context

The adapter extracts from `config`:
- `run_id` — LangChain run identifier
- `run_name` — Run name
- `tags` — Snapshotted for observability
- `metadata` — Snapshotted for observability
- `configurable` — Snapshotted for observability

---

## 10. LlamaIndex Adapter Specification

### 10.1. Overview

The LlamaIndex adapter implements `LLM` with correct Pydantic initialization order and metadata construction, enabling Corpus LLMs to be used in LlamaIndex indices, query engines, and RAG pipelines.

### 10.2. Framework‑Specific Challenges

| Challenge | Solution |
|-----------|----------|
| Pydantic `__setattr__` fails before `__pydantic_extra__` exists | Call `super().__init__` first, then `object.__setattr__` |
| Metadata required (context_window, num_output) | Compute from capabilities or config |
| Message formats (legacy `.content` vs modern `.blocks`) | `_to_translator_messages()` handles both |
| Callback manager context | `context_from_llamaindex()` extracts OperationContext |

### 10.3. Data Types

```python
class LlamaIndexContext(TypedDict, total=False):
    node_ids: Optional[List[str]]
    index_id: Optional[str]
    callback_manager: Optional[Any]
    trace_id: Optional[str]
    workflow: Optional[str]
```

### 10.4. Core Class: `CorpusLlamaIndexLLM`

#### 10.4.1. Pydantic Initialization Order (CRITICAL)

```python
def __init__(self, **data):
    # Validate inputs
    super().__init__(**data)  # Pydantic init first
    # Use object.__setattr__ for internal state
    object.__setattr__(self, "_translator", create_llm_translator(...))
```

#### 10.4.2. Initialization

```python
def __init__(
    self,
    llm_adapter: LLMProtocolV1,
    model: str = "default",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    context_window: Optional[int] = None,
    **kwargs
):
    # Store adapter, build translator
```

#### 10.4.3. Metadata Construction

```python
@property
def metadata(self) -> LLMMetadata:
    ctx_window = self.context_window or 2048
    num_output = self.max_tokens or 256
    return LLMMetadata(
        context_window=ctx_window,
        num_output=num_output,
        is_chat_model=True,
        model_name=self.model,
    )
```

#### 10.4.4. Operations

```python
async def achat(self, messages, **kwargs):
    ctx = self._build_operation_context(kwargs)
    params = self._build_sampling_params(kwargs)
    normalized = self._to_translator_messages(messages)
    result = await self._translator.arun_complete(
        raw_messages=normalized,
        op_ctx=ctx,
        framework_ctx={"framework": "llamaindex", ...},
        **params
    )
    return self._to_chat_response(result)
```

*Note:* Token counting in this adapter raises `TypeError` if the translator does not return an `int` (Pattern A from §4.11).

#### 10.4.5. Callback Manager Context Translation

```python
def _build_operation_context(self, kwargs):
    callback_manager = kwargs.get("callback_manager")
    return context_from_llamaindex(
        callback_manager,
        framework_version=self.framework_version
    )
```

### 10.5. Integration Helpers

#### 10.5.1. Message Block Handling

```python
def _to_translator_messages(self, messages):
    result = []
    for msg in messages:
        if hasattr(msg, "blocks"):
            content = "".join(block.text for block in msg.blocks if hasattr(block, "text"))
        else:
            content = msg.content
        result.append({"role": msg.role.value, "content": content})
    return result
```

#### 10.5.2. Response Building

```python
def _to_chat_response(self, result):
    text, model, finish_reason, usage = _extract_completion_fields(result)
    return ChatResponse(
        message=ChatMessage(role=MessageRole.ASSISTANT, content=text),
        additional_kwargs={"model": model, "finish_reason": finish_reason, "usage": usage}
    )
```

### 10.6. Error Codes

```python
class ErrorCodes:
    BAD_OPERATION_CONTEXT = "LLAMAINDEX_LLM_BAD_OPERATION_CONTEXT"
    BAD_INIT_CONFIG = "LLAMAINDEX_LLM_BAD_INIT_CONFIG"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "LLAMAINDEX_LLM_SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
    TOOL_NOT_SUPPORTED = "LLAMAINDEX_LLM_TOOL_NOT_SUPPORTED"
```

### 10.7. LlamaIndex‑Specific Context

The adapter extracts from `callback_manager`:
- `node_ids` — IDs of nodes being processed
- `index_id` — Index identifier
- `trace_id` — Tracing identifier
- `workflow` — Workflow name

---

## 11. Semantic Kernel Adapter Specification

### 11.1. Overview

The Semantic Kernel adapter implements `ChatCompletionClientBase`, enabling Corpus LLMs to be used as services in Semantic Kernel planners, plugins, and pipelines.

### 11.2. Framework‑Specific Challenges

| Challenge | Solution |
|-----------|----------|
| Pydantic base class rejects undeclared attributes | `object.__setattr__` after `super().__init__` |
| Context comes from `PromptExecutionSettings` | `context_from_semantic_kernel()` extracts OperationContext |
| Multiple streaming method variants | `get_streaming_chat_message_content` and `get_streaming_chat_message_contents` |
| Sync aliases for async methods | Sync methods delegate to async via worker thread |

### 11.3. Data Types

```python
class SemanticKernelContext(TypedDict, total=False):
    plugin_name: Optional[str]
    function_name: Optional[str]
    kernel_id: Optional[str]
    memory_type: Optional[str]
    request_id: Optional[str]
    user_id: Optional[str]
    execution_settings: Any
```

### 11.4. Core Class: `CorpusSemanticKernelChatCompletion`

#### 11.4.1. Initialization

```python
def __init__(
    self,
    llm_adapter: LLMProtocolV1,
    model: str = "default",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    service_id: Optional[str] = None,
    **kwargs
):
    _ensure_semantic_kernel_installed()
    super().__init__(ai_model_id=model, service_id=service_id or "corpus")
    object.__setattr__(self, "_translator", create_llm_translator(...))
    # Set other private attributes
```

#### 11.4.2. Settings Context Translation

```python
def _build_operation_context(self, settings: Any) -> OperationContext:
    try:
        if settings is None:
            return context_from_semantic_kernel(
                None,
                settings=None,
                framework_version=self.framework_version,
            )
        if isinstance(settings, Mapping):
            return context_from_dict(settings)
        return context_from_semantic_kernel(
            None,
            settings=settings,
            framework_version=self.framework_version,
        )
    except Exception as ctx_exc:
        attach_context(...)
        raise
```

#### 11.4.3. Operations

```python
@with_async_llm_error_context("get_chat_message_content")
async def get_chat_message_content(self, chat_history, settings, **kwargs):
    ctx = self._build_operation_context(settings)
    params = self._build_sampling_params(settings, kwargs)
    normalized = self._to_translator_messages(chat_history)
    result = await self._translator.arun_complete(
        raw_messages=normalized,
        op_ctx=ctx,
        framework_ctx={"framework": "semantic_kernel", ...},
        **params
    )
    return result  # translator returns SK-native ChatMessageContent
```

#### 11.4.4. Sync Alias Bridging

```python
def get_chat_message_content_sync(self, chat_history, settings, **kwargs):
    _ensure_not_in_event_loop("get_chat_message_content_sync")
    return asyncio.run(
        self.get_chat_message_content(chat_history, settings, **kwargs)
    )
```

### 11.5. Integration Helpers

#### 11.5.1. Chat History Conversion

```python
def _to_translator_messages(self, chat_history):
    """Convert SK ChatHistory to generic dicts."""
    if isinstance(chat_history, str):
        return [{"role": "user", "content": chat_history}]
    result = []
    for msg in chat_history:
        if isinstance(msg, Mapping):
            result.append(dict(msg))
            continue
        
        role = getattr(msg, "role", None)
        if role is None and hasattr(msg, "author_role"):
            role = getattr(msg, "author_role", "user")
        if role is None:
            role = "user"
        
        content = getattr(msg, "content", "")
        if not content and hasattr(msg, "items"):
            content = "".join(str(i) for i in msg.items)
        
        result.append({"role": str(role), "content": str(content)})
    return result
```

### 11.6. Error Codes

```python
class ErrorCodes:
    BAD_OPERATION_CONTEXT = "SEMANTIC_KERNEL_LLM_BAD_OPERATION_CONTEXT"
    BAD_INIT_CONFIG = "SEMANTIC_KERNEL_LLM_BAD_INIT_CONFIG"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "SEMANTIC_KERNEL_LLM_SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
    TOOL_NOT_SUPPORTED = "SEMANTIC_KERNEL_LLM_TOOL_NOT_SUPPORTED"
```

### 11.7. Semantic Kernel‑Specific Context

The adapter extracts from `settings`:
- `plugin_name` — Name of the calling plugin
- `function_name` — Name of the calling function
- `kernel_id` — Kernel identifier
- `memory_type` — Type of memory operation
- `execution_settings` — Snapshotted for observability

---

## 12. Error Handling and Resilience

### 12.1. Error Code Mapping Table (Normative)

| Corpus Error Code | Framework Adapter Mapping | Retryable |
|-------------------|--------------------------|-----------|
| `BAD_OPERATION_CONTEXT` | Log warning, continue with default context | No |
| `BAD_COMPLETION_RESULT` | Raise TypeError with context | No |
| `BAD_STREAM_CHUNK` | Raise TypeError with details | No |
| `BAD_USAGE_RESULT` | Raise TypeError with details | No |
| `CONTENT_FILTERED` | Raise framework‑specific content filtered error | No |
| `RATE_LIMIT_EXCEEDED` | Raise with `retry_after_ms` | Yes |
| `DEADLINE_EXCEEDED` | Propagate with budget exhausted message | Conditional |
| `TRANSIENT_NETWORK` | Framework network error | Yes |
| `TOOL_NOT_SUPPORTED` | Raise `NotSupportedError` (or framework equivalent) | No |

**Note:** Adapters are not required to define every code in their local `ErrorCodes` class. Event-loop violations, for example, MAY be raised as `RuntimeError` with the symbolic code embedded in the message.

### 12.2. Retry Semantics

Adapters MUST NOT retry automatically unless configured to do so. When retrying:
- Honor `retry_after_ms` if present
- Use exponential backoff with jitter
- Do not retry `BadRequest` or validation errors
- Consider per‑tenant retry budgets

### 12.3. Circuit Breaking Guidance

Implementations MAY implement circuit breakers:
- Open on repeated `Unavailable` or `RateLimitExceeded`
- Half‑open after configured timeout
- Per‑tenant, per‑operation circuits RECOMMENDED

---

## 13. Observability and Monitoring

### 13.1. Metrics Taxonomy (MUST)

All adapters MUST expose:

```
llm_operations_total{framework,operation,model,code}
llm_latency_ms{framework,operation,model,quantile}
llm_tokens_total{framework,model,type}  # type = prompt/completion
llm_messages_count{framework,operation}  # histogram
```

### 13.2. Structured Logging (MUST)

```json
{
  "timestamp": "2026-02-26T10:00:00Z",
  "level": "INFO",
  "framework": "langchain",
  "operation": "agenerate",
  "tenant_hash": "a1b2c3...",
  "trace_id": "00-4bf9...",
  "model": "gpt-4",
  "messages": 5,
  "roles_distribution": {"user": 3, "assistant": 2},
  "total_content_chars": 1240,
  "temperature": 0.7,
  "max_tokens": 150,
  "prompt_tokens": 210,
  "completion_tokens": 85,
  "total_tokens": 295,
  "latency_ms": 127.4,
  "code": "OK"
}
```

**Important:** Raw tenant identifiers MAY appear in structured error context passed to `attach_context()`, but MUST NOT appear in log messages. The logging layer is responsible for redaction.

### 13.3. Distributed Tracing (SHOULD)

- Propagate `traceparent` from operation context
- Create spans for each LLM operation
- Include attributes: `framework`, `operation`, `model`, `messages_count`, `tenant_hash`
- Final span status matches operation outcome

---

## 14. Security Considerations

### 14.1. Tenant Isolation (MUST)

- `tenant` in operation context MUST be used for isolation
- Never log raw tenant identifiers in log messages; use `tenant_hash`
- Caches MUST key by `tenant_hash` when `cache_scope="tenant"`

### 14.2. Credential Handling (MUST)

- Credentials for underlying LLM adapters provisioned out‑of‑band
- Never log, snapshot, or expose credentials in error context

### 14.3. Log Redaction (MUST)

- All logs use `_safe_snapshot()` for object serialization
- Strings >64 bytes replaced with hash + length
- No raw message content, prompts, or vectors in logs
- Tenant identifiers always hashed in log messages

---

## 15. Performance Characteristics

### 15.1. Latency Targets (Indicative)

| Operation Type | Typical Range | Notes |
|----------------|---------------|-------|
| Single completion | 100–500 ms | Depends on model and provider |
| Streaming (first token) | 50–200 ms | Time to first token |
| Token counting | 1–5 ms | Local operation |
| Capabilities/Health | 1–10 ms | Cached where possible |

### 15.2. Concurrency Considerations

- All adapters are thread‑safe for concurrent use
- Translator initialization may be eager (in `__init__`) or lazy (with locks); both are compliant
- Resource cleanup safe under concurrent access
- Streaming iterators are not thread‑safe; each stream should be consumed in a single task

### 15.3. Caching Strategies

- Completion results generally not cached (dynamic)
- Token counting results can be cached with TTL
- Cache keys MUST include `tenant_hash` and model
- Respect `cache_scope` and `cache_tags` when provided
- Never cache across tenant boundaries

---

## 16. Implementation Guidelines

### 16.1. Adapter Implementation Order

1. Copy shared utilities from existing adapter
2. Implement `__init__` with validation and translator initialization
3. Add error context decorators
4. Implement core LLM methods (complete, stream, token counting)
5. Add context extraction and building
6. Implement resource management (context managers, optional lifecycle)
7. Add integration helpers (wrappers, converters)
8. Write conformance tests

### 16.2. Validation Requirements (MUST)

- Validate `llm_adapter` has required methods (`complete`, `stream`, `count_tokens`, `health`, `capabilities`)
- Validate messages are non‑empty and have required fields
- Validate temperature is within [0.0, 2.0] at construction time
- Validate `max_tokens` is positive if provided at construction time
- Reject unknown config keys in configuration dataclasses

### 16.3. Testing

#### 16.3.1. Conformance Test Suite

Each adapter MUST pass:
- Wire format validation (messages → translator format)
- Error normalization tests (context attachment, error code patterns)
- Sampling parameter resolution tests
- Streaming tests (sync and async)
- Token counting tests (with various inputs)
- Event loop guard tests for chat/stream methods
- Resource cleanup tests (context manager behavior)

#### 16.3.2. Framework‑Specific Tests

- **AutoGen:** Tool conversion, usage tracking wrapper, `create`/`acreate` parity
- **CrewAI:** Context extraction from task, streaming iterator wrapping
- **LangChain:** Callback manager integration, Pydantic init order, sync‑in‑async fallback
- **LlamaIndex:** Pydantic init order, metadata construction, block handling
- **Semantic Kernel:** Settings translation, sync alias bridging

#### 16.3.3. Cross‑Adapter Tests

- All adapters produce identical completions for same inputs (within tolerance, see §6.7)
- Error handling patterns consistent across frameworks
- Observability fields follow same patterns
- Resource cleanup behavior matches documented pattern

---

## 17. Versioning and Compatibility

### 17.1. Semantic Versioning (MUST)

Adapter packages MUST use Semantic Versioning:
- MAJOR: Breaking changes to public API
- MINOR: Additive, backward‑compatible features
- PATCH: Bug fixes and internal improvements

### 17.2. Framework Version Compatibility

Adapters SHOULD document supported framework versions. "Tested" means that the adapter has passed the conformance test suite against those specific framework versions.

- AutoGen: ≥0.4.0 (tested)
- CrewAI: ≥0.30.0 (tested)
- LangChain: ≥0.1.0, ≤0.3.x (tested)
- LlamaIndex: ≥0.10.0 (tested)
- Semantic Kernel: ≥1.0.0 (tested)

### 17.3. Deprecation Policy

- Deprecated features documented for one minor version
- Removal only in MAJOR version bump
- Migration guides provided for breaking changes

---

## 18. References

### 18.1. Normative References

- [RFC2119] Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997.
- [RFC8174] Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words", BCP 14, RFC 8174, May 2017.
- Corpus LLM Protocol V1.0 Specification
- Corpus Common Foundation Specification

### 18.2. Informative References

- AutoGen Documentation: https://microsoft.github.io/autogen/
- CrewAI Documentation: https://docs.crewai.com/
- LangChain Documentation: https://python.langchain.com/
- LlamaIndex Documentation: https://docs.llamaindex.ai/
- Semantic Kernel Documentation: https://learn.microsoft.com/en-us/semantic-kernel/

---

## Appendix A — Comparison Matrix: Framework‑Specific Challenges

| Framework | Primary Challenge | Adapter Solution |
|-----------|------------------|------------------|
| AutoGen | OpenAI‑style client + usage tracking | `CorpusAutoGenChatClient` + optional wrapper |
| CrewAI | No shared runtime context | Per‑call context extraction from `task` |
| LangChain | Pydantic + callback integration | `PrivateAttr`, callback hooks, event‑loop guards |
| LlamaIndex | Pydantic init order + metadata | `super().__init__` first + `object.__setattr__`, metadata from capabilities |
| Semantic Kernel | Settings translation + sync aliases | `context_from_semantic_kernel()`, worker thread for sync |

---

## Appendix B — Code Pattern Catalog (Normative)

### B.1. Context Building Patterns

```python
# Framework‑specific context building
def _build_ctx(self, *, framework_input=None, **kwargs):
    try:
        ctx = core_ctx_from_framework(framework_input, **kwargs)
    except Exception:
        logger.warning("Context translation failed")
        ctx = OperationContext()
    return ctx
```

### B.2. Error Context Decorator Patterns

```python
# Decorator with lazy dynamic extraction
@with_llm_error_context("complete")
def complete(self, messages, **kwargs):
    # normal logic
```

### B.3. Event Loop Safety Patterns

```python
# Guard pattern for chat/stream methods
_ensure_not_in_event_loop("sync_method", "async_method")

# Worker thread fallback (optional)
try:
    return sync_method()
except RuntimeError:
    return asyncio.run_coroutine_threadsafe(async_method(), loop).result()
```

### B.4. Streaming Iterator Patterns

```python
# Async streaming with cleanup
async def astream(self, messages, **kwargs):
    agen = self._translator.arun_stream(...)
    try:
        async for chunk in agen:
            yield chunk
    finally:
        await _cleanup_async_iterator(agen)
```

### B.5. Resource Cleanup Patterns

```python
# Pattern 1: Full lifecycle (explicit close)
def close(self):
    _ensure_not_in_event_loop("close")
    _maybe_close_sync(self._translator_cache)

# Pattern 2: Context-manager-only
def __exit__(self, exc_type, exc, tb):
    _maybe_close_sync(self._llm_adapter)  # translator not closed
```

### B.6. Pydantic Initialization Patterns

```python
# LangChain pattern (PrivateAttr)
class MyLLM(BaseChatModel):
    _private: Any = PrivateAttr()
    def __init__(self, ...):
        super().__init__(...)
        object.__setattr__(self, "_private", value)

# LlamaIndex pattern (super first)
def __init__(self, ...):
    # validate with locals
    super().__init__(...)
    object.__setattr__(self, "field", value)
```

### B.7. Token Counting Patterns

```python
# Pattern A: int only (AutoGen, LlamaIndex)
def count_tokens(self, messages, **kwargs):
    result = self._translator.count_tokens_for_messages(...)
    if isinstance(result, int):
        return result
    raise TypeError(...)

# Pattern B: int or Mapping (CrewAI, LangChain, Semantic Kernel)
def count_tokens(self, messages, **kwargs):
    result = self._translator.count_tokens_for_messages(...)
    if isinstance(result, int):
        return result
    if isinstance(result, Mapping):
        for key in ("tokens", "total_tokens", "count"):
            if key in result and isinstance(result[key], int):
                return result[key]
    raise TypeError(...)
```

---

## Appendix C — End‑to‑End Usage Examples

### C.1. AutoGen Agent with Chat Client

```python
from corpus_sdk.llm.framework_adapters.autogen import (
    CorpusAutoGenChatClient,
    create_autogen_chat_completion_client,
)
from autogen_agentchat.agents import AssistantAgent

client = CorpusAutoGenChatClient(
    llm_adapter=my_adapter,
    model="gpt-4",
    temperature=0.7
)

# Optional: wrap for AutoGen Core with usage tracking
autogen_client = create_autogen_chat_completion_client(
    client,
    tools=[my_tool]
)

agent = AssistantAgent(
    name="llm_agent",
    model_client=autogen_client,
)
```

### C.2. CrewAI Agent with LLM

```python
from corpus_sdk.llm.framework_adapters.crewai import CorpusCrewAILLM
from crewai import Agent

llm = CorpusCrewAILLM(
    llm_adapter=my_adapter,
    model="gpt-4",
    temperature=0.7
)

agent = Agent(
    role="Researcher",
    goal="Answer questions",
    backstory="...",
    llm=llm
)
```

### C.3. LangChain Chain with Chat Model

```python
from corpus_sdk.llm.framework_adapters.langchain import CorpusLangChainLLM
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate

llm = CorpusLangChainLLM(
    llm_adapter=my_adapter,
    model="gpt-4",
    temperature=0.7
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}")
])
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(input="Hello!")
```

### C.4. LlamaIndex Query Engine with LLM

```python
from corpus_sdk.llm.framework_adapters.llamaindex import CorpusLlamaIndexLLM
from llama_index.core import Settings, VectorStoreIndex

llm = CorpusLlamaIndexLLM(
    llm_adapter=my_adapter,
    model="gpt-4",
    temperature=0.7,
    context_window=8192
)

Settings.llm = llm
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("What is the capital of France?")
```

### C.5. Semantic Kernel Plugin Registration

```python
from corpus_sdk.llm.framework_adapters.semantic_kernel import CorpusSemanticKernelChatCompletion
import semantic_kernel as sk

kernel = sk.Kernel()

chat = CorpusSemanticKernelChatCompletion(
    llm_adapter=my_adapter,
    model="gpt-4",
    service_id="my-chat"
)

kernel.add_service(chat)

# Use in semantic function
prompt = "{{$input}}"
func = kernel.create_semantic_function(prompt)
result = await kernel.run_async(func, input="Hello!")
```

---

## Appendix D — Error Code Reference

| Code | Description | Frameworks | Notes |
|------|-------------|------------|-------|
| `BAD_OPERATION_CONTEXT` | Failed to build OperationContext | All | |
| `BAD_INIT_CONFIG` | Invalid initialization configuration | All | |
| `BAD_COMPLETION_RESULT` | Completion result has wrong type | All | |
| `BAD_STREAM_CHUNK` | Stream chunk has wrong type | All | |
| `BAD_USAGE_RESULT` | Token usage result has wrong type | All | |
| `SYNC_WRAPPER_CALLED_IN_EVENT_LOOP` | Sync method called from async context | All | MAY be embedded in RuntimeError message |
| `CONTENT_FILTERED` | Content filtered by safety system | All | |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded, retry after | All | |
| `TOOL_NOT_SUPPORTED` | Tool calling not supported | All | MAY be raised by translator |

---

## Appendix E — Implementation Status (Non‑Normative)

| Adapter | Cleanup Pattern | Translator Init | Event Loop Guards | Token Counting |
|---------|----------------|------------------|-------------------|----------------|
| AutoGen | Context-manager-only | Eager | Chat/stream only | int only |
| CrewAI | Context-manager-only | Eager | All sync methods | int/Mapping |
| LangChain | Context-manager-only | Eager | Chat/stream only | int/Mapping |
| LlamaIndex | Context-manager-only | Eager | N/A (no sync methods) | int only |
| Semantic Kernel | Full lifecycle | Eager | Sync wrappers only | int/Mapping |

**Note:** This appendix is non‑normative and provided for informational purposes only. The authoritative conformance status is determined by the conformance test suite (§16.3) and the implementation’s own documentation.

---

## Appendix F — Migration from Existing Framework Adapters (Informative)

### From Custom AutoGen Chat Client

```python
# Before
class MyAutoGenClient:
    async def acreate(self, messages):
        return {"choices": [{"message": {"content": my_llm(messages)}}]}

# After
from corpus_sdk.llm.framework_adapters.autogen import CorpusAutoGenChatClient
client = CorpusAutoGenChatClient(llm_adapter=my_adapter)
```

### From Custom LangChain LLM

```python
# Before
class MyLLM(LLM):
    def _call(self, prompt, stop=None):
        return my_llm(prompt)

# After
from corpus_sdk.llm.framework_adapters.langchain import CorpusLangChainLLM
llm = CorpusLangChainLLM(llm_adapter=my_adapter)
```

### From Custom LlamaIndex LLM

```python
# Before
class MyLLM(LLM):
    def chat(self, messages):
        return ChatResponse(message=ChatMessage(role="assistant", content=my_llm(messages)))

# After
from corpus_sdk.llm.framework_adapters.llamaindex import CorpusLlamaIndexLLM
llm = CorpusLlamaIndexLLM(llm_adapter=my_adapter)
```
