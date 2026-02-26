# EMBEDDING FRAMEWORK ADAPTERS SPECIFICATION

**specification_version:** `1.0.0`   
**protocol_version:** `1.0.0`   

---

## Abstract

This specification defines the Corpus Framework Adapter Suite: a standardized set of production-grade adapters that bridge Corpus Embedding Protocol V1.0 implementations with five leading AI orchestration frameworks—AutoGen, CrewAI, LangChain, LlamaIndex, and Semantic Kernel. The suite provides consistent patterns for context propagation, error handling, observability, and resource management across frameworks while preserving each framework's native interfaces. This document includes normative contracts for adapter behavior, cross-framework patterns, error taxonomy integration, observability requirements, and implementation guidelines for enterprise-scale deployments.

> **Keywords:** Framework Adapters, AutoGen, CrewAI, LangChain, LlamaIndex, Semantic Kernel, Embeddings, Context Propagation, Error Normalization, Observability, Multi-Framework, Protocol Bridge, Production Hardening

---

## Table of Contents

* [1. Introduction](#1-introduction)
  * [1.1. Motivation](#11-motivation)
  * [1.2. Scope](#12-scope)
  * [1.3. Design Philosophy](#13-design-philosophy)
* [2. Requirements Language](#2-requirements-language)
* [3. Terminology](#3-terminology)
* [4. Common Foundation Across All Adapters](#4-common-foundation-across-all-adapters)
  * [4.1. Protocol-First Design (MUST)](#41-protocol-first-design-must)
  * [4.2. Framework Resilience Strategy](#42-framework-resilience-strategy)
  * [4.3. Error Context Attachment (MUST)](#43-error-context-attachment-must)
  * [4.4. Dynamic Context Extraction Pattern](#44-dynamic-context-extraction-pattern)
  * [4.5. Coercion Pipeline (MUST)](#45-coercion-pipeline-must)
  * [4.6. Thread-Safe Lazy Initialization (MUST)](#46-thread-safe-lazy-initialization-must)
  * [4.7. Resource Cleanup Hierarchy (MUST)](#47-resource-cleanup-hierarchy-must)
  * [4.8. Event Loop Guards (MUST)](#48-event-loop-guards-must)
  * [4.9. Dimension Management (SHOULD)](#49-dimension-management-should)
  * [4.10. Batch Processing Semantics (MUST)](#410-batch-processing-semantics-must)
  * [4.11. Empty Text Handling (MUST)](#411-empty-text-handling-must)
  * [4.12. SIEM-Safe Observability (MUST)](#412-siem-safe-observability-must)
  * [4.13. Testing Accommodations (INFORMATIVE)](#413-testing-accommodations-informative)
  * [4.14. Adapter Lifecycle State Machine (MUST)](#414-adapter-lifecycle-state-machine-must)
* [5. Shared Utility Layer](#5-shared-utility-layer)
  * [5.1. Validation Utilities](#51-validation-utilities)
  * [5.2. Snapshot Utilities](#52-snapshot-utilities)
  * [5.3. Operation Context Detection](#53-operation-context-detection)
  * [5.4. Coercion Error Codes](#54-coercion-error-codes)
  * [5.5. Resource Cleanup Helpers](#55-resource-cleanup-helpers)
* [6. Cross-Adapter Patterns](#6-cross-adapter-patterns)
  * [6.1. Unified Error Taxonomy Integration](#61-unified-error-taxonomy-integration)
  * [6.2. Consistent Observability](#62-consistent-observability)
  * [6.3. Operation Context Propagation](#63-operation-context-propagation)
  * [6.4. Idempotency Semantics](#64-idempotency-semantics)
  * [6.5. Partial Failure Reporting](#65-partial-failure-reporting)
  * [6.6. Backpressure Integration](#66-backpressure-integration)
  * [6.7. Embedding Determinism (MUST)](#67-embedding-determinism-must)
  * [6.8. Translator Shim Equivalence (MUST)](#68-translator-shim-equivalence-must)
* [7. AutoGen Adapter Specification](#7-autogen-adapter-specification)
  * [7.1. Overview](#71-overview)
  * [7.2. Framework-Specific Challenges](#72-framework-specific-challenges)
  * [7.3. Data Types](#73-data-types)
  * [7.4. Core Class: `CorpusAutoGenEmbeddings`](#74-core-class-corpusautogenembeddings)
    * [7.4.1. Chroma Compatibility Surface](#741-chroma-compatibility-surface)
    * [7.4.2. Initialization](#742-initialization)
    * [7.4.3. Sync/Async Bridge](#743-syncasync-bridge)
    * [7.4.4. Operations](#744-operations)
  * [7.5. Integration Helpers](#75-integration-helpers)
    * [7.5.1. `create_vector_memory()`](#751-create_vector_memory)
    * [7.5.2. `register_embeddings()`](#752-register_embeddings)
  * [7.6. Error Codes](#76-error-codes)
  * [7.7. AutoGen-Specific Context](#77-autogen-specific-context)
* [8. CrewAI Adapter Specification](#8-crewai-adapter-specification)
  * [8.1. Overview](#81-overview)
  * [8.2. Framework-Specific Challenges](#82-framework-specific-challenges)
  * [8.3. Data Types](#83-data-types)
  * [8.4. Core Class: `CorpusCrewAIEmbeddings`](#84-core-class-corpuscrewaiembeddings)
    * [8.4.1. Initialization](#841-initialization)
    * [8.4.2. Operations](#842-operations)
  * [8.5. Integration Helpers](#85-integration-helpers)
    * [8.5.1. `create_embedder()`](#851-create_embedder)
    * [8.5.2. `register_with_crewai()`](#852-register_with_crewai)
  * [8.6. Error Codes](#86-error-codes)
  * [8.7. CrewAI-Specific Context](#87-crewai-specific-context)
* [9. LangChain Adapter Specification](#9-langchain-adapter-specification)
  * [9.1. Overview](#91-overview)
  * [9.2. Framework-Specific Challenges](#92-framework-specific-challenges)
  * [9.3. Data Types](#93-data-types)
  * [9.4. Core Class: `CorpusLangChainEmbeddings`](#94-core-class-corpuslangchainembeddings)
    * [9.4.1. Pydantic Integration](#941-pydantic-integration)
    * [9.4.2. Initialization](#942-initialization)
    * [9.4.3. Event Loop Safety](#943-event-loop-safety)
    * [9.4.4. Operations](#944-operations)
  * [9.5. Integration Helpers](#95-integration-helpers)
    * [9.5.1. `configure_langchain_embeddings()`](#951-configure_langchain_embeddings)
    * [9.5.2. `register_with_langchain()`](#952-register_with_langchain)
  * [9.6. Error Codes](#96-error-codes)
  * [9.7. LangChain-Specific Context](#97-langchain-specific-context)
* [10. LlamaIndex Adapter Specification](#10-llamaindex-adapter-specification)
  * [10.1. Overview](#101-overview)
  * [10.2. Framework-Specific Challenges](#102-framework-specific-challenges)
  * [10.3. Data Types](#103-data-types)
  * [10.4. Core Class: `CorpusLlamaIndexEmbeddings`](#104-core-class-corpusllamaindexembeddings)
    * [10.4.1. Pydantic Initialization Order (CRITICAL)](#1041-pydantic-initialization-order-critical)
    * [10.4.2. Translator Shim Pattern](#1042-translator-shim-pattern)
    * [10.4.3. Initialization](#1043-initialization)
    * [10.4.4. Operations](#1044-operations)
  * [10.5. Integration Helpers](#105-integration-helpers)
    * [10.5.1. `configure_llamaindex_embeddings()`](#1051-configure_llamaindex_embeddings)
    * [10.5.2. `register_with_llamaindex()`](#1052-register_with_llamaindex)
  * [10.6. Error Codes](#106-error-codes)
  * [10.7. LlamaIndex-Specific Context](#107-llamaindex-specific-context)
* [11. Semantic Kernel Adapter Specification](#11-semantic-kernel-adapter-specification)
  * [11.1. Overview](#111-overview)
  * [11.2. Framework-Specific Challenges](#112-framework-specific-challenges)
  * [11.3. Data Types](#113-data-types)
  * [11.4. Core Class: `CorpusSemanticKernelEmbeddings`](#114-core-class-corpus-semantic-kernel-embeddings)
    * [11.4.1. Direct Translator Detection](#1141-direct-translator-detection)
    * [11.4.2. Initialization](#1142-initialization)
    * [11.4.3. Sync Alias Bridging](#1143-sync-alias-bridging)
    * [11.4.4. Operations](#1144-operations)
  * [11.5. Integration Helpers](#115-integration-helpers)
    * [11.5.1. `configure_semantic_kernel_embeddings()`](#1151-configure_semantic_kernel_embeddings)
    * [11.5.2. `register_with_semantic_kernel()`](#1152-register_with_semantic_kernel)
  * [11.6. Error Codes](#116-error-codes)
  * [11.7. Semantic Kernel-Specific Context](#117-semantic-kernel-specific-context)
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
    * [16.3.2. Framework-Specific Tests](#1632-framework-specific-tests)
    * [16.3.3. Cross-Adapter Tests](#1633-cross-adapter-tests)
* [17. Versioning and Compatibility](#17-versioning-and-compatibility)
  * [17.1. Semantic Versioning (MUST)](#171-semantic-versioning-must)
  * [17.2. Framework Version Compatibility](#172-framework-version-compatibility)
  * [17.3. Deprecation Policy](#173-deprecation-policy)
* [18. References](#18-references)
  * [18.1. Normative References](#181-normative-references)
  * [18.2. Informative References](#182-informative-references)
* [Appendix A — Comparison Matrix: Framework-Specific Challenges](#appendix-a--comparison-matrix-framework-specific-challenges)
* [Appendix B — Code Pattern Catalog (Normative)](#appendix-b--code-pattern-catalog-normative)
  * [B.1. Pydantic Initialization Patterns](#b1-pydantic-initialization-patterns)
  * [B.2. Event Loop Safety Patterns](#b2-event-loop-safety-patterns)
  * [B.3. Resource Cleanup Patterns](#b3-resource-cleanup-patterns)
  * [B.4. Context Extraction Patterns](#b4-context-extraction-patterns)
* [Appendix C — End-to-End Usage Examples](#appendix-c--end-to-end-usage-examples)
  * [C.1. AutoGen with Chroma Memory](#c1-autogen-with-chroma-memory)
  * [C.2. CrewAI Agent with Embedder](#c2-crewai-agent-with-embedder)
  * [C.3. LangChain Vector Store](#c3-langchain-vector-store)
  * [C.4. LlamaIndex Settings Integration](#c4-llamaindex-settings-integration)
  * [C.5. Semantic Kernel Plugin](#c5-semantic-kernel-plugin)
* [Appendix D — Error Code Reference](#appendix-d--error-code-reference)
* [Appendix E — Implementation Status (Non-Normative)](#appendix-e--implementation-status-non-normative)
* [Appendix F — Migration from Existing Framework Adapters (Informative)](#appendix-f--migration-from-existing-framework-adapters-informative)

---

## 1. Introduction

### 1.1. Motivation

The AI framework landscape has fragmented into five dominant orchestration layers—AutoGen for multi-agent systems, CrewAI for role-based agent teams, LangChain for chain-of-thought pipelines, LlamaIndex for RAG and indexing, and Semantic Kernel for enterprise AI integration. Each framework defines its own embedding interface with subtly different expectations:

- **AutoGen** requires Chroma-compatible `embedding_function` callables and struggles with async/sync boundaries in agent loops.
- **CrewAI** expects embedders attached to agents but provides no shared runtime context across agent executions.
- **LangChain** defines `Embeddings` as Pydantic models but allows sync methods to be called from async contexts, creating deadlock risks.
- **LlamaIndex** implements `BaseEmbedding` as a Pydantic model with strict initialization order requirements that crash when attributes are set too early.
- **Semantic Kernel** uses `EmbeddingGeneratorBase` with Pydantic constraints and multiple registration paths across versions.

Building and maintaining separate adapters for each framework duplicates effort, fragments observability, and creates inconsistent error handling across an organization's AI stack. Framework-specific edge cases—like Chroma calling sync methods from event loops, or Pydantic rejecting undeclared attributes—cause production outages that are difficult to debug without deep framework expertise.

The Corpus Framework Adapter Suite solves this by providing a single, battle-tested implementation of each framework's embedding interface, backed by the Corpus Embedding Protocol. Each adapter encapsulates the framework-specific hardening required for production deployments while sharing a common foundation for error handling, observability, and resource management. Organizations can standardize on Corpus embeddings once and use them across any supported framework without rebuilding adapter logic.

### 1.2. Scope

This specification defines five framework adapters:

1. **AutoGen Adapter** — Implements Chroma-compatible `embedding_function` with thread-pool bridging for event-loop safety, plus `create_vector_memory()` helper for AutoGen's ChromaDB-backed memory.

2. **CrewAI Adapter** — Implements `CrewAIEmbedder` protocol with context extraction from agent roles and tasks, plus `register_with_crewai()` for auto-attaching to all agents in a crew.

3. **LangChain Adapter** — Implements `langchain_core.embeddings.Embeddings` with Pydantic v2 compatibility, event-loop detection, and worker-thread fallback for sync methods called from async contexts.

4. **LlamaIndex Adapter** — Implements `llama_index.core.embeddings.BaseEmbedding` with correct Pydantic initialization order, translator shim for EmbedSpec compatibility, and `strict_text_types` mode for row-aligned batch processing.

5. **Semantic Kernel Adapter** — Implements `semantic_kernel.connectors.ai.embeddings.EmbeddingGeneratorBase` with direct translator detection for plain-text adapters, sync alias bridging, and multiple registration paths.

All adapters share:

- **Context propagation** — Framework-specific context (agent_name, task_id, run_id, node_ids, plugin_name) flows into `OperationContext` and framework_ctx.
- **Error normalization** — All exceptions are enriched with `attach_context()` using framework-specific error codes.
- **Observability** — Dynamic context extraction captures batch sizes, empty texts, routing fields, and dimension hints.
- **Resource management** — Sync/async context managers with proper cleanup hierarchy.
- **Dimension management** — First-write-wins dimension hints and empty-text zero vectors.

### 1.3. Design Philosophy

- **Protocol-First (MUST).** Adapters require only duck-typed `embed` methods, not strict inheritance from Corpus base classes. This allows minimal test doubles and lightweight integrations.

- **Framework Resilience (MUST).** Adapters defend against framework evolution by filtering context, normalizing inputs, and never assuming internal APIs remain stable. Static compatibility methods satisfy Chroma's serialization probes without leaking implementation details.

- **Observability-First (MUST).** Every embedding operation attaches rich error context: framework identity, model info, batch sizes, empty text counts, and routing fields. Exceptions crossing framework boundaries carry enough context to debug without log scraping.

- **Fail-Safe Context Translation (MUST).** Context translation from framework-specific structures to `OperationContext` must never break embeddings. If translation fails, adapters proceed without core context and attach diagnostic snapshots.

- **Strict by Default (SHOULD).** Non-string inputs in batch operations are rejected with `TypeError` to avoid silently embedding `repr()` output. Lenient modes (`strict_text_types=False`) are available but must preserve row alignment with zero vectors.

- **Async-Safe Sync Usage (MUST).** Sync APIs enforce guard rails preventing calls from inside active event loops. When bridging is required for tests, adapters use controlled worker-thread execution.

- **Production Hardening (MUST).** Thread-safe lazy initialization, resource cleanup hierarchies, SIEM-safe logging, and dimension consistency are non-negotiable requirements.

---

## 2. Requirements Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [RFC2119] [RFC8174] when, and only when, they appear in all capitals.

**Example:**  
- "The adapter MUST reject non‑string inputs" indicates a strict requirement that must be implemented and verified.  
- "The adapter SHOULD log warnings for large batches" indicates a recommendation that may be deviated from only with good reason.  

**Justified Deviation Example:**  
A developer might choose to disable the `strict_text_types` validation (which is a SHOULD-level recommendation) in a controlled environment where they have verified that all inputs are strings, and where the performance cost of validation is significant. This deviation MUST be documented in the code, explaining why it is safe and what assumptions are being made. The adapter MUST still provide a way to re-enable strict validation (e.g., via a configuration flag) because the default behavior is RECOMMENDED.

---

## 3. Terminology

**Adapter** — Concrete implementation of a framework-specific embedding interface backed by a Corpus Embedding Protocol V1 adapter.

**Corpus Adapter** — The underlying embedding implementation that provides the `embed` method (duck-typed `EmbeddingProtocolV1`).

**Operation Context** — Core context object containing `request_id`, `idempotency_key`, `deadline_ms`, `traceparent`, `tenant`, and `attrs`.

**Framework Context** — Framework-specific context dictionary passed to the translator alongside core context.

**Translator** — `EmbeddingTranslator` instance that orchestrates embedding calls, batching, retries, and caching.

**Direct Translator** — Minimal translator for adapters that implement plain `embed(texts: Sequence[str])` signatures without EmbedSpec support.

**Coercion Pipeline** — Shared utilities that validate and convert raw embedding results into `List[List[float]]` or `List[float]` with consistent error codes.

**Event Loop Guard** — Runtime check preventing sync methods from being called inside an active asyncio event loop.

**Dimension Hint** — Best-effort, first-write-wins embedding dimension stored for observability and zero-vector fallback.

**SIEM-Safe** — Observability that excludes PII, raw content, and tenant identifiers, using hashes and structural metadata instead.

---

## 4. Common Foundation Across All Adapters

### 4.1. Protocol-First Design (MUST)

All adapters MUST accept a `corpus_adapter` parameter that implements an `embed` method. Strict `isinstance` checks against `EmbeddingProtocolV1` are NOT REQUIRED; behavioral duck typing suffices.

```python
# Valid corpus_adapter implementations:
class MinimalAdapter:
    def embed(self, texts, **kwargs): ...

class FullAdapter:
    async def embed(self, spec, ctx=None): ...
    def capabilities(self): ...
    def health(self): ...
    def close(self): ...
    async def aclose(self): ...
```

Adapters MUST validate at initialization:

```python
if not hasattr(corpus_adapter, "embed") or not callable(getattr(corpus_adapter, "embed", None)):
    raise TypeError("corpus_adapter must implement an 'embed' method")
```

### 4.2. Framework Resilience Strategy

All adapters implement three defensive layers:

1. **Context Filtering** — Extract only known, stable fields from framework-specific context objects. Unknown keys are ignored (see §4.4). Unknown fields are snapshotted for observability but not relied upon for correctness.

2. **Normalized Error Attachment** — All exceptions are enriched with `attach_context()` using framework-specific error codes and dynamic context (batch sizes, routing fields).

3. **Static Compatibility Methods** — For frameworks that probe adapter classes (e.g., Chroma's `name()`, `get_config()`), adapters provide static methods that return stable, JSON-serializable values without depending on instance state.

### 4.3. Error Context Attachment (MUST)

Every adapter MUST decorate its core embedding methods with error-context decorators that capture:

- Operation name (`embedding_documents`, `embedding_query`, `capabilities`, `health`)
- Framework identity and version
- Model identifier
- Text length (for single-text operations)
- Batch size and empty text count (for batch operations)
- Framework-specific routing fields
- Dimension hint (when available)

```python
@with_embedding_error_context("documents")
def embed_documents(self, texts, ...): ...

@with_async_embedding_error_context("query")
async def aembed_query(self, text, ...): ...
```

### 4.4. Dynamic Context Extraction Pattern

All adapters implement an `_extract_dynamic_context()` helper that captures per-call metrics:

```python
def _extract_dynamic_context(self, args, kwargs, operation):
    ctx = {
        "model": getattr(self, "model", "unknown"),
        "framework_version": getattr(self, "_framework_version", None),
    }
    
    if operation in ("query", "text") and args and isinstance(args[0], str):
        ctx["text_len"] = len(args[0])
    elif operation in ("documents", "texts") and args:
        maybe_texts = args[0]
        if isinstance(maybe_texts, Sequence) and not isinstance(maybe_texts, (str, bytes)):
            ctx["texts_count"] = len(maybe_texts)
            # Count empty strings
            empty_count = sum(1 for t in maybe_texts if not isinstance(t, str) or not t.strip())
            if empty_count:
                ctx["empty_texts_count"] = empty_count
    
    # Framework-specific fields: extract known keys, ignore unknown
    framework_ctx = kwargs.get("framework_specific_context")
    if isinstance(framework_ctx, Mapping):
        for key in self._framework_routing_fields:   # defined per adapter
            if key in framework_ctx:
                ctx[key] = framework_ctx[key]
        # Unknown keys are ignored (not passed to core context)
    
    return ctx
```

**Versioning Contract:** Framework context dictionaries (e.g., `autogen_context`, `crewai_context`) MAY contain keys unknown to the adapter. Adapters MUST ignore such keys and MUST NOT raise errors because of them. This ensures forward compatibility when frameworks add new fields.

### 4.5. Coercion Pipeline (MUST)

All adapters MUST use the shared coercion utilities from `framework_utils`:

```python
def _coerce_embedding_matrix(self, result):
    return coerce_embedding_matrix(
        result=result,
        framework=self._framework_name,
        error_codes=self.EMBEDDING_COERCION_ERROR_CODES,
        logger=logger,
    )

def _coerce_embedding_vector(self, result):
    return coerce_embedding_vector(
        result=result,
        framework=self._framework_name,
        error_codes=self.EMBEDDING_COERCION_ERROR_CODES,
        logger=logger,
    )
```

**Coercion Failure Conditions (Normative):**  
The coercion utilities MUST detect and raise appropriate errors for the following conditions:

- **Shape mismatch:** For matrix coercion, if the result is not a list of lists (or equivalent sequence of sequences). For vector coercion, if the result is not a list of numbers.
- **Non-float elements:** Any element that is not a `float` or cannot be converted to float without loss (e.g., string `"nan"` is not acceptable).
- **NaN or Inf values:** If any element is `math.nan` or `math.inf` (or negative infinity), the adapter MUST raise a `ValueError` with an error code indicating invalid embedding result. (Zero vectors are only allowed for empty texts as per §4.11.)
- **Dimension mismatch:** If the embedding dimension is known (from previous calls or explicit `embedding_dimension`), and the coerced vector has a different length, the adapter MUST raise a `ValueError`.

These conditions are verified by the conformance test suite (§16.3.1).

### 4.6. Thread-Safe Lazy Initialization (MUST)

Translators and other expensive resources MUST be initialized lazily with thread safety:

```python
@cached_property
def _translator(self):
    with self._lock:
        if self._translator_cache is None:
            self._translator_cache = create_embedding_translator(...)
        return self._translator_cache
```

### 4.7. Resource Cleanup Hierarchy (MUST)

All adapters MUST implement both sync and async context managers with proper cleanup:

```python
def __enter__(self):
    return self

def __exit__(self, exc_type, exc, tb):
    self.close()

async def __aenter__(self):
    return self

async def __aexit__(self, exc_type, exc, tb):
    await self.aclose()

def close(self):
    _ensure_not_in_event_loop("close")
    _maybe_close_sync(self._translator_cache)
    _maybe_close_sync(self.corpus_adapter)

async def aclose(self):
    await _maybe_close_async(self._translator_cache)
    await _maybe_close_async(self.corpus_adapter)
```

**Thread Safety of close():**  
The `close()` and `aclose()` methods MUST be thread-safe and idempotent. If called concurrently from multiple threads, the cleanup must happen exactly once, and subsequent calls must have no effect. Implementations SHOULD use a lock to guard the cleanup logic and mark the instance as closed before releasing the lock.

### 4.8. Event Loop Guards (MUST)

All sync methods MUST prevent execution inside running event loops:

```python
def _ensure_not_in_event_loop(sync_api_name, async_alternative=None):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return
    suggestion = f"Use async variant: {async_alternative}" if async_alternative else ""
    raise RuntimeError(f"{sync_api_name} called from event loop. {suggestion}")
```

### 4.9. Dimension Management (SHOULD)

Adapters SHOULD track embedding dimension on first successful embed:

```python
def _update_dim_hint(self, dim):
    if dim is None or self._embedding_dim_hint is not None:
        return
    with self._lock:
        if self._embedding_dim_hint is None:
            self._embedding_dim_hint = dim
```

For adapters that require known dimensions (LlamaIndex, Semantic Kernel), callers MUST provide `embedding_dimension` if the underlying adapter lacks `get_embedding_dimension()`.

### 4.10. Batch Processing Semantics (MUST)

Batch operations MUST:

1. Return empty list for empty input
2. Validate all items are strings when `strict_text_types=True`
3. Warn on extremely large batches (configurable threshold)
4. Preserve input order in output
5. Handle partial failures according to §6.5

**Default and Maximum Batch Sizes (Normative):**  
- Adapters SHOULD log a warning when a batch exceeds `DEFAULT_BATCH_WARN_THRESHOLD = 1000` items.
- Adapters MUST enforce a maximum batch size of `MAX_BATCH_SIZE = 10000` items, unless explicitly overridden by configuration (with appropriate warnings). Exceeding this limit MUST result in a `ValueError`.

```python
if not texts_list:
    return []

if self.strict_text_types:
    _validate_texts_are_strings(texts_list, op_name="embed_documents")

self._warn_if_extreme_batch(texts_list, op_name="embed_documents")
if len(texts_list) > self.max_batch_size:
    raise ValueError(f"Batch size {len(texts_list)} exceeds maximum {self.max_batch_size}")
```

### 4.11. Empty Text Handling (MUST)

Single-text operations on empty or whitespace-only strings MUST return zero vectors of the correct dimension:

```python
def _handle_empty_text(self, text):
    dim = self.embedding_dimension
    logger.warning("Empty text, returning zero vector (dim=%d)", dim)
    return [0.0] * dim
```

Batch operations in lenient mode (`strict_text_types=False`) MUST insert zero vectors for non-string or empty items to preserve row alignment.

**Note:** Zero vectors are only allowed for empty texts. If an embedding result from the underlying adapter contains NaN or Inf, it MUST be treated as a coercion failure (see §4.5) and an error raised.

### 4.12. SIEM-Safe Observability (MUST)

All logging MUST:

- Never log raw text, vectors, or tenant identifiers
- Use `_safe_snapshot()` to truncate long strings and limit container sizes
- Include `tenant_hash` instead of raw tenant
- Log operation completion with dimensions and latency

**`_safe_snapshot` thresholds (Normative):**  
Implementations MUST use at least the following truncation limits:
- Strings longer than `MAX_STRING_LENGTH = 5000` characters MUST be truncated to that length.
- Containers (lists, dicts) with more than `MAX_CONTAINER_ITEMS = 200` items MUST be limited to that many items (with an indication of truncation).  
These are minimum requirements; implementations MAY use stricter limits.

```python
logger.debug(
    "Batch embedding completed: docs=%d dim=%s latency_ms=%.2f",
    len(mat), dim, elapsed_ms
)
```

### 4.13. Testing Accommodations (INFORMATIVE)

Adapters SHOULD support test injection:

- Translator can be monkeypatched via `_translator` setter
- Context building can be overridden in test subclasses
- Dimension hints are observable via `_embedding_dim_hint`
- Error codes are exposed for assertion

### 4.14. Adapter Lifecycle State Machine (MUST)

Each adapter instance MUST maintain a clear lifecycle with the following states and transitions:

- **`UNINITIALIZED`** (initial state after `__init__`, before any lazy initialization)
- **`INITIALIZED`** (after first use, lazy resources created)
- **`CLOSED`** (after `close()` or `aclose()` is called)

**Valid Transitions:**
- `UNINITIALIZED` → `INITIALIZED`: automatically when any embedding operation is first invoked.
- `UNINITIALIZED` → `CLOSED`: via `close()` or `aclose()`.
- `INITIALIZED` → `CLOSED`: via `close()` or `aclose()`.
- `CLOSED` → (no transitions allowed; instance is considered dead).

**Illegal States:**
- Attempting any embedding operation (including `embed_documents`, `embed_query`, their async variants, `capabilities`, `health`) after `CLOSED` MUST raise a `RuntimeError` with a message indicating the adapter is closed.
- Calling `close()` or `aclose()` multiple times is allowed and MUST be idempotent (no error, subsequent calls have no effect).
- Calling `close()` from within an async context (i.e., while an event loop is running) MUST raise `RuntimeError` unless the adapter is designed to handle that (e.g., AutoGen's Chroma bridge). In general, sync `close()` should enforce event loop guard.

**Behavior After Close:**  
- All resources (translator, underlying corpus_adapter) are released.
- The adapter instance should be considered unusable; any further method calls (except `__enter__`/`__exit__` which are part of context manager protocol) must raise.

**Partial Initialization Failure:**  
If an exception occurs during `__init__` after some resources have been allocated (e.g., a lock created but validation fails), the adapter MUST clean up any successfully allocated resources before propagating the exception. Implementations SHOULD use a try/finally block or a context manager to ensure cleanup. After a failed `__init__`, the object is considered not constructed and MUST NOT be used; no lifecycle state is defined. Callers must ensure that if `__init__` raises, the object reference is discarded.

This lifecycle ensures predictable resource management and aids in debugging.

---

## 5. Shared Utility Layer

### 5.1. Validation Utilities

```python
def _validate_texts_are_strings(texts: Sequence[Any], *, op_name: str) -> None:
    """Reject non-string items with clear TypeError messages."""
    for i, t in enumerate(texts):
        if not isinstance(t, str):
            raise TypeError(f"{op_name} expects Sequence[str]; item {i} is {type(t).__name__}")
```

### 5.2. Snapshot Utilities

```python
def _safe_snapshot(value: Any, *, max_items: int = 200, max_str: int = 5000) -> Any:
    """
    Convert any value to a safe-to-log snapshot:
    - Truncates long strings
    - Limits container sizes
    - Falls back to repr() for unknown objects
    """
    # Implementation details in each adapter
    # Must respect normative thresholds (max_items >= 200, max_str >= 5000)
```

### 5.3. Operation Context Detection

```python
def _looks_like_operation_context(obj: Any) -> bool:
    """Structural check for OperationContext-like objects."""
    if obj is None:
        return False
    try:
        if isinstance(obj, OperationContext):
            return True
    except TypeError:
        pass
    return any(hasattr(obj, attr) for attr in (
        "request_id", "idempotency_key", "deadline_ms", "traceparent"
    ))
```

### 5.4. Coercion Error Codes

```python
class CoercionErrorCodes:
    invalid_result: str
    empty_result: str
    conversion_error: str
    framework_label: str

# Each adapter defines:
EMBEDDING_COERCION_ERROR_CODES = CoercionErrorCodes(
    invalid_result="INVALID_EMBEDDING_RESULT",
    empty_result="EMPTY_EMBEDDING_RESULT",
    conversion_error="EMBEDDING_CONVERSION_ERROR",
    framework_label="autogen",  # framework-specific
)
```

### 5.5. Resource Cleanup Helpers

```python
def _maybe_close_sync(obj: Any) -> None:
    """Best-effort sync cleanup with priority: aclose() → close()."""
    # Implementation handles coroutines via asyncio.run()

async def _maybe_close_async(obj: Any) -> None:
    """Best-effort async cleanup with priority: aclose() → close()."""
    # Implementation offloads sync close to thread pool
```

---

## 6. Cross-Adapter Patterns

### 6.1. Unified Error Taxonomy Integration

All adapters map framework-specific exceptions to the Corpus error taxonomy:

```python
try:
    result = await self._translator.arun_embed(...)
except BadRequest as e:
    if e.code == "TEXT_TOO_LONG":
        # Map to framework-appropriate exception
        raise TextTooLongError(...) from e
    raise
except Exception as e:
    attach_context(e, framework=self._framework_name, ...)
    raise
```

### 6.2. Consistent Observability

All adapters emit:
- One `observe` metric per operation (including streaming)
- Structured logs with `tenant_hash`, operation, latency, dimensions
- Distributed trace context via `traceparent`

### 6.3. Operation Context Propagation

Framework-specific context flows into `OperationContext` via translation helpers:

```
framework_context → context_from_framework() → OperationContext
```

### 6.4. Idempotency Semantics

When `idempotency_key` is provided in operation context, adapters MUST ensure exactly-once semantics for mutating operations (embeddings are read-only, so idempotency applies to token counting and health checks where supported).

### 6.5. Partial Failure Reporting

Batch operations MAY experience partial failures (e.g., some texts succeed, some fail). The adapter MUST handle these according to the following rules:

- If the underlying translator returns a structured result containing partial failures (as defined in the Corpus Embedding Protocol), the adapter MUST:
  - Return the embeddings for the successful items, and insert zero vectors for the failed items (to preserve row alignment).
  - Log each failure with sufficient detail (index, error code, message) using the observability system.
  - Not raise an exception unless all items fail (in which case an exception summarizing the failures SHOULD be raised).

- The JSON structure shown in the example is for observability/logging only; it is NOT the return type of the embedding methods. Embedding methods return a list of vectors (or raise an exception). The observability layer may capture the partial failure details and include them in logs/metrics.

```json
// Example log entry for partial failure (observability)
{
  "ok": true,
  "code": "OK",
  "ms": 38.4,
  "result": {
    "processed_count": 2,
    "failed_count": 1,
    "failures": [
      {
        "index": 2,
        "error": "TEXT_TOO_LONG",
        "detail": "Input exceeds max_text_length"
      }
    ],
    "embeddings": [...]   // not logged, but present in return value
  }
}
```

### 6.6. Backpressure Integration

Adapters SHOULD:
- Surface `ResourceExhausted` with `retry_after_ms` when rate-limited
- Include `throttle_scope` in error details
- Propagate backpressure hints from underlying provider

### 6.7. Embedding Determinism (MUST)

All adapters MUST produce the same embedding vectors for the same input text and model, within a defined tolerance, **regardless of which framework adapter is used**. This ensures that applications can switch frameworks without changing retrieval behavior.

- **Floating point tolerance:** For the same input text and model, the output vectors from different adapters (or the same adapter across calls) MUST be equal to within **1e-6** in each component (absolute difference ≤ 1e-6).
- **Normalization equivalence:** If the underlying model produces normalized embeddings, all adapters MUST preserve that normalization. If the model does not normalize, adapters MUST NOT introduce normalization unless explicitly configured to do so (and then it must be consistent across all adapters).
- **Determinism under identical conditions:** Repeated calls with the same input and same configuration (model, tenant, etc.) MUST produce bitwise‑identical results, unless the underlying provider is non‑deterministic (in which case this requirement is waived but MUST be documented).

**Documentation Requirement for Non‑Deterministic Providers:**  
If the underlying embedding provider is known to be non‑deterministic (e.g., due to random seeds, hardware fluctuations, or load‑balancing across different model instances), the adapter MUST include a clear statement in its public documentation (e.g., in the class docstring or a separate documentation page) that explains:
- The name of the provider and the source of non‑determinism.
- Whether the non‑determinism affects the embedding vectors or only metadata (e.g., timing).
- Any configuration options that can mitigate non‑determinism (e.g., fixing a random seed, pinning to a specific model replica).
- The practical impact on applications (e.g., retrieval may vary slightly between runs).

This documentation ensures that users are aware of potential variability and can make informed decisions.

### 6.8. Translator Shim Equivalence (MUST)

Some adapters (e.g., LlamaIndex, Semantic Kernel) use a `_TranslatorAdapterShim` to accommodate underlying corpus adapters that may not support the full EmbedSpec interface. The shim MUST ensure that the observable behavior (the embeddings returned) is **equivalent** regardless of which signature the underlying adapter implements.

Specifically:

- If the underlying adapter implements `embed(texts: Sequence[str], ...)` (raw text mode), the shim MUST correctly extract the raw texts from the EmbedSpec and call the underlying adapter with those texts.
- If the underlying adapter implements `embed(spec: EmbedSpec, ctx=None, ...)` (full mode), the shim MUST pass the spec through unchanged.
- In both cases, for the same input texts and operation context, the resulting embeddings MUST be identical (within the tolerance defined in §6.7).

This requirement ensures that users can mix and match adapters without behavioral surprises. The conformance test suite includes tests that verify equivalence using a mock adapter that supports both modes.

---

## 7. AutoGen Adapter Specification

### 7.1. Overview

The AutoGen adapter exposes Corpus embeddings as Chroma-compatible `embedding_function` callables and integrates with AutoGen's `autogen_ext.memory.chromadb` for vector memory. It solves the fundamental impedance mismatch between Chroma's synchronous callback expectation and AutoGen's async execution model.

### 7.2. Framework-Specific Challenges

| Challenge | Solution |
|-----------|----------|
| Chroma calls sync `__call__` from async event loop | `_allow_chromadb_in_event_loop` flag with thread-pool bridge |
| Chroma probes adapter class for `name()`, `get_config()` | Static compatibility methods returning stable values |
| AutoGen batch memory `add()` raises `AttributeError` instead of `TypeError` | `_AutoGenChromaMemoryCompatWrapper` normalizes exception |
| Context translation must preserve agent/conversation IDs | Extract `agent_name`, `conversation_id`, `workflow_type`, `retriever_name` |

### 7.3. Data Types

```python
class AutoGenContext(TypedDict, total=False):
    agent_name: Optional[str]
    conversation_id: Optional[str]
    workflow_type: Optional[str]
    retriever_name: Optional[str]
    request_id: Optional[str]
    user_id: Optional[str]

class AutoGenMemory(Protocol):
    async def add(self, *args, **kwargs): ...
    async def query(self, *args, **kwargs): ...
    async def close(self, *args, **kwargs): ...
```

### 7.4. Core Class: `CorpusAutoGenEmbeddings`

#### 7.4.1. Chroma Compatibility Surface

```python
@staticmethod
def name() -> str:
    return "corpus-autogen-embeddings"

@staticmethod
def is_legacy() -> bool:
    return False

@staticmethod
def default_space() -> str:
    return "cosine"

@staticmethod
def supported_spaces() -> List[str]:
    return ["cosine", "l2", "ip"]

@staticmethod
def get_config() -> Dict[str, Any]:
    return {
        "name": "corpus-autogen-embeddings",
        "framework": "autogen",
        "default_space": "cosine",
        "supported_spaces": ["cosine", "l2", "ip"],
        "is_legacy": False,
    }
```

#### 7.4.2. Initialization

```python
def __init__(
    self,
    corpus_adapter: EmbeddingProtocolV1,
    model: Optional[str] = None,
    batch_config: Optional[BatchConfig] = None,
    text_normalization_config: Optional[TextNormalizationConfig] = None,
    autogen_config: Optional[Dict[str, Any]] = None,
    framework_version: Optional[str] = None,
    *,
    _allow_chromadb_in_event_loop: bool = False,
):
    # Validate corpus_adapter has embed method
    # Store configuration
    # Initialize thread lock for translator
    # Set _allow_chromadb_in_event_loop flag
```

#### 7.4.3. Sync/Async Bridge

The adapter uses a module‑level thread pool for Chroma compatibility:

```python
_CHROMA_BRIDGE_EXECUTOR = ThreadPoolExecutor(max_workers=4)

def _run_blocking_in_chroma_bridge_thread(fn: Callable[[], T]) -> T:
    return _CHROMA_BRIDGE_EXECUTOR.submit(fn).result()
```

**Thread Pool Lifecycle and Constraints:**  
- The thread pool is a module‑level singleton shared by all AutoGen adapter instances.  
- It MUST be created as a **daemon** thread pool (`daemon=True`) so that it does not block interpreter shutdown.  
- The pool MUST have a bounded work queue with a configurable maximum size (default 1000). If the queue is full, submitting a new task MUST block or raise an exception (implementations MAY use a `Queue` with `maxsize` and a timeout).  
- On interpreter exit, daemon threads are abruptly terminated; this is acceptable because the pool only runs short‑lived embedding tasks, and abrupt termination will not leak resources (the underlying translator calls are expected to handle cancellation).  
- No explicit shutdown of the pool is required, but implementations MAY register an `atexit` handler to attempt graceful shutdown (non‑normative).

**Normative constraints on `_allow_chromadb_in_event_loop`:**  
- This flag MUST default to `False`.  
- It MUST only be used to enable Chroma compatibility; it MUST NOT be used to circumvent event loop guards for other operations (e.g., direct calls to `embed_documents`).  
- When `True`, the adapter's `__call__` method (the Chroma embedding function) MAY run synchronously inside an event loop by delegating to the thread pool.  
- The adapter MUST still enforce event loop guards for all other sync methods (`embed_documents`, `embed_query`, `close`).  
- Setting this flag to `True` when Chroma is not in use is NOT RECOMMENDED, as it may hide deadlocks.

#### 7.4.4. Operations

```python
@with_embedding_error_context("function_call")
def __call__(self, input: Sequence[str]) -> List[List[float]]:
    """Chroma embedding function interface."""
    if not _is_running_event_loop():
        return self.embed_documents(list(input))
    
    if not self._allow_chromadb_in_event_loop:
        _ensure_not_in_event_loop("__call__")
    
    # Run in thread pool
    return _run_blocking_in_chroma_bridge_thread(lambda: self.embed_documents(list(input)))

@with_embedding_error_context("documents")
def embed_documents(self, texts, *, autogen_context=None, model=None):
    _ensure_not_in_event_loop("embed_documents")
    # Implementation with translator

@with_embedding_error_context("query")  
def embed_query(self, text, *, input=None, autogen_context=None, model=None):
    # Handles both single text and legacy batch modes
```

### 7.5. Integration Helpers

#### 7.5.1. `create_vector_memory()`

```python
def create_vector_memory(
    corpus_adapter: EmbeddingProtocolV1,
    *,
    collection_name: str = "corpus_autogen_memory",
    persistence_path: Optional[str] = None,
    model: Optional[str] = None,
    batch_config: Optional[BatchConfig] = None,
    text_normalization_config: Optional[TextNormalizationConfig] = None,
    autogen_config: Optional[Dict[str, Any]] = None,
    framework_version: Optional[str] = None,
    k: int = 3,
    score_threshold: Optional[float] = None,
) -> AutoGenMemory:
    """Create AutoGen ChromaDB vector memory with Corpus embeddings."""
    # Lazily import autogen_ext
    # Configure embedding function with _allow_chromadb_in_event_loop=True
    # Return wrapped memory for exception normalization
```

#### 7.5.2. `register_embeddings()`

```python
def register_embeddings(...) -> CorpusAutoGenEmbeddings:
    """Convenience constructor for reusable embedding function."""
```

### 7.6. Error Codes

```python
class ErrorCodes:
    INVALID_EMBEDDING_RESULT = "INVALID_EMBEDDING_RESULT"
    EMPTY_EMBEDDING_RESULT = "EMPTY_EMBEDDING_RESULT"
    EMBEDDING_CONVERSION_ERROR = "EMBEDDING_CONVERSION_ERROR"
    AUTOGEN_CONTEXT_INVALID = "AUTOGEN_CONTEXT_INVALID"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
```

### 7.7. AutoGen-Specific Context

The adapter extracts these fields from `autogen_context`:
- `agent_name` — Current agent identifier
- `conversation_id` — Active conversation
- `workflow_type` — Type of agent workflow
- `retriever_name` — Name of retriever component

Unknown keys are ignored (per §4.4).

---

## 8. CrewAI Adapter Specification

### 8.1. Overview

The CrewAI adapter implements the embedder protocol expected by CrewAI agents, enabling Corpus embeddings in role-based agent teams. It solves the problem of context propagation across agents that operate without a shared runtime.

### 8.2. Framework-Specific Challenges

| Challenge | Solution |
|-----------|----------|
| No shared runtime context across agents | Extract context from per-call `crewai_context` |
| Agents may be created before embedder is available | `register_with_crewai()` auto-attaches to existing agents |
| Non-mapping context types must be rejected | Raise `ValueError` for invalid types (test requirement) |
| Empty batch returns empty list | Early return for empty inputs |

### 8.3. Data Types

```python
class CrewAIContext(TypedDict, total=False):
    agent_role: Optional[str]
    task_id: Optional[str]
    workflow: Optional[str]
    agent_id: Optional[str]
    crew_id: Optional[str]
    process_id: Optional[str]

class CrewAIConfig(TypedDict, total=False):
    fallback_to_simple_context: bool
    enable_agent_context_propagation: bool
    task_aware_batching: bool

class CrewAIEmbedder(Protocol):
    def embed_documents(self, texts, *, crewai_context=None, model=None, **kwargs): ...
    def embed_query(self, text, *, crewai_context=None, model=None, **kwargs): ...
    async def aembed_documents(self, texts, *, crewai_context=None, model=None, **kwargs): ...
    async def aembed_query(self, text, *, crewai_context=None, model=None, **kwargs): ...
```

### 8.4. Core Class: `CorpusCrewAIEmbeddings`

#### 8.4.1. Initialization

```python
def __init__(
    self,
    corpus_adapter: EmbeddingProtocolV1,
    model: Optional[str] = None,
    batch_config: Optional[BatchConfig] = None,
    text_normalization_config: Optional[TextNormalizationConfig] = None,
    crewai_config: Optional[CrewAIConfig] = None,
    framework_version: Optional[str] = None,
):
    # Validate corpus_adapter
    # Normalize crewai_config with defaults
    # Initialize thread lock and dimension hint
```

#### 8.4.2. Operations

```python
@with_embedding_error_context("documents")
def embed_documents(self, texts, *, crewai_context=None, model=None, **kwargs):
    _ensure_not_in_event_loop("embed_documents")
    
    if not texts:
        return []
    
    _validate_texts_are_strings(list(texts), op_name="embed_documents")
    self._warn_if_extreme_batch(texts, op_name="embed_documents")
    
    core_ctx, framework_ctx = self._build_contexts(
        crewai_context=crewai_context,
        model=model,
        **kwargs
    )
    
    translated = self._translator.embed(
        raw_texts=list(texts),
        op_ctx=core_ctx,
        framework_ctx=framework_ctx,
    )
    
    return self._coerce_embedding_matrix(translated)

@with_embedding_error_context("query")
def embed_query(self, text, *, crewai_context=None, model=None, **kwargs):
    _ensure_not_in_event_loop("embed_query")
    
    if not isinstance(text, str):
        raise TypeError(f"embed_query expects str; got {type(text).__name__}")
    
    core_ctx, framework_ctx = self._build_contexts(...)
    translated = self._translator.embed(raw_texts=text, ...)
    return self._coerce_embedding_vector(translated)
```

### 8.5. Integration Helpers

#### 8.5.1. `create_embedder()`

```python
def create_embedder(
    corpus_adapter: EmbeddingProtocolV1,
    model: Optional[str] = None,
    *,
    framework_version: Optional[str] = None,
    **kwargs,
) -> CrewAIEmbedder:
    """Create a CrewAI-compatible embedder for manual agent assignment."""
```

#### 8.5.2. `register_with_crewai()`

```python
def register_with_crewai(
    crew: Any,
    corpus_adapter: EmbeddingProtocolV1,
    model: Optional[str] = None,
    *,
    framework_version: Optional[str] = None,
    **kwargs,
) -> CorpusCrewAIEmbeddings:
    """
    Register embeddings with a CrewAI Crew instance.
    
    - Creates embedder instance
    - Attempts to attach to all agents in crew.agents
    - Logs warnings if crew structure is unexpected
    """
    embedder = CorpusCrewAIEmbeddings(...)
    
    agents = getattr(crew, "agents", [])
    for agent in agents:
        if hasattr(agent, "embedder"):
            agent.embedder = embedder
    
    return embedder
```

### 8.6. Error Codes

```python
class ErrorCodes:
    INVALID_EMBEDDING_RESULT = "INVALID_EMBEDDING_RESULT"
    EMPTY_EMBEDDING_RESULT = "EMPTY_EMBEDDING_RESULT"
    EMBEDDING_CONVERSION_ERROR = "EMBEDDING_CONVERSION_ERROR"
    CREWAI_CONTEXT_INVALID = "CREWAI_CONTEXT_INVALID"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
```

### 8.7. CrewAI-Specific Context

The adapter extracts:
- `agent_role` — Role of the current agent
- `task_id` — Current task identifier
- `workflow` — Workflow name
- `agent_id` — Agent instance identifier
- `crew_id` — Crew identifier
- `process_id` — Process identifier

When `task_aware_batching=True`, batch strategies include task ID in framework context. Unknown keys are ignored.

---

## 9. LangChain Adapter Specification

### 9.1. Overview

The LangChain adapter implements `langchain_core.embeddings.Embeddings` with comprehensive event-loop safety and Pydantic v2 compatibility. It solves the production problem of sync embedding methods being called from async contexts.

### 9.2. Framework-Specific Challenges

| Challenge | Solution |
|-----------|----------|
| Sync methods called from async event loops | Detect event loop and run in worker thread |
| Pydantic v2 rejects undeclared attributes | Use `PrivateAttr` and `model_config["extra"] = "allow"` |
| Empty string queries must return zero vectors | Dimension-aware empty handling |
| Unknown config keys must be rejected | Strict validation in `langchain_config` |
| LangChain may not be installed | Lazy imports with fallback stubs |

### 9.3. Data Types

```python
class LangChainConfig(TypedDict, total=False):
    configurable: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    callbacks: Optional[Any]
    run_name: Optional[str]
    run_id: Optional[str]

class LangChainAdapterConfig(TypedDict, total=False):
    fallback_to_simple_context: bool
    enable_operation_context_propagation: bool
```

### 9.4. Core Class: `CorpusLangChainEmbeddings`

#### 9.4.1. Pydantic Integration

```python
class CorpusLangChainEmbeddings(BaseModel, Embeddings):
    corpus_adapter: Any
    model: Optional[str] = None
    framework_version: Optional[str] = None
    batch_config: Optional[BatchConfig] = None
    text_normalization_config: Optional[TextNormalizationConfig] = None
    langchain_config: LangChainAdapterConfig = {}
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    _translator_cache: Optional[Any] = PrivateAttr(default=None)
    _translator_lock: threading.Lock = PrivateAttr(default_factory=threading.Lock)
    _embedding_dim_hint: Optional[int] = PrivateAttr(default=None)
```

#### 9.4.2. Initialization

```python
@field_validator("corpus_adapter")
def validate_corpus_adapter(cls, v):
    if not hasattr(v, "embed") or not callable(getattr(v, "embed", None)):
        raise ValueError("corpus_adapter must implement 'embed' method")
    return v

@field_validator("langchain_config", mode="before")
def validate_langchain_config(cls, v):
    # Reject unknown keys
    allowed = {"fallback_to_simple_context", "enable_operation_context_propagation"}
    unknown = set(dict(v).keys()) - allowed
    if unknown:
        raise ValueError(f"Unknown keys: {sorted(unknown)}")
    # Set defaults
    return {
        "fallback_to_simple_context": bool(v.get("fallback_to_simple_context", False)),
        "enable_operation_context_propagation": bool(v.get("enable_operation_context_propagation", True)),
    }
```

#### 9.4.3. Event Loop Safety

```python
def _run_in_worker_thread(fn: Callable[[], T]) -> T:
    """Run sync function in worker thread when called from event loop."""
    with ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(fn).result()

def embed_documents(self, texts, *, config=None, model=None, **kwargs):
    def _do_call():
        # Normal embedding logic
        return result
    
    try:
        _ensure_not_in_event_loop("embed_documents")
        return _do_call()
    except Exception:
        return _run_in_worker_thread(_do_call)
```

#### 9.4.4. Operations

```python
@with_embedding_error_context("documents")
def embed_documents(self, texts, *, config=None, model=None, **kwargs):
    # Implementation with worker thread fallback

@with_embedding_error_context("query")
def embed_query(self, text, *, config=None, model=None, **kwargs):
    # Empty string handling with dimension probe

@with_async_embedding_error_context("documents")
async def aembed_documents(self, texts, *, config=None, model=None, **kwargs):
    # Async implementation

@with_async_embedding_error_context("query")
async def aembed_query(self, text, *, config=None, model=None, **kwargs):
    # Async implementation with empty string handling
```

### 9.5. Integration Helpers

#### 9.5.1. `configure_langchain_embeddings()`

```python
def configure_langchain_embeddings(
    corpus_adapter: Any,
    model: Optional[str] = None,
    framework_version: Optional[str] = None,
    langchain_config: Optional[LangChainAdapterConfig] = None,
    **kwargs,
) -> CorpusLangChainEmbeddings:
    """Configure and return Corpus embeddings for LangChain usage."""
```

#### 9.5.2. `register_with_langchain()`

```python
def register_with_langchain(...) -> CorpusLangChainEmbeddings:
    """Alias for configure_langchain_embeddings for API symmetry."""
```

### 9.6. Error Codes

```python
class ErrorCodes:
    INVALID_EMBEDDING_RESULT = "INVALID_EMBEDDING_RESULT"
    EMPTY_EMBEDDING_RESULT = "EMPTY_EMBEDDING_RESULT"
    EMBEDDING_CONVERSION_ERROR = "EMBEDDING_CONVERSION_ERROR"
    LANGCHAIN_CONFIG_INVALID = "LANGCHAIN_CONFIG_INVALID"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
```

### 9.7. LangChain-Specific Context

The adapter extracts from `config`:
- `run_id` — LangChain run identifier
- `run_name` — Run name
- `tags` — Snapshotted for observability
- `metadata` — Snapshotted for observability
- `configurable` — Snapshotted for observability

Unknown keys are ignored.

---

## 10. LlamaIndex Adapter Specification

### 10.1. Overview

The LlamaIndex adapter implements `llama_index.core.embeddings.BaseEmbedding` with correct Pydantic initialization order and robust handling of mixed-type batches. It solves the critical problem of attribute assignment before Pydantic internals are initialized.

### 10.2. Framework-Specific Challenges

| Challenge | Solution |
|-----------|----------|
| Pydantic `__setattr__` fails before `__pydantic_extra__` exists | Call `super().__init__` first, then `object.__setattr__` |
| LlamaIndex may pass non-Mapping context | Defensive filtering with warnings |
| Adapters may implement simple `embed(texts)` without EmbedSpec | `_TranslatorAdapterShim` adapts signatures (see §6.8) |
| Batch operations must handle non-string items with row alignment | `strict_text_types=False` inserts zero vectors |
| Global `Settings.embed_model` registration may fail | Best-effort registration with graceful fallback |

### 10.3. Data Types

```python
class LlamaIndexContext(TypedDict, total=False):
    node_ids: Optional[List[str]]
    index_id: Optional[str]
    callback_manager: Optional[Any]
    trace_id: Optional[str]
    workflow: Optional[str]

class LlamaIndexAdapterConfig(TypedDict, total=False):
    enable_operation_context_propagation: bool
    strict_text_types: bool
    max_node_ids_in_context: int
```

### 10.4. Core Class: `CorpusLlamaIndexEmbeddings`

#### 10.4.1. Pydantic Initialization Order (CRITICAL)

```python
def __init__(
    self,
    corpus_adapter: EmbeddingProtocolV1,
    model_name: str = "corpus-embedding-protocol",
    batch_config: Optional[BatchConfig] = None,
    text_normalization_config: Optional[TextNormalizationConfig] = None,
    callback_manager: Optional[CallbackManager] = None,
    embed_batch_size: int = DEFAULT_EMBED_BATCH_SIZE,
    *,
    llamaindex_config: Optional[LlamaIndexAdapterConfig] = None,
    embedding_dimension: Optional[int] = None,
    **kwargs: Any,
):
    # 1. Validate inputs using local variables (no self mutation)
    if not hasattr(corpus_adapter, "embed"):
        raise TypeError("corpus_adapter must implement 'embed'")
    
    # 2. Call super().__init__ FIRST (Pydantic internals initialized)
    super().__init__(
        model_name=model_name,
        embed_batch_size=embed_batch_size,
        callback_manager=callback_manager,
        **kwargs,
    )
    
    # 3. Use object.__setattr__ to attach runtime state
    object.__setattr__(self, "corpus_adapter", corpus_adapter)
    object.__setattr__(self, "_translator_adapter", _TranslatorAdapterShim(corpus_adapter))  # see §6.8
    object.__setattr__(self, "batch_config", batch_config)
    object.__setattr__(self, "text_normalization_config", text_normalization_config)
    object.__setattr__(self, "llamaindex_config", normalized_config)
    object.__setattr__(self, "_translator_lock", threading.Lock())
    object.__setattr__(self, "_embedding_dim_hint", None)
```

#### 10.4.2. Translator Shim Pattern

The `_TranslatorAdapterShim` ensures equivalence as defined in §6.8.

#### 10.4.3. Initialization Validation

```python
# Enforce known embedding dimension
if (not hasattr(corpus_adapter, "get_embedding_dimension")) and (embedding_dimension is None):
    raise ValueError(
        "Embedding dimension unknown. Implement get_embedding_dimension() "
        "or pass embedding_dimension=..."
    )
```

#### 10.4.4. Operations

```python
@with_embedding_error_context("texts")
def _get_text_embeddings(self, texts: Sequence[Any], **kwargs) -> List[List[float]]:
    _ensure_not_in_event_loop("_get_text_embeddings")
    context = _filter_llamaindex_context_from_kwargs(kwargs)
    return self._embed_text_batch(texts, context)

def _embed_text_batch(self, texts, llamaindex_context):
    texts_list = list(texts)
    
    if self.llamaindex_config["strict_text_types"]:
        _validate_texts_are_strings(texts_list, op_name="_get_text_embeddings")
    
    # Split into empty and non-empty
    non_empty = [t for t in texts_list if isinstance(t, str) and t.strip()]
    empty_indices = [i for i, t in enumerate(texts_list) if not isinstance(t, str) or not t.strip()]
    
    if not non_empty:
        dim = self.embedding_dimension
        return [[0.0] * dim for _ in texts_list]
    
    # Embed non-empty texts
    core_ctx, framework_ctx = self._build_contexts(llamaindex_context=llamaindex_context)
    translated = self._translator.embed(raw_texts=non_empty, op_ctx=core_ctx, framework_ctx=framework_ctx)
    embeddings = self._coerce_embedding_matrix(translated)
    
    # Re-insert zero rows for empty indices
    if empty_indices:
        result = []
        non_empty_idx = 0
        for i in range(len(texts_list)):
            if i in set(empty_indices):
                result.append([0.0] * self.embedding_dimension)
            else:
                result.append(embeddings[non_empty_idx])
                non_empty_idx += 1
        return result
    
    return embeddings
```

### 10.5. Integration Helpers

#### 10.5.1. `configure_llamaindex_embeddings()`

```python
def configure_llamaindex_embeddings(
    corpus_adapter: EmbeddingProtocolV1,
    model_name: str = "corpus-embedding-protocol",
    llamaindex_config: Optional[LlamaIndexAdapterConfig] = None,
    **kwargs,
) -> CorpusLlamaIndexEmbeddings:
    """
    Configure and optionally register embeddings with LlamaIndex.
    
    - Always returns embeddings instance
    - Attempts to set Settings.embed_model if LlamaIndex installed
    """
    embeddings = CorpusLlamaIndexEmbeddings(...)
    
    try:
        from llama_index.core import Settings
        Settings.embed_model = embeddings
    except Exception:
        logger.warning("Failed to register with Settings")
    
    return embeddings
```

#### 10.5.2. `register_with_llamaindex()`

```python
def register_with_llamaindex(...) -> CorpusLlamaIndexEmbeddings:
    """Alias for configure_llamaindex_embeddings."""
```

### 10.6. Error Codes

```python
class ErrorCodes:
    INVALID_EMBEDDING_RESULT = "INVALID_EMBEDDING_RESULT"
    EMPTY_EMBEDDING_RESULT = "EMPTY_EMBEDDING_RESULT"
    EMBEDDING_CONVERSION_ERROR = "EMBEDDING_CONVERSION_ERROR"
    LLAMAINDEX_CONTEXT_INVALID = "LLAMAINDEX_CONTEXT_INVALID"
    LLAMAINDEX_CONFIG_INVALID = "LLAMAINDEX_CONFIG_INVALID"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
```

### 10.7. LlamaIndex-Specific Context

The adapter extracts:
- `node_ids` — IDs of nodes being embedded (bounded to `max_node_ids_in_context`)
- `node_count` — Total number of nodes
- `index_id` — Index identifier
- `trace_id` — Tracing identifier
- `workflow` — Workflow name
- `has_callback_manager` — Boolean flag

Unknown keys are ignored.

---

## 11. Semantic Kernel Adapter Specification

### 11.1. Overview

The Semantic Kernel adapter implements `semantic_kernel.connectors.ai.embeddings.EmbeddingGeneratorBase` with direct translator detection for plain-text adapters and multiple registration paths for different SK versions.

### 11.2. Framework-Specific Challenges

| Challenge | Solution |
|-----------|----------|
| Pydantic base class rejects undeclared attributes | `object.__setattr__` after `super().__init__` |
| Simple adapters choke on EmbedSpec objects | Detect plain-text mode, use `_DirectEmbeddingTranslator` (ensuring equivalence per §6.8) |
| Tests call sync aliases from async contexts | `_run_coroutine_in_new_thread()` bridge |
| Multiple registration APIs across versions | Try `add_service`, fall back to `register_embedding_generation` |
| `ai_model_id` and `service_id` required in modern SK | Pass through with defaults |

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

class SemanticKernelAdapterConfig(TypedDict, total=False):
    enable_operation_context_propagation: bool
    strict_text_types: bool
    max_items_in_context: int
```

### 11.4. Core Class: `CorpusSemanticKernelEmbeddings`

#### 11.4.1. Direct Translator Detection

```python
def _adapter_prefers_direct_text_mode(adapter: Any) -> bool:
    """
    Detect if adapter.embed expects raw texts (Sequence[str]) rather than EmbedSpec.
    
    Checks first non-self parameter name for text-related keywords.
    """
    try:
        sig = inspect.signature(getattr(adapter, "embed"))
        params = list(sig.parameters.values())
        if params and params[0].name == "self":
            params = params[1:]
        if not params:
            return False
        first = params[0]
        name = (first.name or "").lower()
        return name in ("texts", "text", "documents", "inputs", "strings")
    except Exception:
        # Detection failure: fall back to assuming full EmbedSpec mode.
        return False
```

**Detection Failure Fallback:**  
If detection fails (e.g., due to `*args`, compiled extensions, or wrapped functions), the adapter MUST assume the underlying adapter expects the full EmbedSpec interface. Implementations MAY provide an explicit configuration flag (e.g., `force_direct_mode`) to override the heuristic when needed.

#### 11.4.2. Initialization

```python
def __init__(
    self,
    corpus_adapter: EmbeddingProtocolV1,
    model_id: Optional[str] = None,
    batch_config: Optional[BatchConfig] = None,
    text_normalization_config: Optional[TextNormalizationConfig] = None,
    *,
    embedding_dimension: Optional[int] = None,
    sk_config: Optional[Mapping[str, Any]] = None,
    **kwargs,
):
    # Validate corpus_adapter
    if corpus_adapter is None or not hasattr(corpus_adapter, "embed"):
        raise TypeError("corpus_adapter must implement 'embed'")
    
    # Handle SK base class initialization (may require ai_model_id/service_id)
    service_id = kwargs.get("service_id", "")
    try:
        super().__init__(ai_model_id=(model_id or "unknown"), service_id=service_id)
    except TypeError:
        super().__init__()  # Older SK versions
    
    # Store runtime state with object.__setattr__
    object.__setattr__(self, "corpus_adapter", corpus_adapter)
    object.__setattr__(self, "model_id", model_id)
    object.__setattr__(self, "batch_config", batch_config)
    object.__setattr__(self, "text_normalization_config", text_normalization_config)
    object.__setattr__(self, "sk_config", _normalize_sk_config(sk_config or {}))
    object.__setattr__(self, "_embedding_dimension_override", embedding_dimension)
    object.__setattr__(self, "_translator_lock", threading.Lock())
    object.__setattr__(self, "_translator_instance", None)
    object.__setattr__(self, "_embedding_dim_hint", None)
    object.__setattr__(self, "_prefer_direct_translator", 
                       _adapter_prefers_direct_text_mode(corpus_adapter))
```

#### 11.4.3. Sync Alias Bridging

```python
def _run_coroutine_in_new_thread(coro) -> Any:
    """Run async coroutine to completion in dedicated thread."""
    result = {}
    error = {}
    
    def runner():
        try:
            result["value"] = asyncio.run(coro)
        except Exception as e:
            error["exc"] = e
    
    t = threading.Thread(target=runner, daemon=True)
    t.start()
    t.join()
    
    if "exc" in error:
        raise error["exc"]
    return result["value"]

def embed_documents(self, texts, *, sk_context=None, **kwargs):
    if _is_running_in_event_loop():
        if len(texts) <= 1:
            _ensure_not_in_event_loop("embed_documents")
        return _run_coroutine_in_new_thread(
            self.aembed_documents(texts, sk_context=sk_context, **kwargs)
        )
    return self.generate_embeddings(texts, sk_context=sk_context, **kwargs)
```

#### 11.4.4. Operations

```python
@with_embedding_error_context("embedding_documents")
def generate_embeddings(self, texts, *, sk_context=None, **__):
    _ensure_not_in_event_loop("generate_embeddings")
    return self._embed_text_batch(texts, sk_context=sk_context, op_name="generate_embeddings")

@with_embedding_error_context("embedding_query")
def generate_embedding(self, text, *, sk_context=None, **__):
    _ensure_not_in_event_loop("generate_embedding")
    
    if self.sk_config["strict_text_types"]:
        _validate_text_is_string(text, op_name="generate_embedding")
    
    if not isinstance(text, str) or not text.strip():
        return self._handle_empty_text("")
    
    return self._embed_single_text(text, sk_context=sk_context)

@with_async_embedding_error_context("embedding_documents")
async def generate_embeddings_async(self, texts, *, sk_context=None, **__):
    return await self._aembed_text_batch(texts, sk_context=sk_context, op_name="generate_embeddings_async")

@with_async_embedding_error_context("embedding_query")
async def generate_embedding_async(self, text, *, sk_context=None, **__):
    if self.sk_config["strict_text_types"]:
        _validate_text_is_string(text, op_name="generate_embedding_async")
    
    if not isinstance(text, str) or not text.strip():
        return self._handle_empty_text("")
    
    return await self._aembed_single_text(text, sk_context=sk_context)
```

### 11.5. Integration Helpers

#### 11.5.1. `configure_semantic_kernel_embeddings()`

```python
def configure_semantic_kernel_embeddings(
    corpus_adapter: EmbeddingProtocolV1,
    model_id: Optional[str] = None,
    sk_config: Optional[Mapping[str, Any]] = None,
    **kwargs,
) -> CorpusSemanticKernelEmbeddings:
    """Construct and return embeddings instance."""
```

#### 11.5.2. `register_with_semantic_kernel()`

```python
def register_with_semantic_kernel(
    kernel: Any,
    corpus_adapter: EmbeddingProtocolV1,
    service_id: Optional[str] = None,
    model_id: Optional[str] = None,
    **kwargs,
) -> CorpusSemanticKernelEmbeddings:
    """
    Register embeddings as a service with Semantic Kernel.
    
    Tries:
    1. kernel.add_service(embeddings, service_id=service_id)
    2. kernel.register_embedding_generation(embeddings, service_id=service_id)
    
    If both registration attempts fail, a warning MUST be logged with details of the failure.
    The embeddings instance is still returned and can be used directly.
    """
    embeddings = CorpusSemanticKernelEmbeddings(
        corpus_adapter=corpus_adapter,
        model_id=model_id,
        service_id=service_id or "unknown",
        **kwargs,
    )
    
    registered = False
    add_service = getattr(kernel, "add_service", None)
    if callable(add_service):
        try:
            add_service(embeddings, service_id=service_id)
            registered = True
        except TypeError as e:
            logger.debug("add_service failed: %s", e)
    
    if not registered:
        reg = getattr(kernel, "register_embedding_generation", None)
        if callable(reg):
            try:
                reg(embeddings, service_id=service_id)
                registered = True
            except TypeError as e:
                logger.debug("register_embedding_generation failed: %s", e)
    
    if not registered:
        logger.warning(
            "Failed to register embeddings with Semantic Kernel kernel. "
            "The embeddings instance can still be used directly, but will not be available via the kernel's service registry."
        )
    
    return embeddings
```

### 11.6. Error Codes

```python
class ErrorCodes:
    INVALID_EMBEDDING_RESULT = "INVALID_EMBEDDING_RESULT"
    EMPTY_EMBEDDING_RESULT = "EMPTY_EMBEDDING_RESULT"
    EMBEDDING_CONVERSION_ERROR = "EMBEDDING_CONVERSION_ERROR"
    SEMANTIC_KERNEL_CONTEXT_INVALID = "SEMANTIC_KERNEL_CONTEXT_INVALID"
    SEMANTIC_KERNEL_CONFIG_INVALID = "SEMANTIC_KERNEL_CONFIG_INVALID"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
```

### 11.7. Semantic Kernel-Specific Context

The adapter extracts:
- `plugin_name` — Name of the calling plugin
- `function_name` — Name of the calling function
- `kernel_id` — Kernel identifier
- `memory_type` — Type of memory operation
- `request_id` — Request identifier
- `user_id` — User identifier
- `execution_settings` — Snapshotted for observability

Unknown keys are ignored.

---

## 12. Error Handling and Resilience

### 12.1. Error Code Mapping Table (Normative)

| Corpus Error Code | Framework Adapter Mapping | Retryable |
|-------------------|--------------------------|-----------|
| `INVALID_EMBEDDING_RESULT` | Raise `TypeError` or framework equivalent | No |
| `EMPTY_EMBEDDING_RESULT` | Raise `ValueError` with context | No |
| `EMBEDDING_CONVERSION_ERROR` | Raise `TypeError` with details | No |
| `TEXT_TOO_LONG` | Framework-specific (e.g., `BadRequest` in LangChain) | No |
| `MODEL_NOT_AVAILABLE` | `NotSupported` or `Unavailable` | Conditional |
| `DEADLINE_EXCEEDED` | Propagate with budget exhausted message | Conditional |
| `RESOURCE_EXHAUSTED` | Framework rate-limit exception with `retry_after_ms` | Yes |
| `TRANSIENT_NETWORK` | Framework network error | Yes |

### 12.2. Retry Semantics

Adapters MUST NOT retry automatically unless configured to do so. When retrying:
- Honor `retry_after_ms` if present
- Use exponential backoff with jitter
- Do not retry `BadRequest` or validation errors
- Consider per-tenant retry budgets

### 12.3. Circuit Breaking Guidance

Implementations MAY implement circuit breakers:
- Open on repeated `Unavailable` or `ResourceExhausted`
- Half-open after configured timeout
- Per-tenant, per-operation circuits RECOMMENDED

---

## 13. Observability and Monitoring

### 13.1. Metrics Taxonomy (MUST)

All adapters MUST expose:

```
embedding_operations_total{framework,operation,model,code}
embedding_latency_ms{framework,operation,model,quantile}
embedding_tokens_total{framework,model}  # when available
embedding_batch_size{framework,operation}  # histogram
```

### 13.2. Structured Logging (MUST)

```json
{
  "timestamp": "2026-02-26T10:00:00Z",
  "level": "INFO",
  "framework": "langchain",
  "operation": "embed_documents",
  "tenant_hash": "a1b2c3...",
  "trace_id": "00-4bf9...",
  "model": "text-embedding-3-large",
  "texts": 24,
  "empty_texts": 2,
  "dimensions": 1536,
  "latency_ms": 127.4,
  "code": "OK"
}
```

### 13.3. Distributed Tracing (SHOULD)

- Propagate `traceparent` from operation context
- Create spans for each embedding operation
- Include attributes: `framework`, `operation`, `model`, `batch_size`, `tenant_hash`
- Final span status matches operation outcome

---

## 14. Security Considerations

### 14.1. Tenant Isolation (MUST)

- `tenant` in operation context MUST be used for isolation
- Never log raw tenant identifiers; use `tenant_hash`
- Caches MUST key by `tenant_hash` when `cache_scope="tenant"`

### 14.2. Credential Handling (MUST)

- Credentials for underlying adapters provisioned out-of-band
- Never log, snapshot, or expose credentials in error context

### 14.3. Log Redaction (MUST)

- All logs use `_safe_snapshot()` for object serialization
- Strings >64 bytes replaced with hash + length
- No raw text, vectors, or prompts in logs

---

## 15. Performance Characteristics

### 15.1. Latency Targets (Indicative)

| Operation Type | Typical Range | Notes |
|----------------|---------------|-------|
| Single embedding | 5–50 ms | Model and provider dependent |
| Batch embedding (100 texts) | 50–500 ms | Includes batching overhead |
| Token counting | 1–5 ms | Local operation |
| Capabilities/Health | 1–10 ms | Cached where possible |

### 15.2. Concurrency Considerations

- All adapters are thread-safe for concurrent use
- Translator initialized lazily with locks
- Resource cleanup safe under concurrent access

### 15.3. Caching Strategies

- Embedding results cacheable by `(model, normalize, sha256(text))`
- Cache keys MUST include `tenant_hash`
- Respect `cache_scope` and `cache_tags` when provided
- Never cache across tenant boundaries

---

## 16. Implementation Guidelines

### 16.1. Adapter Implementation Order

1. Copy shared utilities from existing adapter
2. Implement `__init__` with validation
3. Add error context decorators
4. Implement core embedding methods
5. Add context extraction and building
6. Implement resource management (including lifecycle state)
7. Add integration helpers
8. Write conformance tests

### 16.2. Validation Requirements (MUST)

- Reject non-string inputs when `strict_text_types=True`
- Validate corpus_adapter has `embed` method
- Validate batch_config and text_normalization_config types
- Reject unknown config keys
- Enforce positive `embed_batch_size` and maximum batch size (§4.10)

### 16.3. Testing

#### 16.3.1. Conformance Test Suite

Each adapter MUST pass:
- Wire format validation
- Error normalization tests
- Coercion failure conditions (shape mismatch, non-float, NaN/Inf, dimension mismatch) — see §4.5
- Batch operation tests (including empty batches, large batches)
- Empty text handling
- Event loop guard tests
- Resource cleanup tests (including lifecycle state transitions)

#### 16.3.2. Framework-Specific Tests

- AutoGen: Chroma compatibility, exception normalization, `_allow_chromadb_in_event_loop` constraints
- CrewAI: Context extraction, crew registration
- LangChain: Pydantic validation, worker thread fallback
- LlamaIndex: Pydantic init order, strict/lenient modes, translator shim equivalence (§6.8)
- Semantic Kernel: Direct translator detection, registration paths, shim equivalence

#### 16.3.3. Cross-Adapter Tests

- All adapters produce identical embeddings for same input (within tolerance, see §6.7)
- Error codes consistent across frameworks
- Observability fields follow same patterns
- Lifecycle behavior (close, use after close) consistent

---

## 17. Versioning and Compatibility

### 17.1. Semantic Versioning (MUST)

Adapter packages MUST use Semantic Versioning:
- MAJOR: Breaking changes to public API
- MINOR: Additive, backward-compatible features
- PATCH: Bug fixes and internal improvements

### 17.2. Framework Version Compatibility

Adapters SHOULD document supported framework versions. "Tested" means that the adapter has passed the conformance test suite (as defined in §16.3) against those specific framework versions. The adapter MAY work with other versions but compatibility is not guaranteed.

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
- Corpus Embedding Protocol V1.0 Specification
- Corpus Common Foundation Specification

### 18.2. Informative References

- AutoGen Documentation: https://microsoft.github.io/autogen/
- CrewAI Documentation: https://docs.crewai.com/
- LangChain Documentation: https://python.langchain.com/
- LlamaIndex Documentation: https://docs.llamaindex.ai/
- Semantic Kernel Documentation: https://learn.microsoft.com/en-us/semantic-kernel/

---

## Appendix A — Comparison Matrix: Framework-Specific Challenges

| Framework | Primary Challenge | Adapter Solution |
|-----------|------------------|------------------|
| AutoGen | Chroma sync callback in async loop | Thread-pool bridge with opt-in flag |
| CrewAI | No shared runtime context | Per-call context extraction |
| LangChain | Sync methods called from async | Event loop detection + worker thread |
| LlamaIndex | Pydantic init order | `super().__init__` first + `object.__setattr__` |
| Semantic Kernel | Pydantic + multiple registration paths | Direct translator detection + fallback registration |

---

## Appendix B — Code Pattern Catalog (Normative)

### B.1. Pydantic Initialization Patterns

```python
# LangChain pattern (PrivateAttr)
class MyEmbeddings(BaseModel):
    _private_state: Any = PrivateAttr()
    
    def __init__(self, ...):
        super().__init__(...)
        object.__setattr__(self, "_private_state", value)

# LlamaIndex pattern (super first)
def __init__(self, ...):
    # Validate with locals
    super().__init__(...)
    object.__setattr__(self, "field", value)
```

### B.2. Event Loop Safety Patterns

```python
# Guard pattern
_ensure_not_in_event_loop("sync_method")

# Bridge pattern (controlled)
if _is_running_in_event_loop():
    return _run_in_worker_thread(sync_method)

# Async fallback pattern
try:
    return sync_method()
except Exception:
    return await asyncio.to_thread(sync_method)
```

### B.3. Resource Cleanup Patterns

```python
# Sync cleanup
def close(self):
    _ensure_not_in_event_loop("close")
    _maybe_close_sync(self._resource)

# Async cleanup
async def aclose(self):
    await _maybe_close_async(self._resource)
```

### B.4. Context Extraction Patterns

```python
# Dynamic context
def _extract_dynamic_context(self, args, kwargs, operation):
    ctx = {"model": self.model}
    if operation == "documents" and args:
        ctx["texts_count"] = len(args[0])
    return ctx
```

---

## Appendix C — End-to-End Usage Examples

### C.1. AutoGen with Chroma Memory

```python
from corpus_sdk.embedding.framework_adapters.autogen import create_vector_memory
from corpus_sdk.embedding import SomeAdapter

adapter = SomeAdapter()
memory = create_vector_memory(
    corpus_adapter=adapter,
    collection_name="my_memory",
    persistence_path="./chroma_db",
    model="text-embedding-3-large",
    k=5
)

# Use with AutoGen agent
await memory.add([...])
results = await memory.query("find similar", k=3)
```

### C.2. CrewAI Agent with Embedder

```python
from corpus_sdk.embedding.framework_adapters.crewai import create_embedder
from crewai import Agent

embedder = create_embedder(
    corpus_adapter=adapter,
    model="text-embedding-3-large"
)

agent = Agent(
    role="Researcher",
    goal="Find relevant information",
    backstory="...",
    embedder=embedder  # Manual assignment
)

# Or auto-register with crew
from corpus_sdk.embedding.framework_adapters.crewai import register_with_crewai
register_with_crewai(my_crew, adapter)
```

### C.3. LangChain Vector Store

```python
from corpus_sdk.embedding.framework_adapters.langchain import configure_langchain_embeddings
from langchain.vectorstores import Chroma

embeddings = configure_langchain_embeddings(
    corpus_adapter=adapter,
    model="text-embedding-3-large",
    langchain_config={"fallback_to_simple_context": True}
)

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name="my_docs"
)
```

### C.4. LlamaIndex Settings Integration

```python
from corpus_sdk.embedding.framework_adapters.llamaindex import configure_llamaindex_embeddings
from llama_index.core import Settings

embeddings = configure_llamaindex_embeddings(
    corpus_adapter=adapter,
    model_name="text-embedding-3-large",
    llamaindex_config={"strict_text_types": False},  # Lenient mode
    embedding_dimension=1536  # Required if adapter lacks get_embedding_dimension()
)

# Auto-registers with Settings
index = VectorStoreIndex.from_documents(documents)
```

### C.5. Semantic Kernel Plugin

```python
from corpus_sdk.embedding.framework_adapters.semantic_kernel import register_with_semantic_kernel
import semantic_kernel as sk

kernel = sk.Kernel()

embeddings = register_with_semantic_kernel(
    kernel=kernel,
    corpus_adapter=adapter,
    service_id="my-embedder",
    model_id="text-embedding-3-large"
)

# Use in kernel functions
result = await kernel.run_async(
    kernel.create_semantic_function("Find similar to: {{$input}}"),
    input="query text"
)
```

---

## Appendix D — Error Code Reference

| Code | Description | Frameworks |
|------|-------------|------------|
| `INVALID_EMBEDDING_RESULT` | Embedding result not a list of floats | All |
| `EMPTY_EMBEDDING_RESULT` | Embedding result empty when non-empty expected | All |
| `EMBEDDING_CONVERSION_ERROR` | Failed to convert result to expected type | All |
| `AUTOGEN_CONTEXT_INVALID` | Invalid AutoGen context structure | AutoGen |
| `CREWAI_CONTEXT_INVALID` | Invalid CrewAI context structure | CrewAI |
| `LANGCHAIN_CONFIG_INVALID` | Invalid LangChain adapter config | LangChain |
| `LLAMAINDEX_CONTEXT_INVALID` | Invalid LlamaIndex context | LlamaIndex |
| `LLAMAINDEX_CONFIG_INVALID` | Invalid LlamaIndex adapter config | LlamaIndex |
| `SEMANTIC_KERNEL_CONTEXT_INVALID` | Invalid Semantic Kernel context | Semantic Kernel |
| `SEMANTIC_KERNEL_CONFIG_INVALID` | Invalid Semantic Kernel adapter config | Semantic Kernel |
| `SYNC_WRAPPER_CALLED_IN_EVENT_LOOP` | Sync method called from async context | All |

---

## Appendix E — Implementation Status (Non-Normative)

| Adapter | Status | Conformance | Framework Versions |
|---------|--------|-------------|-------------------|
| AutoGen | Stable | 100% | ≥0.4.0 |
| CrewAI | Stable | 100% | ≥0.30.0 |
| LangChain | Stable | 100% | 0.1.x, 0.2.x, 0.3.x |
| LlamaIndex | Stable | 100% | ≥0.10.0 |
| Semantic Kernel | Stable | 100% | ≥1.0.0 |

**Note:** This appendix is non‑normative and provided for informational purposes only. The authoritative conformance status is determined by the conformance test suite (§16.3) and the implementation’s own documentation. This table may not be up‑to‑date; refer to the latest release notes for current status.

---

## Appendix F — Migration from Existing Framework Adapters (Informative)

### From Custom AutoGen Embeddings

```python
# Before
class MyAutoGenEmbeddings:
    def __call__(self, input):
        return [my_embed(t) for t in input]

# After
from corpus_sdk.embedding.framework_adapters.autogen import CorpusAutoGenEmbeddings
embeddings = CorpusAutoGenEmbeddings(my_adapter)
```

### From Custom LangChain Embeddings

```python
# Before
class MyEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [my_embed(t) for t in texts]

# After
from corpus_sdk.embedding.framework_adapters.langchain import CorpusLangChainEmbeddings
embeddings = CorpusLangChainEmbeddings(my_adapter)
```

### From Custom LlamaIndex Embeddings

```python
# Before
class MyEmbeddings(BaseEmbedding):
    def _get_text_embedding(self, text):
        return my_embed(text)

# After  
from corpus_sdk.embedding.framework_adapters.llamaindex import CorpusLlamaIndexEmbeddings
embeddings = CorpusLlamaIndexEmbeddings(my_adapter, embedding_dimension=1536)
```
