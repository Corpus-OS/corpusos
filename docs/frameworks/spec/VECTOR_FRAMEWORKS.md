
# VECTOR FRAMEWORK ADAPTERS SPECIFICATION

**specification_version:** `1.0.0`  
**protocol_version:** `1.0.0`  

---

## Abstract

This specification defines the Corpus Framework Adapter Suite for Vector operations: a standardized set of production-grade adapters that bridge Corpus Vector Protocol V1.0 implementations with five leading AI orchestration frameworks—AutoGen, CrewAI, LangChain, LlamaIndex, and Semantic Kernel. The suite provides consistent patterns for context propagation, error handling, observability, resource management, and streaming across frameworks while preserving each framework's native interfaces. This document includes normative contracts for adapter behavior, cross-framework patterns, error taxonomy integration, observability requirements, and implementation guidelines for enterprise-scale vector operations.

> **Keywords:** Framework Adapters, AutoGen, CrewAI, LangChain, LlamaIndex, Semantic Kernel, Vector Operations, Context Propagation, Error Normalization, Observability, Streaming, Multi-Framework, Protocol Bridge, Production Hardening

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
  * [4.5. Operation Context Building (MUST)](#45-operation-context-building-must)
  * [4.6. Thread-Safe Lazy Initialization (MUST)](#46-thread-safe-lazy-initialization-must)
  * [4.7. Resource Cleanup Hierarchy (MUST)](#47-resource-cleanup-hierarchy-must)
  * [4.8. Event Loop Guards (MUST)](#48-event-loop-guards-must)
  * [4.9. Async Streaming Normalization (MUST)](#49-async-streaming-normalization-must)
  * [4.10. Query Building Semantics (MUST)](#410-query-building-semantics-must)
  * [4.11. Namespace Resolution (MUST)](#411-namespace-resolution-must)
  * [4.12. Embedding Function Integration](#412-embedding-function-integration)
  * [4.13. Dimension Hint Management (MUST)](#413-dimension-hint-management-must)
  * [4.14. Score Thresholding (SHOULD)](#414-score-thresholding-should)
  * [4.15. MMR Search Pattern](#415-mmr-search-pattern)
  * [4.16. SIEM-Safe Observability (MUST)](#416-siem-safe-observability-must)
  * [4.17. Adapter Lifecycle State Machine (MUST)](#417-adapter-lifecycle-state-machine-must)
  * [4.18. Thread Pool Executors for Tool Bridging (MUST)](#418-thread-pool-executors-for-tool-bridging-must)
* [5. Shared Utility Layer](#5-shared-utility-layer)
  * [5.1. Validation Utilities](#51-validation-utilities)
    * [5.1.1. Top‑k Validation](#511-top-k-validation)
    * [5.1.2. Embedding Batch Validation](#512-embedding-batch-validation)
    * [5.1.3. Metadata Normalization](#513-metadata-normalization)
    * [5.1.4. ID Normalization](#514-id-normalization)
    * [5.1.5. Result Type Validation](#515-result-type-validation)
    * [5.1.6. Parameter Coercion for Tool Inputs](#516-parameter-coercion-for-tool-inputs)
  * [5.2. Dimension Hint Helpers](#52-dimension-hint-helpers)
  * [5.3. Zero Vector Generation](#53-zero-vector-generation)
  * [5.4. Snapshot Utilities](#54-snapshot-utilities)
  * [5.5. Operation Context Detection](#55-operation-context-detection)
  * [5.6. Async Iterator Detection & Normalization](#56-async-iterator-detection--normalization)
  * [5.7. Resource Cleanup Helpers](#57-resource-cleanup-helpers)
  * [5.8. Error Context Decorator Factory](#58-error-context-decorator-factory)
  * [5.9. Capabilities Normalization](#59-capabilities-normalization)
  * [5.10. MMR Utilities](#510-mmr-utilities)
* [6. Cross-Adapter Patterns](#6-cross-adapter-patterns)
  * [6.1. Unified Error Taxonomy Integration](#61-unified-error-taxonomy-integration)
  * [6.2. Consistent Observability](#62-consistent-observability)
  * [6.3. Operation Context Propagation](#63-operation-context-propagation)
  * [6.4. Idempotency Semantics](#64-idempotency-semantics)
  * [6.5. Partial Failure Reporting](#65-partial-failure-reporting)
  * [6.6. Backpressure Integration](#66-backpressure-integration)
  * [6.7. Vector Operation Determinism (REVISED)](#67-vector-operation-determinism-revised)
  * [6.8. Translator Shim Equivalence (MUST)](#68-translator-shim-equivalence-must)
  * [6.9. Single Source of Truth Pattern (SHOULD)](#69-single-source-of-truth-pattern-should)
  * [6.10. Delete Operation Helper Pattern](#610-delete-operation-helper-pattern)
* [7. AutoGen Adapter Specification](#7-autogen-adapter-specification)
  * [7.1. Overview](#71-overview)
  * [7.2. Framework-Specific Challenges](#72-framework-specific-challenges)
  * [7.3. Data Types](#73-data-types)
  * [7.4. Core Class: `CorpusAutoGenVectorClient`](#74-core-class-corpusautogenvectorclient)
    * [7.4.1. AutoGen Compatibility Surface](#741-autogen-compatibility-surface)
    * [7.4.2. Initialization](#742-initialization)
    * [7.4.3. Context Translation](#743-context-translation)
    * [7.4.4. Operations](#744-operations)
  * [7.5. Integration Helpers](#75-integration-helpers)
    * [7.5.1. `create_autogen_vector_tools()`](#751-create_autogen_vector_tools)
  * [7.6. Error Codes](#76-error-codes)
  * [7.7. AutoGen-Specific Context](#77-autogen-specific-context)
* [8. CrewAI Adapter Specification](#8-crewai-adapter-specification)
  * [8.1. Overview](#81-overview)
  * [8.2. Framework-Specific Challenges](#82-framework-specific-challenges)
  * [8.3. Data Types](#83-data-types)
  * [8.4. Core Class: `CorpusCrewAIVectorClient`](#84-core-class-corpuscrewaivectorclient)
    * [8.4.1. Initialization](#841-initialization)
    * [8.4.2. Task Context Translation](#842-task-context-translation)
    * [8.4.3. Operations](#843-operations)
    * [8.4.4. Tool Bridge Executor](#844-tool-bridge-executor)
  * [8.5. Integration Helpers](#85-integration-helpers)
    * [8.5.1. `create_crewai_vector_tools()`](#851-create_crewai_vector_tools)
  * [8.6. Error Codes](#86-error-codes)
  * [8.7. CrewAI-Specific Context](#87-crewai-specific-context)
* [9. LangChain Adapter Specification](#9-langchain-adapter-specification)
  * [9.1. Overview](#91-overview)
  * [9.2. Framework-Specific Challenges](#92-framework-specific-challenges)
  * [9.3. Data Types](#93-data-types)
  * [9.4. Core Class: `CorpusLangChainVectorClient`](#94-core-class-corpuslangchainvectorclient)
    * [9.4.1. Initialization](#941-initialization)
    * [9.4.2. Config Context Translation](#942-config-context-translation)
    * [9.4.3. Event Loop Safety](#943-event-loop-safety)
    * [9.4.4. Operations](#944-operations)
    * [9.4.5. Tool Bridge Executor](#945-tool-bridge-executor)
  * [9.5. Integration Helpers](#95-integration-helpers)
    * [9.5.1. `create_langchain_vector_tools()`](#951-create_langchain_vector_tools)
    * [9.5.2. `create_corpus_vector_tool()`](#952-create_corpus_vector_tool)
  * [9.6. Error Codes](#96-error-codes)
  * [9.7. LangChain-Specific Context](#97-langchain-specific-context)
* [10. LlamaIndex Adapter Specification](#10-llamaindex-adapter-specification)
  * [10.1. Overview](#101-overview)
  * [10.2. Framework-Specific Challenges](#102-framework-specific-challenges)
  * [10.3. Data Types](#103-data-types)
  * [10.4. Core Class: `CorpusLlamaIndexVectorClient`](#104-core-class-corpusllamaindexvectorclient)
    * [10.4.1. Initialization](#1041-initialization)
    * [10.4.2. Callback Manager Context Translation](#1042-callback-manager-context-translation)
    * [10.4.3. Operations](#1043-operations)
    * [10.4.4. Single Source of Truth Request Builders](#1044-single-source-of-truth-request-builders)
  * [10.5. Integration Helpers](#105-integration-helpers)
    * [10.5.1. `CorpusVectorIndex`](#1051-corpusvectorindex)
  * [10.6. Error Codes](#106-error-codes)
  * [10.7. LlamaIndex-Specific Context](#107-llamaindex-specific-context)
* [11. Semantic Kernel Adapter Specification](#11-semantic-kernel-adapter-specification)
  * [11.1. Overview](#111-overview)
  * [11.2. Framework-Specific Challenges](#112-framework-specific-challenges)
  * [11.3. Data Types](#113-data-types)
  * [11.4. Core Class: `CorpusSemanticKernelVectorClient`](#114-core-class-corpussemantickernelvectorclient)
    * [11.4.1. Initialization](#1141-initialization)
    * [11.4.2. Context + Settings Translation](#1142-context--settings-translation)
    * [11.4.3. Operations](#1143-operations)
    * [11.4.4. Forward-Compatible Kwargs Handling](#1144-forward-compatible-kwargs-handling)
  * [11.5. Integration Helpers](#115-integration-helpers)
    * [11.5.1. `CorpusSemanticKernelVectorPlugin`](#1151-corpussemantickernelvectorplugin)
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
  * [B.1. Context Building Patterns](#b1-context-building-patterns)
  * [B.2. Event Loop Safety Patterns](#b2-event-loop-safety-patterns)
  * [B.3. Async Streaming Normalization Patterns](#b3-async-streaming-normalization-patterns)
  * [B.4. Resource Cleanup Patterns](#b4-resource-cleanup-patterns)
  * [B.5. Delete Operation Helper Patterns](#b5-delete-operation-helper-patterns)
  * [B.6. Single Source of Truth Request Builders](#b6-single-source-of-truth-request-builders)
  * [B.7. MMR Implementation Patterns](#b7-mmr-implementation-patterns)
* [Appendix C — End-to-End Usage Examples](#appendix-c--end-to-end-usage-examples)
  * [C.1. AutoGen Agent with Vector Tools](#c1-autogen-agent-with-vector-tools)
  * [C.2. CrewAI Crew with Vector Tools](#c2-crewai-crew-with-vector-tools)
  * [C.3. LangChain Agent with Vector Tools](#c3-langchain-agent-with-vector-tools)
  * [C.4. LlamaIndex Vector Index](#c4-llamaindex-vector-index)
  * [C.5. Semantic Kernel Plugin Registration](#c5-semantic-kernel-plugin-registration)
* [Appendix D — Error Code Reference](#appendix-d--error-code-reference)
* [Appendix E — Implementation Status (Non-Normative)](#appendix-e--implementation-status-non-normative)
* [Appendix F — Migration from Existing Framework Adapters (Informative)](#appendix-f--migration-from-existing-framework-adapters-informative)

---

## 1. Introduction

### 1.1. Motivation

The AI framework landscape has fragmented into five dominant orchestration layers—AutoGen for multi-agent systems, CrewAI for role-based agent teams, LangChain for chain-of-thought pipelines, LlamaIndex for RAG and indexing, and Semantic Kernel for enterprise AI integration. Each framework defines its own interface for vector operations with subtly different expectations:

- **AutoGen** requires tool-based interfaces for agent vector access and struggles with async/sync boundaries in agent loops.
- **CrewAI** expects vector operations attached to agents but provides no shared runtime context across agent executions.
- **LangChain** defines tool interfaces and Runnable patterns but creates deadlock risks when sync methods are called from async contexts.
- **LlamaIndex** implements `VectorStore` with specific expectations about embedding integration and callback propagation.
- **Semantic Kernel** uses plugin-based architecture with context and settings objects that must be propagated to underlying operations.

Building and maintaining separate adapters for each framework duplicates effort, fragments observability, and creates inconsistent error handling across an organization's AI stack. Framework-specific edge cases—like async streaming return shape variations, or context extraction failures—cause production outages that are difficult to debug without deep framework expertise.

The Corpus Framework Adapter Suite for Vector solves this by providing a single, battle-tested implementation of each framework's vector interface, backed by the Corpus Vector Protocol. Each adapter encapsulates the framework-specific hardening required for production deployments while sharing a common foundation for error handling, observability, and resource management. Organizations can standardize on Corpus vector operations once and use them across any supported framework without rebuilding adapter logic.

### 1.2. Scope

This specification defines five framework adapters for vector operations:

1. **AutoGen Adapter** — Implements vector tool interfaces with FunctionTool wrappers, context extraction from conversation objects, and thread-pool bridging for event-loop safety.

2. **CrewAI Adapter** — Implements BaseTool interfaces with context extraction from agent tasks, bounded thread-pool execution for sync-in-async safety, and JSON-safe snapshotting for tool outputs.

3. **LangChain Adapter** — Implements BaseTool interfaces with config context extraction, event-loop detection, worker-thread fallback, and comprehensive validation for LLM-provided parameters.

4. **LlamaIndex Adapter** — Implements `VectorStore` protocol with callback manager context propagation, Single Source of Truth request builders, and embedding function integration.

5. **Semantic Kernel Adapter** — Implements plugin architecture with context+settings translation, forward-compatible kwargs handling, and graceful fallback for capability methods.

All adapters share:

- **Context propagation** — Framework-specific context (conversation, task, config, callback_manager, context/settings) flows into `OperationContext` and framework_ctx.
- **Error normalization** — All exceptions are enriched with `attach_context()` using framework-specific error codes.
- **Observability** — Dynamic context extraction captures operation types, namespaces, top‑k values, batch sizes, and embedding dimensions.
- **Streaming support** — Both sync and async streaming with robust iterator normalization.
- **Resource management** — Sync/async context managers with proper cleanup hierarchy.
- **Namespace resolution** — Consistent precedence: explicit args → spec.namespace → client defaults.
- **Delete operation helpers** — Shared logic for filter/ID selection across all delete methods.
- **Embedding function integration** — Both sync and async embedding functions with dimension hint management.
- **MMR search** — Standard MMR implementation across all adapters.

### 1.3. Design Philosophy

- **Protocol-First (MUST).** Adapters require only duck-typed vector adapters implementing `VectorProtocolV1`, not strict inheritance. This allows minimal test doubles and lightweight integrations.

- **Framework Resilience (MUST).** Adapters defend against framework evolution by filtering context, normalizing inputs, and never assuming internal APIs remain stable. Static compatibility methods satisfy framework probes without leaking implementation details.

- **Observability-First (MUST).** Every vector operation attaches rich error context: framework identity, operation type, namespace, top‑k, batch sizes, and embedding dimensions. Exceptions crossing framework boundaries carry enough context to debug without log scraping.

- **Fail-Safe Context Translation (MUST).** Context translation from framework-specific structures to `OperationContext` must never break vector operations. If translation fails, adapters proceed without core context and attach diagnostic snapshots.

- **Async-Safe Sync Usage (MUST).** Sync APIs enforce guard rails preventing calls from inside active event loops. When bridging is required for tool integration, adapters use controlled worker-thread execution.

- **Streaming Robustness (MUST).** Async streaming methods must handle both direct AsyncIterator returns and awaitable→AsyncIterator patterns from underlying translators, with post-resolution validation.

- **Single Source of Truth (SHOULD).** Complex request shapes (upsert vectors, query) should use shared builders to prevent drift between sync/async implementations.

- **Production Hardening (MUST).** Thread-safe lazy initialization, resource cleanup hierarchies, SIEM-safe logging, and consistent namespace resolution are non-negotiable requirements.

- **Embedding Determinism (SHOULD).** For empty inputs (empty strings or whitespace-only), adapters SHOULD return a deterministic zero vector when the vector dimension is known, rather than raising an error or calling the embedding function. This ensures predictable behavior in edge cases.

---

## 2. Requirements Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [RFC2119] [RFC8174] when, and only when, they appear in all capitals.

**Example:**  
- "The adapter MUST reject non‑string inputs" indicates a strict requirement that must be implemented and verified.  
- "The adapter SHOULD log warnings for large top‑k values" indicates a recommendation that may be deviated from only with good reason.  

**Justified Deviation Example:**  
A developer might choose to disable strict validation in a controlled environment where they have verified all inputs are valid, and where the performance cost of validation is significant. This deviation MUST be documented in the code, explaining why it is safe and what assumptions are being made. The adapter MUST still provide a way to re‑enable strict validation via configuration.

---

## 3. Terminology

**Adapter** — Concrete implementation of a framework-specific vector interface backed by a Corpus Vector Protocol V1 adapter.

**Vector Adapter** — The underlying vector implementation that provides the VectorProtocolV1 interface.

**Operation Context** — Core context object containing `request_id`, `idempotency_key`, `deadline_ms`, `traceparent`, `tenant`, and `attrs`.

**Framework Context** — Framework-specific context dictionary passed to the translator alongside core context (e.g., conversation, task, config).

**Translator** — `VectorTranslator` instance that orchestrates vector operations, handling batching, retries, and streaming.

**Framework Translator** — `VectorFrameworkTranslator` implementation that handles framework-specific translation of results.

**Event Loop Guard** — Runtime check preventing sync methods from being called inside an active asyncio event loop.

**Namespace Resolution** — Precedence rules determining which namespace value is used: explicit argument → spec.namespace → client default.

**Single Source of Truth** — Pattern where shared request builders ensure sync/async implementations remain consistent.

**Tool Bridge Executor** — Bounded thread pool used to execute sync vector calls from within async contexts in tool integrations.

**Dimension Hint** — Thread‑safe, lazily‑updated record of the vector dimension observed from the first embedding. Used for validation and deterministic zero‑vector generation.

**Zero Vector** — A vector of zeros with known dimension, used as a fallback for empty inputs when dimension is known.

**MMR (Maximal Marginal Relevance)** — Re‑ranking algorithm that balances relevance and diversity.

**Types from the Vector Protocol:** This specification references types defined in the Corpus Vector Protocol V1.0: `VectorMatch`, `QueryResult`, `UpsertResult`, `DeleteResult`, `OperationContext`, `VectorCapabilities`, `BadRequest`, `NotSupported`, `VectorAdapterError`, `Embeddings` (as `Sequence[Sequence[float]]`), and `Metadata` (as `Dict[str, Any]`). Their exact definitions are provided in the protocol specification; adapters need only duck‑type compatibility.

---

## 4. Common Foundation Across All Adapters

### 4.1. Protocol-First Design (MUST)

All adapters MUST accept a `vector_adapter` or `adapter` parameter that implements VectorProtocolV1. Strict `isinstance` checks are NOT REQUIRED; behavioral duck typing suffices.

```python
# Valid vector_adapter implementations:
class MinimalVectorAdapter:
    def query(self, query, **kwargs): ...
    def capabilities(self): ...
    def health(self): ...
    def close(self): ...
    async def aclose(self): ...

class FullVectorAdapter:
    async def aquery(self, spec, ctx=None): ...
    def capabilities(self): ...
    async def acapabilities(self): ...
    def health(self): ...
    async def ahealth(self): ...
    def close(self): ...
    async def aclose(self): ...
```

Adapters MUST validate at initialization that the provided adapter has the required methods:

```python
if not hasattr(resolved_adapter, "query") or not hasattr(resolved_adapter, "capabilities"):
    raise TypeError("adapter must implement VectorProtocolV1-like interface with 'query' and 'capabilities' methods")
```

### 4.2. Framework Resilience Strategy

All adapters implement three defensive layers:

1. **Context Filtering** — Extract only known, stable fields from framework-specific context objects. Unknown keys are ignored (see §4.5). Unknown fields are snapshotted for observability but not relied upon for correctness.

2. **Normalized Error Attachment** — All exceptions are enriched with `attach_context()` using framework-specific error codes and dynamic context (operation, namespace, top‑k, batch sizes, embedding dimensions).

3. **Forward-Compatible Method Signatures** — Methods accept `**kwargs` and gracefully handle unsupported parameters by logging and ignoring, ensuring compatibility as frameworks evolve.

### 4.3. Error Context Attachment (MUST)

Every adapter MUST decorate its core vector methods with error-context decorators that capture:

- Operation name (`similarity_search`, `stream_query`, `add_texts`, `delete`, etc.)
- Framework identity and version
- Namespace (when available)
- Query length (for search operations)
- `top_k` value
- Batch size (for batch operations)
- Framework-specific routing fields

```python
@with_vector_error_context("similarity_search_sync")
def similarity_search(self, query, ..., context=None, settings=None):
    # Implementation
    pass

@with_async_vector_error_context("similarity_search_async")
async def asimilarity_search(self, query, ..., context=None, settings=None):
    # Implementation
    pass
```

### 4.4. Dynamic Context Extraction Pattern

All adapters implement dynamic context extraction that captures per‑call metrics:

```python
def _extract_dynamic_context(self, args, kwargs, operation):
    ctx = {
        "framework": self._framework_name,
        "framework_version": getattr(self, "_framework_version", None),
    }
    
    if operation in ("similarity_search", "stream_query") and args and isinstance(args[0], str):
        ctx["query_len"] = len(args[0])
    
    # Extract top‑k if present
    top_k = kwargs.get("k")
    if top_k is None and len(args) >= 2:
        top_k = args[1]
    if isinstance(top_k, int):
        ctx["top_k"] = top_k
    
    # Extract namespace if present
    namespace = kwargs.get("namespace")
    if namespace:
        ctx["namespace"] = namespace
    
    # Framework-specific fields: extract known keys, ignore unknown
    framework_ctx = kwargs.get("context") or kwargs.get("config") or kwargs.get("task")
    if hasattr(framework_ctx, "__dict__"):
        for key in self._framework_routing_fields:
            if hasattr(framework_ctx, key):
                ctx[key] = getattr(framework_ctx, key)
    
    return ctx
```

**Versioning Contract:** Framework context objects (conversation, task, config, callback_manager, context) MAY contain fields unknown to the adapter. Adapters MUST ignore such fields and MUST NOT raise errors because of them. This ensures forward compatibility when frameworks add new fields.

### 4.5. Operation Context Building (MUST)

All adapters implement a `_build_ctx()` method that translates framework-specific inputs into an `OperationContext`:

```python
def _build_ctx(self, *, framework_input=None, extra_context=None) -> Optional[OperationContext]:
    """
    Build OperationContext from framework-specific inputs.
    
    - If translation fails, log warning and return None
    - Enrich attrs with framework and framework_version
    - Use structural check (_looks_like_operation_context) to validate result
    """
    extra = dict(extra_context or {})
    
    if framework_input is None and not extra:
        return None
    
    try:
        ctx_candidate = core_ctx_from_framework(
            framework_input,
            framework_version=self._framework_version,
            **extra,
        )
    except Exception as exc:
        attach_context(exc, framework=self._framework_name, ...)
        logger.warning("Failed to build OperationContext; proceeding without.")
        return None
    
    if not _looks_like_operation_context(ctx_candidate):
        logger.warning("Non-OperationContext returned; ignoring.")
        return None
    
    # Enrich attrs with framework metadata
    attrs = getattr(ctx_candidate, "attrs", {}) or {}
    if isinstance(attrs, dict):
        attrs.setdefault("framework", self._framework_name)
        if self._framework_version:
            attrs.setdefault("framework_version", self._framework_version)
    
    return ctx_candidate
```

### 4.6. Thread-Safe Lazy Initialization (MUST)

Translators and other expensive resources MUST be initialized lazily with thread safety:

```python
@cached_property
def _translator(self) -> VectorTranslator:
    """Lazily construct and cache VectorTranslator with thread safety."""
    framework_translator = self._framework_translator or DefaultVectorFrameworkTranslator()
    return create_vector_translator(
        adapter=self._vector,
        framework=self._framework_name,
        translator=framework_translator,
    )
```

### 4.7. Resource Cleanup Hierarchy (MUST)

All adapters MUST implement both sync and async context managers with proper cleanup. The `close()` and `aclose()` methods MUST be thread‑safe and idempotent. Typical implementations use a lock to guard the cleanup logic.

```python
def __enter__(self):
    return self

def __exit__(self, exc_type, exc, tb):
    self.close()

async def __aenter__(self):
    return self

async def __aexit__(self, exc_type, exc, tb):
    await self.aclose()

def close(self) -> None:
    with self._close_lock:
        if self._closed:
            return
        self._closed = True
    
    if hasattr(self._vector, "close"):
        try:
            self._vector.close()
        except Exception:
            logger.debug("Failed to close vector adapter", exc_info=True)

async def aclose(self) -> None:
    async with self._aclose_lock:
        if self._aclosed:
            return
        self._aclosed = True
    
    if hasattr(self._vector, "aclose"):
        try:
            await self._vector.aclose()
            self._closed = True
            return
        except Exception:
            logger.debug("Failed to async-close vector adapter", exc_info=True)
    
    if not self._closed:
        self.close()
```

### 4.8. Event Loop Guards (MUST)

All sync methods MUST prevent execution inside running event loops:

```python
def _ensure_not_in_event_loop(api_name: str) -> None:
    """
    Prevent sync methods from being called inside active asyncio event loops.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return
    
    raise RuntimeError(
        f"{api_name}() cannot be called from an active event loop. "
        f"Use a{api_name}() instead. [SYNC_WRAPPER_CALLED_IN_EVENT_LOOP]"
    )
```

### 4.9. Async Streaming Normalization (MUST)

All async streaming methods MUST handle variations in translator return types. The normalization logic is provided in §5.6.

```python
async def astream_query(self, ...):
    # ... setup ...
    aiter_or_awaitable = self._translator.arun_query_stream(...)
    normalized = _normalize_async_iterator(aiter_or_awaitable)   # see §5.6
    
    if inspect.isawaitable(normalized):
        aiter = await normalized
    else:
        aiter = normalized
    
    if not _is_async_iterator(aiter):
        raise TypeError("Resolved value not an AsyncIterator")
    
    async for chunk in aiter:
        yield chunk
```

### 4.10. Query Building Semantics (MUST)

All adapters MUST implement a consistent `_build_raw_query()` method. The exact implementation is provided in §B.6.

```python
def _build_raw_query(
    self,
    embedding: Sequence[float],
    *,
    k: int,
    namespace: Optional[str],
    filter: Optional[Mapping[str, Any]],
    include_vectors: bool,
) -> Mapping[str, Any]:
    """
    Build raw query mapping for VectorTranslator.
    
    Required fields:
    - vector: list[float]
    - top_k: int
    - namespace: str (if resolved)
    - filters: dict (if any)
    - include_metadata: bool
    - include_vectors: bool
    """
    ns = self._effective_namespace(namespace)
    
    raw = {
        "vector": [float(x) for x in embedding],
        "top_k": int(k),
        "namespace": ns,
        "filters": dict(filter) if filter else None,
        "include_metadata": True,
        "include_vectors": bool(include_vectors),
    }
    return raw
```

**Embedding Validation:** The embedding sequence is already validated by the embedding helper; this builder simply coerces to float list.

### 4.11. Namespace Resolution (MUST)

All adapters MUST implement consistent namespace precedence:

1. **Explicit argument** — If `namespace` is provided directly to the method call, it has highest precedence.
2. **Spec namespace** — For spec‑based operations (if any), `spec.namespace` is used if present.
3. **Client default** — If neither explicit nor spec namespace is provided, the client's `default_namespace` (set during initialization) is used.
4. **None** — If none of the above are set, namespace is omitted from the request.

```python
def _effective_namespace(self, namespace: Optional[str]) -> Optional[str]:
    """Resolve namespace using explicit override or store default."""
    return namespace if namespace is not None else self.default_namespace

def _framework_ctx(self, *, operation: str, namespace: Optional[str] = None) -> Mapping[str, Any]:
    """Build framework context with resolved namespace."""
    ctx = {"framework": self._framework_name, "operation": operation}
    
    effective_ns = self._effective_namespace(namespace)
    if effective_ns is not None:
        ctx["namespace"] = effective_ns
    
    return ctx
```

### 4.12. Embedding Function Integration

Adapters MUST support both sync and async embedding functions, with clear precedence rules. The implementation helpers are provided in §5.

```python
# Sync embedding function (for add_texts, embed_query)
def _ensure_embeddings(
    self,
    texts: List[str],
    embeddings: Optional[Embeddings],
) -> Embeddings:
    """
    Ensure embeddings are available for a batch of texts.
    
    - If embeddings provided, validate length.
    - Else, if embedding_function configured, compute.
    - Else, raise NotSupported.
    """
    # Implementation in §5

# Async embedding function (for aadd_texts, aembed_query)
async def _ensure_embeddings_async(
    self,
    texts: List[str],
    embeddings: Optional[Embeddings],
) -> Embeddings:
    """
    Async-safe version with fallback to sync embedding function in thread pool.
    """
    # Implementation in §5
```

**Empty‑input hardening:** For empty or whitespace‑only strings, adapters SHOULD return deterministic zero vectors when the vector dimension is known, rather than calling the embedding function or raising. If dimension is unknown, raise `BadRequest` with code `EMPTY_INPUT_DIM_UNKNOWN`.

### 4.13. Dimension Hint Management (MUST)

All adapters MUST maintain a thread‑safe, first‑write‑wins dimension hint. The helper functions are provided in §5.2.

```python
def _update_dim_hint(self, dim: Optional[int]) -> None:
    """Thread‑safe, best‑effort update of vector dimension hint."""
    # Implementation in §5.2

def _maybe_check_dim(self, vec: Sequence[float], *, where: str) -> None:
    """Validate vector dimensionality against hint (if set)."""
    # Implementation in §5.2

def _zero_vector(self) -> List[float]:
    """Return zero vector of known dimension, or raise."""
    # Implementation in §5.3
```

### 4.14. Score Thresholding (SHOULD)

Adapters MAY implement client‑side score threshold filtering:

```python
def _apply_score_threshold(
    self,
    matches: List[VectorMatch],
    threshold: Optional[float],
) -> List[VectorMatch]:
    """Filter matches by minimum score."""
    if threshold is None:
        return matches
    return [m for m in matches if float(m.score) >= threshold]
```

Threshold value is configured at client initialization and can be overridden per call.

### 4.15. MMR Search Pattern

All adapters SHOULD provide MMR search capabilities with a shared implementation. The core MMR logic is provided in §5.10.

```python
def _mmr_select_indices(
    self,
    query_vec: Sequence[float],
    candidate_matches: List[VectorMatch],
    k: int,
    lambda_mult: float,
) -> List[int]:
    """
    Select indices via Maximal Marginal Relevance.
    
    - Uses original database scores for relevance.
    - Caches similarity calculations.
    - Respects lambda_mult in [0,1].
    """
    # Implementation in §5.10
    pass
```

### 4.16. SIEM-Safe Observability (MUST)

All logging MUST:

- Never log raw query text, parameters, or tenant identifiers
- Use truncation for long strings and containers
- Include `tenant_hash` instead of raw tenant
- Log operation completion with dimensions and latency

**Truncation thresholds (Normative):**  
- Strings longer than `MAX_STRING_LENGTH = 5000` characters MUST be truncated
- Containers with more than `MAX_CONTAINER_ITEMS = 200` items MUST be limited

```python
logger.debug(
    "Query completed: op=%s namespace=%s top_k=%d latency_ms=%.2f",
    operation, namespace, top_k, elapsed_ms
)
```

### 4.17. Adapter Lifecycle State Machine (MUST)

Each adapter instance MUST maintain a clear lifecycle with the following states and transitions:

- **`UNINITIALIZED`** (initial state after `__init__`, before any lazy initialization)
- **`INITIALIZED`** (after first use, lazy resources created)
- **`CLOSED`** (after `close()` or `aclose()` is called)

**Valid Transitions:**
- `UNINITIALIZED` → `INITIALIZED`: automatically when any operation is first invoked.
- `UNINITIALIZED` → `CLOSED`: via `close()` or `aclose()`.
- `INITIALIZED` → `CLOSED`: via `close()` or `aclose()`.
- `CLOSED` → (no transitions allowed; instance is dead).

**Illegal States:**
- Attempting any operation after `CLOSED` MUST raise `RuntimeError`.
- Calling `close()` or `aclose()` multiple times is allowed and MUST be idempotent.
- Calling `close()` from within an async context MUST raise `RuntimeError` (except in controlled tool bridge scenarios).

**Partial Initialization Failure:**  
If an exception occurs during `__init__` after some resources have been allocated (e.g., a lock created but validation fails), the adapter MUST clean up any successfully allocated resources before propagating the exception. Implementations SHOULD use a try/finally block or a context manager to ensure cleanup. After a failed `__init__`, the object is considered not constructed and MUST NOT be used; no lifecycle state is defined. Callers must ensure that if `__init__` raises, the object reference is discarded.

### 4.18. Thread Pool Executors for Tool Bridging (MUST)

For adapters that provide tool integration (AutoGen, CrewAI, LangChain), any thread pool executor used to bridge sync calls from async contexts MUST satisfy the following requirements:

- The executor's threads MUST NOT prevent interpreter shutdown (e.g., they SHOULD be daemon threads). Because the standard `ThreadPoolExecutor` does not expose a `daemon` parameter directly, implementations MAY use a custom thread factory that creates daemon threads, or they MAY rely on the fact that the pool is not explicitly shut down and threads will be terminated abruptly on exit (which is acceptable for short‑lived operations).
- The pool MUST have a bounded work queue with a configurable maximum size (default 1000). If the queue is full, submitting a new task MUST block or raise an exception; implementations MAY use a `Queue` with `maxsize` and a timeout.
- The executor MUST be created as a **module‑level singleton** shared by all instances of that adapter to avoid unbounded thread creation.
- No explicit shutdown of the pool is required, but implementations MAY register an `atexit` handler to attempt graceful shutdown (non‑normative).

---

## 5. Shared Utility Layer

This section contains reusable helpers that implement the behaviors mandated in §4. Adapters SHOULD use these utilities or provide equivalent implementations.

### 5.1. Validation Utilities

#### 5.1.1. Top‑k Validation

```python
def validate_top_k(top_k: int, *, operation: str, error_code: str) -> None:
    """Validate top_k is positive."""
    if not isinstance(top_k, int) or top_k <= 0:
        raise ValueError(f"{operation}: top_k must be positive integer; got {top_k}")
```

#### 5.1.2. Embedding Batch Validation

```python
def validate_embeddings(embeddings: Embeddings, expected_len: int) -> None:
    """Validate embeddings list length and that each embedding is non‑empty."""
    if len(embeddings) != expected_len:
        raise ValueError(f"embeddings length {len(embeddings)} != expected {expected_len}")
    for i, emb in enumerate(embeddings):
        if not emb or len(emb) == 0:
            raise ValueError(f"embedding at index {i} is empty")
```

#### 5.1.3. Metadata Normalization

```python
def normalize_metadatas(n: int, metadatas: Optional[List[Metadata]]) -> List[Metadata]:
    """Normalize metadata list to length n."""
    if metadatas is None:
        return [{} for _ in range(n)]
    if len(metadatas) == n:
        return [dict(m or {}) for m in metadatas]
    if len(metadatas) == 1 and n > 1:
        base = dict(metadatas[0] or {})
        return [dict(base) for _ in range(n)]
    raise ValueError(f"metadatas length {len(metadatas)} does not match n {n}")
```

#### 5.1.4. ID Normalization

```python
def normalize_ids(n: int, ids: Optional[List[str]]) -> List[str]:
    """Normalize IDs list to length n, generating UUIDs if None."""
    if ids is None:
        return [uuid.uuid4().hex for _ in range(n)]
    if len(ids) != n:
        raise ValueError(f"ids length {len(ids)} does not match n {n}")
    return [str(i) for i in ids]
```

#### 5.1.5. Result Type Validation

```python
def validate_vector_result_type(
    result: Any,
    *,
    expected_type: Any,
    operation: str,
    error_code: str,
) -> Any:
    """Validate result type and return it unchanged."""
    if not isinstance(result, expected_type):
        raise TypeError(
            f"{operation} returned {type(result).__name__}; expected {expected_type.__name__} "
            f"[{error_code}]"
        )
    return result
```

#### 5.1.6. Parameter Coercion for Tool Inputs

The following functions MUST be used by adapters that accept LLM‑provided parameters (e.g., CrewAI, LangChain tools) to safely convert and bound numeric inputs.

```python
def coerce_bounded_positive_int(
    value: Any,
    *,
    name: str,
    default: int,
    min_value: int = 1,
    max_value: int = 100,
) -> int:
    """
    Convert a possibly‑LLM‑provided value into a safe bounded positive int.

    Behavior:
      - If conversion fails, returns the provided default.
      - If converted value is out of bounds, clamps to [min_value, max_value].
      - MUST NOT raise an exception.

    This function is used to protect tool execution from malformed or malicious inputs.
    """
    try:
        ivalue = int(value)
    except Exception:
        logger.debug("Invalid tool param %s=%r; defaulting to %d", name, value, default)
        return default

    if ivalue < min_value:
        return min_value
    if ivalue > max_value:
        return max_value
    return ivalue

def validated_k(value: Any, *, max_k: int = 100) -> int:
    """Specialization for k parameter."""
    return coerce_bounded_positive_int(value, name="k", default=4, min_value=1, max_value=max_k)

def validated_fetch_k(value: Any, *, max_k: int = 500) -> int:
    """Specialization for fetch_k (MMR)."""
    return coerce_bounded_positive_int(value, name="fetch_k", default=20, min_value=1, max_value=max_k)
```

### 5.2. Dimension Hint Helpers

```python
def update_dim_hint_safe(hint_attr: Optional[int], lock: RLock, new_dim: int) -> Optional[int]:
    """Thread‑safe update of dimension hint (first write wins)."""
    if hint_attr is not None:
        return hint_attr
    with lock:
        if hint_attr is None:
            hint_attr = new_dim
    return hint_attr

def check_dim(hint: Optional[int], vec: Sequence[float], where: str) -> None:
    """Validate vector dimension against hint."""
    if hint is None:
        return
    if len(vec) != hint:
        raise BadRequest(f"Dimension mismatch at {where}: got {len(vec)}, expected {hint}")
```

### 5.3. Zero Vector Generation

```python
def zero_vector(dim: int) -> List[float]:
    """Return zero vector of given dimension."""
    return [0.0] * dim
```

### 5.4. Snapshot Utilities

```python
def _safe_snapshot(value: Any, *, max_items: int = 200, max_str: int = 5000) -> Any:
    """
    Convert any value to a safe‑to‑log snapshot:
    - Truncates long strings
    - Limits container sizes
    - Falls back to repr() for unknown objects
    """
    try:
        if value is None or isinstance(value, (bool, int, float)):
            return value
        if isinstance(value, str):
            return value if len(value) <= max_str else value[:max_str] + "…"
        if isinstance(value, Mapping):
            out = {}
            for i, (k, v) in enumerate(value.items()):
                if i >= max_items:
                    out["…"] = f"truncated after {max_items} items"
                    break
                out[str(k)] = _safe_snapshot(v, max_items=max_items, max_str=max_str)
            return out
        if isinstance(value, (list, tuple)):
            out = []
            for i, v in enumerate(value):
                if i >= max_items:
                    out.append(f"… truncated after {max_items} items")
                    break
                out.append(_safe_snapshot(v, max_items=max_items, max_str=max_str))
            return out
        to_dict = getattr(value, "to_dict", None)
        if callable(to_dict):
            return _safe_snapshot(to_dict(), max_items=max_items, max_str=max_str)
        return repr(value)
    except Exception:
        return {"repr": repr(value)}
```

### 5.5. Operation Context Detection

```python
def _looks_like_operation_context(obj: Any) -> bool:
    """
    Structural check for OperationContext‑like objects.
    
    Requires attrs plus at least one of: to_dict, request_id, traceparent.
    """
    if obj is None:
        return False
    
    try:
        if isinstance(obj, OperationContext):
            return True
    except TypeError:
        pass
    
    has_attrs = hasattr(obj, "attrs")
    has_to_dict = hasattr(obj, "to_dict")
    has_request_id = hasattr(obj, "request_id")
    has_traceparent = hasattr(obj, "traceparent")
    
    return has_attrs and (has_to_dict or has_request_id or has_traceparent)
```

### 5.6. Async Iterator Detection & Normalization

```python
def _is_async_iterator(obj: Any) -> bool:
    return hasattr(obj, "__aiter__") and hasattr(obj, "__anext__")

def _normalize_async_iterator(aiter_or_awaitable: Any) -> Any:
    if inspect.isawaitable(aiter_or_awaitable):
        return aiter_or_awaitable
    if _is_async_iterator(aiter_or_awaitable):
        return aiter_or_awaitable
    raise TypeError(f"Expected AsyncIterator or awaitable; got {type(aiter_or_awaitable)}")
```

### 5.7. Resource Cleanup Helpers

```python
def _maybe_close_sync(obj: Any) -> None:
    if obj is None:
        return
    close_fn = getattr(obj, "close", None)
    if callable(close_fn):
        try:
            close_fn()
        except Exception:
            logger.debug("Failed to close object", exc_info=True)

async def _maybe_close_async(obj: Any) -> None:
    if obj is None:
        return
    aclose_fn = getattr(obj, "aclose", None)
    if callable(aclose_fn):
        try:
            await aclose_fn()
            return
        except Exception:
            logger.debug("Failed to async‑close object", exc_info=True)
    _maybe_close_sync(obj)
```

### 5.8. Error Context Decorator Factory

```python
def create_vector_error_context_decorator(
    framework: str,
    is_async: bool,
) -> Callable:
    """
    Create a decorator that attaches rich error context to vector operations.
    """
    def decorator(operation: str, **static_context: Any) -> Callable:
        def wrap(func: Callable) -> Callable:
            if is_async:
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        dynamic_ctx = _extract_dynamic_context(args, kwargs, operation)
                        attach_context(
                            e,
                            framework=framework,
                            operation=operation,
                            **static_context,
                            **dynamic_ctx,
                        )
                        raise
                return async_wrapper
            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        dynamic_ctx = _extract_dynamic_context(args, kwargs, operation)
                        attach_context(
                            e,
                            framework=framework,
                            operation=operation,
                            **static_context,
                            **dynamic_ctx,
                        )
                        raise
                return sync_wrapper
        return wrap
    return decorator
```

### 5.9. Capabilities Normalization

```python
def vector_capabilities_to_dict(caps: Any) -> Dict[str, Any]:
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

### 5.10. MMR Utilities

```python
def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def mmr_select_indices(
    query_vec: Sequence[float],
    candidate_matches: List[VectorMatch],
    k: int,
    lambda_mult: float,
    similarity_fn: Callable = cosine_similarity,
) -> List[int]:
    """
    Standard MMR selection implementation.
    """
    if k <= 0 or not candidate_matches:
        return []
    
    if lambda_mult >= 1.0:
        # Pure relevance
        scores = [c.score for c in candidate_matches]
        return sorted(range(len(candidate_matches)), key=lambda i: scores[i], reverse=True)[:k]
    
    scores = [c.score for c in candidate_matches]
    max_score = max(scores) if scores else 1.0
    norm_scores = [s / max_score for s in scores]
    
    # Similarity cache
    sim_cache = {}
    def sim(i, j):
        key = (min(i,j), max(i,j))
        if key not in sim_cache:
            a = candidate_matches[i].vector.vector
            b = candidate_matches[j].vector.vector
            sim_cache[key] = similarity_fn(a, b) if a and b else 0.0
        return sim_cache[key]
    
    selected = []
    candidates_set = set(range(len(candidate_matches)))
    
    # Pick first by relevance
    first = max(candidates_set, key=lambda i: norm_scores[i])
    selected.append(first)
    candidates_set.remove(first)
    
    while candidates_set and len(selected) < k:
        best_idx = None
        best_score = -float('inf')
        
        for i in candidates_set:
            rel = norm_scores[i]
            max_sim = max(sim(i, j) for j in selected)
            mmr = lambda_mult * rel - (1 - lambda_mult) * max_sim
            if mmr > best_score:
                best_score = mmr
                best_idx = i
        
        if best_idx is None:
            break
        selected.append(best_idx)
        candidates_set.remove(best_idx)
    
    return selected
```

---

## 6. Cross-Adapter Patterns

### 6.1. Unified Error Taxonomy Integration

All adapters map framework‑specific exceptions to the Corpus error taxonomy:

```python
try:
    result = await self._translator.arun_query(...)
except NotSupported as e:
    # Map to framework‑appropriate exception
    raise ValueError("Feature not supported") from e
except BadRequest as e:
    if e.code == "INVALID_QUERY":
        raise ValueError(f"Invalid query: {e}") from e
    raise
except Exception as e:
    attach_context(e, framework=self._framework_name, ...)
    raise
```

### 6.2. Consistent Observability

All adapters emit:
- One metric per operation (including streaming)
- Structured logs with `tenant_hash`, operation, namespace, top‑k, latency
- Distributed trace context via `traceparent`

### 6.3. Operation Context Propagation

Framework‑specific context flows into `OperationContext` via translation helpers:

```
framework_context → context_from_framework() → OperationContext
```

### 6.4. Idempotency Semantics

When `idempotency_key` is provided in operation context, adapters MUST ensure exactly‑once semantics for mutating operations (`add_texts`, `delete`). Read operations (`similarity_search`, `stream`) are naturally idempotent.

### 6.5. Partial Failure Reporting

Batch operations (`add_texts`) MAY experience partial failures. The adapter MUST handle these according to the following rules:

- If the underlying translator returns a structured result containing partial failures, the adapter MUST:
  - Return the list of successfully inserted IDs
  - Log each failure with sufficient detail (index, error code, message)
  - Not raise an exception unless all operations fail

```json
// Example log entry for partial failure
{
  "ok": true,
  "code": "PARTIAL_SUCCESS",
  "operation": "add_texts",
  "successful": 5,
  "failed": 1,
  "failures": [
    {
      "index": 3,
      "error": "EMBEDDING_FAILED",
      "detail": "Embedding service unavailable"
    }
  ]
}
```

### 6.6. Backpressure Integration

Adapters SHOULD:
- Surface `ResourceExhausted` with `retry_after_ms` when rate‑limited
- Include `throttle_scope` in error details
- Propagate backpressure hints from underlying provider

### 6.7. Vector Operation Determinism (REVISED)

Adapters MUST NOT introduce additional non‑determinism beyond what the underlying vector provider exhibits. For deterministic backends, adapters MUST preserve deterministic behavior (no extra randomness, stable ordering for equal scores, etc.).

- **Query equivalence:** For the same query string and top‑k, adapters MUST return results that are consistent with the underlying provider's output. If the provider itself is non‑deterministic (e.g., due to approximate nearest neighbor algorithms), adapters MUST NOT add extra randomness that could further vary results.

- **Mutation equivalence:** The same texts and metadata upserted MUST produce identical state changes across all adapters, subject to any provider‑specific eventual consistency guarantees.

- **Error equivalence:** The same invalid inputs MUST produce equivalent error types and codes across all adapters.

**Documentation Requirement for Non‑Deterministic Providers:**  
If the underlying vector provider is known to be non‑deterministic (e.g., approximate nearest neighbor, load‑balanced replicas), the adapter MUST include a clear statement in its public documentation explaining:
- The name of the provider and the source of non‑determinism.
- Whether the non‑determinism affects query results, mutation visibility, or only metadata (e.g., timing).
- Any configuration options that can mitigate non‑determinism (e.g., read‑after‑write consistency, increasing `k` to reduce variance).
- The practical impact on applications (e.g., retrieval may vary slightly between runs, mutations may not be immediately visible).

**Streaming chunk equivalence:** For streaming similarity search, adapters MUST produce results that are semantically equivalent to the non‑streaming query result (same set of documents and scores) regardless of chunk boundaries. Chunk boundaries MAY differ, but the concatenation of yielded documents MUST be identical across adapters when the provider is deterministic.

### 6.8. Translator Shim Equivalence (MUST)

The `VectorTranslator` and `VectorFrameworkTranslator` layers MUST ensure that observable behavior is **equivalent** regardless of which underlying vector adapter implementation is used. This means:

- Query results must have identical structure and content
- Error types and codes must be consistent
- Streaming chunk boundaries and content must match
- Batch operation results must report successes/failures identically

The conformance test suite includes tests that verify equivalence using mock vector adapters.

### 6.9. Single Source of Truth Pattern (SHOULD)

For complex request shapes (upsert, query), adapters SHOULD implement shared request builders (see §B.6). This prevents drift between sync and async implementations as specs evolve.

### 6.10. Delete Operation Helper Pattern

All adapters implement a shared helper for delete operation filter/ID selection (see §B.5).

```python
def _select_filter_or_ids(
    self,
    *,
    ids: Optional[List[str]],
    filter: Optional[Mapping[str, Any]],
    empty_message: str,
) -> Any:
    """
    Select either filter or non‑empty ID list for delete operations.
    
    - If filter is provided, return it
    - Otherwise, validate that ids is non‑empty and return ids
    - Raise BadRequest with empty_message if neither is valid
    """
    if filter is not None:
        return filter
    
    if ids and len(ids) > 0:
        return ids
    
    raise BadRequest(
        f"{empty_message} [INVALID_DELETE_SPEC]",
        code="BAD_ADAPTER_RESULT",
    )
```

This ensures consistent behavior across sync/async and different frameworks.

---

## 7. AutoGen Adapter Specification

### 7.1. Overview

The AutoGen adapter exposes Corpus vector operations as AutoGen‑friendly FunctionTool wrappers, enabling agent‑based vector search and retrieval. It solves the fundamental impedance mismatch between AutoGen's async agent runtime and synchronous vector operations.

### 7.2. Framework‑Specific Challenges

| Challenge | Solution |
|-----------|----------|
| AutoGen agents expect tool interfaces | `create_autogen_vector_tools()` produces FunctionTool wrappers |
| Context must propagate from conversation objects | `core_ctx_from_autogen()` extracts OperationContext |
| Tool execution may occur in async agent loops | Thread‑pool bridge for sync vector calls |
| Tool outputs must be JSON‑serializable | `_json_safe_snapshot()` with truncation limits |

### 7.3. Data Types

```python
class AutoGenDocument:
    """Simple document representation for AutoGen."""
    page_content: str
    metadata: Dict[str, Any]

class AutoGenContext(TypedDict, total=False):
    agent_name: Optional[str]
    conversation_id: Optional[str]
    workflow_type: Optional[str]
    retriever_name: Optional[str]
    request_id: Optional[str]
    user_id: Optional[str]
```

### 7.4. Core Class: `CorpusAutoGenVectorClient`

#### 7.4.1. AutoGen Compatibility Surface

```python
class CorpusAutoGenVectorClient:
    """
    AutoGen‑oriented client wrapper around a Corpus VectorProtocolV1.
    
    Translates AutoGen conversation objects into OperationContext
    and delegates all vector operations to VectorTranslator.
    """
```

#### 7.4.2. Initialization

```python
def __init__(
    self,
    adapter: Optional[VectorProtocolV1] = None,
    *,
    vector_adapter: Optional[VectorProtocolV1] = None,
    default_namespace: Optional[str] = None,
    default_top_k: int = 4,
    score_threshold: Optional[float] = None,
    embedding_function: Optional[Callable[[List[str]], Embeddings]] = None,
    async_embedding_function: Optional[Callable[[List[str]], Awaitable[Embeddings]]] = None,
    framework_version: Optional[str] = None,
    framework_translator: Optional[VectorFrameworkTranslator] = None,
):
    # Validate adapter has required methods
    # Store configuration
    # Initialize resource management flags
```

#### 7.4.3. Context Translation

```python
def _build_ctx(
    self,
    *,
    conversation: Optional[Any] = None,
    extra_context: Optional[Mapping[str, Any]] = None,
) -> Optional[OperationContext]:
    """Translate AutoGen conversation to OperationContext."""
    # Use core_ctx_from_autogen()
    # Enrich with framework metadata
    # Return None on failure (best‑effort)
```

#### 7.4.4. Operations

All standard vector operations as defined in §4, with `conversation` parameter for context propagation.

### 7.5. Integration Helpers

#### 7.5.1. `create_autogen_vector_tools()`

```python
def create_autogen_vector_tools(
    client: "CorpusAutoGenVectorClient",
    *,
    name_prefix: str = "vector",
    description_prefix: str = "Corpus vector tool",
) -> List[Any]:
    """
    Create AutoGen‑native FunctionTool wrappers for vector operations.
    
    - Lazy imports AutoGen
    - Creates async tools that bridge to sync client when needed
    - Returns JSON‑safe snapshots for tool compatibility
    """
```

### 7.6. Error Codes

```python
class ErrorCodes:
    BAD_OPERATION_CONTEXT = "BAD_OPERATION_CONTEXT"
    BAD_TRANSLATED_SCHEMA = "BAD_TRANSLATED_SCHEMA"
    BAD_HEALTH_RESULT = "BAD_HEALTH_RESULT"
    BAD_TRANSLATED_RESULT = "BAD_TRANSLATED_RESULT"
    BAD_TRANSLATED_CHUNK = "BAD_TRANSLATED_CHUNK"
    BAD_UPSERT_RESULT = "BAD_UPSERT_RESULT"
    BAD_DELETE_RESULT = "BAD_DELETE_RESULT"
    BAD_ADAPTER_RESULT = "BAD_ADAPTER_RESULT"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
    INVALID_QUERY = "INVALID_QUERY"
    BAD_ASYNC_ITERATOR_SHAPE = "BAD_ASYNC_ITERATOR_SHAPE"
    INVALID_DELETE_SPEC = "INVALID_DELETE_SPEC"
    BAD_EMBEDDINGS = "BAD_EMBEDDINGS"
    NO_EMBEDDING_FUNCTION = "NO_EMBEDDING_FUNCTION"
    EMBEDDING_ERROR = "EMBEDDING_ERROR"
    VECTOR_DIM_MISMATCH = "VECTOR_DIM_MISMATCH"
    UNKNOWN_VECTOR_DIMENSION = "UNKNOWN_VECTOR_DIMENSION"
    EMPTY_INPUT_DIM_UNKNOWN = "EMPTY_INPUT_DIM_UNKNOWN"
    BAD_MMR_LAMBDA = "BAD_MMR_LAMBDA"
    BAD_TOP_K = "BAD_TOP_K"
    FILTER_NOT_SUPPORTED = "FILTER_NOT_SUPPORTED"
    CAPABILITIES_NOT_AVAILABLE = "CAPABILITIES_NOT_AVAILABLE"
```

### 7.7. AutoGen‑Specific Context

The adapter extracts these fields from `conversation`:
- `agent_name` — Current agent identifier
- `conversation_id` — Active conversation
- `workflow_type` — Type of agent workflow
- `retriever_name` — Name of retriever component

Unknown fields are ignored.

---

## 8. CrewAI Adapter Specification

### 8.1. Overview

The CrewAI adapter exposes Corpus vector operations as CrewAI BaseTool wrappers, enabling role‑based agent teams to access vector data. It solves context propagation across agents that operate without a shared runtime.

### 8.2. Framework‑Specific Challenges

| Challenge | Solution |
|-----------|----------|
| No shared runtime context across agents | Extract context from per‑call `task` parameter |
| Tool execution in async agent loops | Bounded thread pool with `_run_blocking_in_crewai_tool_thread()` |
| LLM‑provided parameters need validation | `coerce_bounded_positive_int()` for k, fetch_k (see §5.1.6) |
| Tool outputs must be JSON strings | `_json_result()` with size bounds and fallback truncation |

### 8.3. Data Types

```python
class CrewAIContext(TypedDict, total=False):
    agent_role: Optional[str]
    task_id: Optional[str]
    workflow: Optional[str]
    agent_id: Optional[str]
    crew_id: Optional[str]
    process_id: Optional[str]
```

### 8.4. Core Class: `CorpusCrewAIVectorClient`

#### 8.4.1. Initialization

```python
def __init__(
    self,
    adapter: Optional[VectorProtocolV1] = None,
    *,
    vector_adapter: Optional[VectorProtocolV1] = None,
    default_namespace: Optional[str] = None,
    default_top_k: int = 4,
    score_threshold: Optional[float] = None,
    embedding_function: Optional[Callable[[List[str]], Embeddings]] = None,
    async_embedding_function: Optional[Callable[[List[str]], Awaitable[Embeddings]]] = None,
    framework_version: Optional[str] = None,
    framework_translator: Optional[VectorFrameworkTranslator] = None,
):
    # Standard initialization
    # Set up resource management flags
```

#### 8.4.2. Task Context Translation

```python
def _build_ctx(
    self,
    *,
    task: Optional[Any] = None,
    extra_context: Optional[Mapping[str, Any]] = None,
) -> Optional[OperationContext]:
    """Translate CrewAI Task to OperationContext."""
    # Use core_ctx_from_crewai()
    # Enrich with framework metadata
    # Return None on failure
```

#### 8.4.3. Operations

All standard vector operations as defined in §4, with `task` parameter for context propagation.

#### 8.4.4. Tool Bridge Executor

```python
_CREWAI_TOOL_BRIDGE_EXECUTOR: Optional[ThreadPoolExecutor] = None
_CREWAI_TOOL_BRIDGE_EXECUTOR_LOCK = threading.Lock()

def _run_blocking_in_crewai_tool_thread(fn: Callable[[], T]) -> T:
    """Run sync function in bounded thread pool when called from event loop."""
    global _CREWAI_TOOL_BRIDGE_EXECUTOR
    with _CREWAI_TOOL_BRIDGE_EXECUTOR_LOCK:
        if _CREWAI_TOOL_BRIDGE_EXECUTOR is None:
            # Use a custom thread factory for daemon threads if needed
            _CREWAI_TOOL_BRIDGE_EXECUTOR = ThreadPoolExecutor(
                max_workers=4,
                thread_name_prefix="corpus-crewai-tool",
            )
        executor = _CREWAI_TOOL_BRIDGE_EXECUTOR
    
    return executor.submit(fn).result()
```

### 8.5. Integration Helpers

#### 8.5.1. `create_crewai_vector_tools()`

```python
def create_crewai_vector_tools(
    client: "CorpusCrewAIVectorClient",
    *,
    name_prefix: str = "vector",
    description_prefix: str = "Corpus vector tool",
) -> List[Any]:
    """
    Create CrewAI‑native BaseTool wrappers for vector operations.
    
    - Lazy imports CrewAI
    - Provides both _run (sync) and _arun (async) implementations
    - Uses thread pool for sync‑in‑async safety
    - For numeric parameters k and fetch_k, uses `validated_k()` and `validated_fetch_k()` (see §5.1.6)
    - Returns JSON strings with size bounds
    """
```

### 8.6. Error Codes

Same as AutoGen adapter (see §7.6), with framework label "crewai".

### 8.7. CrewAI‑Specific Context

The adapter extracts from `task`:
- `agent_role` — Role of the current agent
- `task_id` — Current task identifier
- `workflow` — Workflow name
- `agent_id` — Agent instance identifier
- `crew_id` — Crew identifier
- `process_id` — Process identifier

Unknown fields are ignored.

---

## 9. LangChain Adapter Specification

### 9.1. Overview

The LangChain adapter exposes Corpus vector operations as LangChain BaseTool wrappers, enabling vector access in LangChain agents and chains. It solves the production problem of sync methods called from async contexts and LLM‑provided parameter validation.

### 9.2. Framework‑Specific Challenges

| Challenge | Solution |
|-----------|----------|
| Sync methods called from async agent runtimes | Event loop detection + worker thread bridge |
| LLM‑provided parameters may be malformed | `validated_k()`, `validated_fetch_k()` with coercion and clamping (see §5.1.6) |
| Tool outputs must be JSON strings | `_json_result()` with size bounds |
| Multiple LangChain versions have different tool imports | Soft import with fallback paths |
| Config objects vary across versions | Structural context extraction |

### 9.3. Data Types

```python
class LangChainContext(TypedDict, total=False):
    run_id: Optional[str]
    run_name: Optional[str]
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    configurable: Optional[Dict[str, Any]]
```

### 9.4. Core Class: `CorpusLangChainVectorClient`

#### 9.4.1. Initialization

```python
def __init__(
    self,
    *,
    vector_adapter: Optional[VectorProtocolV1] = None,
    adapter: Optional[VectorProtocolV1] = None,
    default_namespace: Optional[str] = None,
    default_top_k: int = 4,
    score_threshold: Optional[float] = None,
    embedding_function: Optional[Callable[[List[str]], Embeddings]] = None,
    async_embedding_function: Optional[Callable[[List[str]], Awaitable[Embeddings]]] = None,
    framework_version: Optional[str] = None,
    framework_translator: Optional[VectorFrameworkTranslator] = None,
):
    # Standard initialization with adapter/vector_adapter resolution
    # Note: adapter.close() may return coroutine; handled in close()
```

#### 9.4.2. Config Context Translation

```python
def _build_ctx(
    self,
    *,
    config: Optional[Mapping[str, Any]] = None,
    extra_context: Optional[Mapping[str, Any]] = None,
) -> Optional[OperationContext]:
    """Translate LangChain config to OperationContext."""
    # Use core_ctx_from_langchain()
    # Enrich with framework metadata
    # Handle both RunnableConfig and older dict formats
```

#### 9.4.3. Event Loop Safety

```python
def close(self) -> None:
    """Handle adapters that may return coroutine from close()."""
    if self._closed:
        return
    self._closed = True
    
    close_fn = getattr(self._vector, "close", None)
    if callable(close_fn):
        try:
            result = close_fn()
            if inspect.iscoroutine(result):
                result.close()  # Suppress "never awaited" warning
                logger.warning("Adapter has async‑only close() - use aclose()")
        except Exception as e:
            logger.warning("Error closing vector adapter: %s", e)
```

#### 9.4.4. Operations

All standard vector operations as defined in §4, with `config` parameter for context propagation.

#### 9.4.5. Tool Bridge Executor

Same pattern as CrewAI (§8.4.4) but with `_LANGCHAIN_TOOL_BRIDGE_EXECUTOR`.

### 9.5. Integration Helpers

#### 9.5.1. `create_langchain_vector_tools()`

```python
def create_langchain_vector_tools(
    client: CorpusLangChainVectorClient,
    *,
    name_prefix: str = "vector",
    description_prefix: str = "Corpus vector tool",
) -> List[Any]:
    """
    Create LangChain‑native BaseTool wrappers for vector operations.
    
    - Lazy imports LangChain BaseTool
    - Provides _run (sync) and _arun (async) implementations
    - Validates LLM‑provided parameters with `validated_k()` and `validated_fetch_k()` (see §5.1.6)
    - Returns JSON strings with size bounds
    """
```

#### 9.5.2. `create_corpus_vector_tool()`

```python
def create_corpus_vector_tool(
    *,
    vector_adapter: VectorProtocolV1,
    default_namespace: Optional[str] = None,
    default_top_k: int = 4,
    score_threshold: Optional[float] = None,
    embedding_function: Optional[Callable[[List[str]], Embeddings]] = None,
    async_embedding_function: Optional[Callable[[List[str]], Awaitable[Embeddings]]] = None,
    framework_version: Optional[str] = None,
    name: str = "corpus_vector",
    description: Optional[str] = None,
    framework_translator: Optional[VectorFrameworkTranslator] = None,
) -> Any:
    """
    Convenience factory: creates client and returns single similarity search tool.
    
    Maintains backward compatibility with older single‑tool pattern.
    """
```

### 9.6. Error Codes

Same as AutoGen adapter (see §7.6), with framework label "langchain".

### 9.7. LangChain‑Specific Context

The adapter extracts from `config`:
- `run_id` — LangChain run identifier
- `run_name` — Run name
- `tags` — Snapshotted for observability
- `metadata` — Snapshotted for observability
- `configurable` — Snapshotted for observability

Unknown fields are ignored.

---

## 10. LlamaIndex Adapter Specification

### 10.1. Overview

The LlamaIndex adapter implements the `VectorStore` protocol, enabling Corpus vectors to be used in LlamaIndex indices. It solves the problem of embedding integration and callback propagation.

### 10.2. Framework‑Specific Challenges

| Challenge | Solution |
|-----------|----------|
| `VectorStore` expects nodes with embeddings | `nodes_to_corpus_vectors()` maps LlamaIndex nodes to Corpus Vectors |
| Callback manager must propagate to operations | `core_ctx_from_llamaindex()` extracts context |
| Async streaming may return awaitable→AsyncIterator | `_normalize_async_iterator()` handles both forms |
| Persist operation expected but vector store is remote | No‑op by default, overridable |

### 10.3. Data Types

```python
class LlamaIndexContext(TypedDict, total=False):
    node_ids: Optional[List[str]]
    index_id: Optional[str]
    callback_manager: Optional[Any]
    trace_id: Optional[str]
    workflow: Optional[str]
```

### 10.4. Core Class: `CorpusLlamaIndexVectorClient`

#### 10.4.1. Initialization

```python
def __init__(
    self,
    adapter: Optional[VectorProtocolV1] = None,
    *,
    vector_adapter: Optional[VectorProtocolV1] = None,
    default_namespace: Optional[str] = None,
    default_top_k: int = 4,
    score_threshold: Optional[float] = None,
    embedding_function: Optional[Callable[[List[str]], Embeddings]] = None,
    async_embedding_function: Optional[Callable[[List[str]], Awaitable[Embeddings]]] = None,
    framework_version: Optional[str] = None,
    framework_translator: Optional[VectorFrameworkTranslator] = None,
):
    # Standard initialization
    # Set up resource management flags
```

#### 10.4.2. Callback Manager Context Translation

```python
def _build_ctx(
    self,
    *,
    callback_manager: Optional[Any] = None,
    extra_context: Optional[Mapping[str, Any]] = None,
) -> Optional[OperationContext]:
    """Translate LlamaIndex CallbackManager to OperationContext."""
    # Use core_ctx_from_llamaindex()
    # Enrich with framework metadata
    # Return None on failure
```

#### 10.4.3. Operations

All standard vector operations as defined in §4, with `callback_manager` parameter for context propagation.

#### 10.4.4. Single Source of Truth Request Builders

```python
def _build_upsert_request(
    self,
    nodes: Sequence[BaseNode],
    namespace: Optional[str],
) -> List[Mapping[str, Any]]:
    """Convert nodes to Corpus upsert documents."""
    # Implementation details (see §B.6)

def _build_query_request(...) -> Mapping[str, Any]:
    """Build query request from VectorStoreQuery."""
    # Implementation details (see §B.6)
```

### 10.5. Integration Helpers

#### 10.5.1. `CorpusVectorIndex`

```python
class CorpusVectorIndex(_LlamaIndexVectorStore):
    """
    LlamaIndex VectorStore implementation backed by CorpusLlamaIndexVectorClient.
    
    Maps LlamaIndex Node objects to Corpus vectors and handles embedding integration.
    """
    
    def __init__(
        self,
        client: "CorpusLlamaIndexVectorClient",
        *,
        namespace: Optional[str] = None,
    ):
        """Initialize with client and optional default namespace."""
        self._client = client
        self._namespace = namespace
    
    def add(self, nodes: List[BaseNode], **kwargs) -> List[str]:
        """Add nodes to vector store."""
        return self._client.add_nodes(nodes, namespace=self._namespace, **kwargs)
    
    def delete(self, ref_doc_id: str, **kwargs) -> None:
        """Delete nodes by ref_doc_id."""
        self._client.delete(ref_doc_id=ref_doc_id, namespace=self._namespace, **kwargs)
    
    def query(self, query: VectorStoreQuery, **kwargs) -> VectorStoreQueryResult:
        """Execute similarity search."""
        return self._client.query(query, namespace=self._namespace, **kwargs)
    
    # Optional streaming and MMR methods as extensions
    def query_stream(self, query: VectorStoreQuery, **kwargs) -> Iterator[NodeWithScore]:
        return self._client.query_stream(query, namespace=self._namespace, **kwargs)
    
    def query_mmr(self, query: VectorStoreQuery, **kwargs) -> VectorStoreQueryResult:
        return self._client.query_mmr(query, namespace=self._namespace, **kwargs)
```

### 10.6. Error Codes

Same as AutoGen adapter (see §7.6), with framework label "llamaindex".

### 10.7. LlamaIndex‑Specific Context

The adapter extracts from `callback_manager`:
- `node_ids` — IDs of nodes being processed
- `index_id` — Index identifier
- `trace_id` — Tracing identifier
- `workflow` — Workflow name
- `has_callback_manager` — Boolean flag

Unknown fields are ignored.

---

## 11. Semantic Kernel Adapter Specification

### 11.1. Overview

The Semantic Kernel adapter exposes Corpus vector operations as SK plugins, enabling vector access in Semantic Kernel applications. It solves the problem of context propagation from SK's dual context/settings objects.

### 11.2. Framework‑Specific Challenges

| Challenge | Solution |
|-----------|----------|
| Context comes from both context and settings objects | `core_ctx_from_semantic_kernel()` handles both |
| Capabilities methods may evolve with new parameters | Forward kwargs with graceful TypeError fallback |
| Plugin architecture requires thin wrapper | `CorpusSemanticKernelVectorPlugin` passthrough layer |
| Async streaming may return awaitable→AsyncIterator | `_normalize_async_iterator()` handles both forms |

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

### 11.4. Core Class: `CorpusSemanticKernelVectorClient`

#### 11.4.1. Initialization

```python
def __init__(
    self,
    adapter: Optional[VectorProtocolV1] = None,
    *,
    vector_adapter: Optional[VectorProtocolV1] = None,
    default_namespace: Optional[str] = None,
    default_top_k: int = 4,
    score_threshold: Optional[float] = None,
    embedding_function: Optional[Callable[[List[str]], Embeddings]] = None,
    async_embedding_function: Optional[Callable[[List[str]], Awaitable[Embeddings]]] = None,
    framework_version: Optional[str] = None,
    framework_translator: Optional[VectorFrameworkTranslator] = None,
):
    # Standard initialization
    # Set up resource management flags
```

#### 11.4.2. Context + Settings Translation

```python
def _build_ctx(
    self,
    *,
    context: Optional[Any] = None,
    settings: Optional[Any] = None,
    extra_context: Optional[Mapping[str, Any]] = None,
) -> Optional[OperationContext]:
    """Translate Semantic Kernel context and settings to OperationContext."""
    # Use core_ctx_from_semantic_kernel()
    # Enrich with framework metadata
    # Return None on failure
```

#### 11.4.3. Operations

All standard vector operations as defined in §4, with `context` and `settings` parameters for context propagation.

#### 11.4.4. Forward‑Compatible Kwargs Handling

```python
@with_vector_error_context("capabilities_sync")
def capabilities(self, **kwargs: Any) -> Mapping[str, Any]:
    """
    Sync capabilities with forward‑compatible kwargs handling.
    
    Attempts to pass kwargs to translator; falls back gracefully if not supported.
    """
    _ensure_not_in_event_loop("capabilities")
    
    try:
        caps = self._translator.capabilities(**kwargs)
    except TypeError:
        if kwargs:
            logger.debug("VectorTranslator.capabilities does not accept kwargs; ignoring")
        caps = self._translator.capabilities()
    
    return vector_capabilities_to_dict(caps)
```

### 11.5. Integration Helpers

#### 11.5.1. `CorpusSemanticKernelVectorPlugin`

```python
class CorpusSemanticKernelVectorPlugin:
    """
    Semantic Kernel plugin wrapper backed by CorpusSemanticKernelVectorClient.
    
    Provides passthrough methods for all vector operations with consistent
    namespace resolution and context propagation.
    """
    
    def __init__(
        self,
        client: "CorpusSemanticKernelVectorClient",
        *,
        namespace: Optional[str] = None,
    ):
        """Initialize with client and optional default namespace."""
        self._client = client
        self._namespace = namespace
    
    @kernel_function(
        name="vector_search",
        description="Search for semantically similar documents."
    )
    async def vector_search(
        self,
        query: str,
        k: int = 4,
        *,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        context: Optional[Any] = None,
        settings: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic search passthrough."""
        effective_namespace = namespace if namespace is not None else self._namespace
        return await self._client.asimilarity_search(
            query,
            k=k,
            filter=filter,
            namespace=effective_namespace,
            context=context,
            settings=settings,
        )
    
    @kernel_function(
        name="vector_search_stream",
        description="Streaming similarity search."
    )
    def vector_search_stream(
        self,
        query: str,
        k: int = 4,
        *,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        context: Optional[Any] = None,
        settings: Optional[Any] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Streaming search passthrough."""
        effective_namespace = namespace if namespace is not None else self._namespace
        yield from self._client.similarity_search_stream(
            query,
            k=k,
            filter=filter,
            namespace=effective_namespace,
            context=context,
            settings=settings,
        )
    
    @kernel_function(
        name="vector_mmr_search",
        description="MMR search for diverse results."
    )
    async def vector_mmr_search(
        self,
        query: str,
        k: int = 4,
        lambda_mult: float = 0.5,
        *,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        context: Optional[Any] = None,
        settings: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """MMR search passthrough."""
        effective_namespace = namespace if namespace is not None else self._namespace
        return await self._client.amax_marginal_relevance_search(
            query,
            k=k,
            lambda_mult=lambda_mult,
            filter=filter,
            namespace=effective_namespace,
            context=context,
            settings=settings,
        )
    
    @kernel_function(
        name="vector_store_document",
        description="Store a document in the vector index."
    )
    async def vector_store_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None,
        namespace: Optional[str] = None,
        context: Optional[Any] = None,
        settings: Optional[Any] = None,
    ) -> str:
        """Store a single document."""
        effective_namespace = namespace if namespace is not None else self._namespace
        ids = await self._client.aadd_texts(
            [text],
            metadatas=[metadata or {}],
            ids=[document_id] if document_id else None,
            namespace=effective_namespace,
            context=context,
            settings=settings,
        )
        return ids[0] if ids else ""
    
    @kernel_function(
        name="vector_get_capabilities",
        description="Get information about vector store capabilities."
    )
    async def vector_get_capabilities(
        self,
        context: Optional[Any] = None,
        settings: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Capabilities passthrough."""
        return await self._client.acapabilities(context=context, settings=settings)
```

### 11.6. Error Codes

Same as AutoGen adapter (see §7.6), with framework label "semantic_kernel".

### 11.7. Semantic Kernel‑Specific Context

The adapter extracts from `context` and `settings`:
- `plugin_name` — Name of the calling plugin
- `function_name` — Name of the calling function
- `kernel_id` — Kernel identifier
- `memory_type` — Type of memory operation
- `request_id` — Request identifier
- `user_id` — User identifier
- `execution_settings` — Snapshotted for observability

Unknown fields are ignored.

---

## 12. Error Handling and Resilience

### 12.1. Error Code Mapping Table (Normative)

| Corpus Error Code | Framework Adapter Mapping | Retryable |
|-------------------|--------------------------|-----------|
| `BAD_OPERATION_CONTEXT` | Log warning, continue without context | No |
| `BAD_TRANSLATED_SCHEMA` | Raise TypeError with context | No |
| `BAD_HEALTH_RESULT` | Raise TypeError with details | No |
| `BAD_TRANSLATED_RESULT` | Raise TypeError with details | No |
| `BAD_TRANSLATED_CHUNK` | Raise TypeError with details | No |
| `BAD_UPSERT_RESULT` | Raise TypeError with details | No |
| `BAD_DELETE_RESULT` | Raise TypeError with details | No |
| `BAD_ADAPTER_RESULT` | Raise BadRequest with context | No |
| `SYNC_WRAPPER_CALLED_IN_EVENT_LOOP` | Raise RuntimeError | No |
| `INVALID_QUERY` | Raise ValueError | No |
| `BAD_ASYNC_ITERATOR_SHAPE` | Raise TypeError | No |
| `INVALID_DELETE_SPEC` | Raise BadRequest | No |
| `BAD_EMBEDDINGS` | Raise BadRequest | No |
| `NO_EMBEDDING_FUNCTION` | Raise NotSupported | No |
| `EMBEDDING_ERROR` | Raise BadRequest with context | Maybe (if transient) |
| `VECTOR_DIM_MISMATCH` | Raise BadRequest | No |
| `UNKNOWN_VECTOR_DIMENSION` | Raise BadRequest | No |
| `EMPTY_INPUT_DIM_UNKNOWN` | Raise BadRequest | No |
| `BAD_MMR_LAMBDA` | Raise ValueError | No |
| `BAD_TOP_K` | Raise ValueError | No |
| `FILTER_NOT_SUPPORTED` | Raise NotSupported | No |
| `CAPABILITIES_NOT_AVAILABLE` | Raise NotSupported | No |

### 12.2. Retry Semantics

Adapters MUST NOT retry automatically unless configured to do so. When retrying:
- Honor `retry_after_ms` if present
- Use exponential backoff with jitter
- Do not retry validation errors (INVALID_* codes)
- Consider per‑tenant retry budgets

### 12.3. Circuit Breaking Guidance

Implementations MAY implement circuit breakers:
- Open on repeated Unavailable or ResourceExhausted
- Half‑open after configured timeout
- Per‑tenant, per‑operation circuits RECOMMENDED

---

## 13. Observability and Monitoring

### 13.1. Metrics Taxonomy (MUST)

All adapters MUST expose:

```
vector_operations_total{framework,operation,namespace,code}
vector_latency_ms{framework,operation,namespace,quantile}
vector_batch_size{framework,operation}  # histogram
vector_stream_chunks_total{framework,operation}
vector_dimension{framework,namespace}  # gauge for dimension hint
vector_top_k{framework,operation}  # histogram of requested k
```

### 13.2. Structured Logging (MUST)

```json
{
  "timestamp": "2026-02-26T10:00:00Z",
  "level": "INFO",
  "framework": "langchain",
  "operation": "similarity_search",
  "tenant_hash": "a1b2c3...",
  "trace_id": "00-4bf9...",
  "namespace": "production",
  "query_len": 156,
  "top_k": 4,
  "latency_ms": 127.4,
  "code": "OK"
}
```

### 13.3. Distributed Tracing (SHOULD)

- Propagate `traceparent` from operation context
- Create spans for each vector operation
- Include attributes: `framework`, `operation`, `namespace`, `tenant_hash`, `top_k`
- Final span status matches operation outcome

---

## 14. Security Considerations

### 14.1. Tenant Isolation (MUST)

- `tenant` in operation context MUST be used for isolation
- Never log raw tenant identifiers; use `tenant_hash`
- Caches MUST key by `tenant_hash` when `cache_scope="tenant"`

### 14.2. Credential Handling (MUST)

- Credentials for underlying vector adapters provisioned out‑of‑band
- Never log, snapshot, or expose credentials in error context

### 14.3. Log Redaction (MUST)

- All logs use `_safe_snapshot()` for object serialization
- Strings >64 bytes replaced with hash + length
- No raw query text, parameters, or vectors in logs
- Tenant identifiers always hashed

---

## 15. Performance Characteristics

### 15.1. Latency Targets (Indicative)

| Operation Type | Typical Range | Notes |
|----------------|---------------|-------|
| Simple similarity search | 10–100 ms | Depends on index size and complexity |
| Add texts (batch of 10) | 50–200 ms | Includes embedding generation |
| Streaming search | First chunk: 10–50 ms | Subsequent chunks streaming rate |
| MMR search | 2× fetch_k query time | Additional MMR computation |
| Capabilities/Health | 1–10 ms | Cached where possible |

### 15.2. Concurrency Considerations

- All adapters are thread‑safe for concurrent use
- Translator initialized lazily with locks
- Resource cleanup safe under concurrent access
- Tool bridge executors bounded (max_workers=4)

### 15.3. Caching Strategies

- Capabilities can be cached with TTL
- Query results cacheable by `(namespace, query_text, top_k, params_hash)`
- Cache keys MUST include `tenant_hash`
- Respect `cache_scope` and `cache_tags` when provided
- Never cache across tenant boundaries

---

## 16. Implementation Guidelines

### 16.1. Adapter Implementation Order

1. Copy shared utilities from existing adapter
2. Implement `__init__` with validation
3. Add error context decorators
4. Implement core vector methods (similarity_search, stream, add_texts, delete)
5. Add context extraction and building
6. Implement resource management (including lifecycle state)
7. Add validation helpers (`_validate_top_k`, `_validate_embeddings`, `_select_filter_or_ids`)
8. Add Single Source of Truth request builders
9. Implement embedding helpers (`_ensure_embeddings`, `_embed_query`)
10. Implement MMR helpers
11. Write integration helpers (tools, plugins, stores)
12. Write conformance tests

### 16.2. Validation Requirements (MUST)

- Validate adapter has required methods (`query`, `capabilities`)
- Validate query strings are non‑empty
- Validate top‑k is positive integer
- Validate embedding batch shapes and dimensions
- Validate metadata normalization
- Validate IDs normalization
- Validate delete specs have either filter or non‑empty ids
- Validate MMR lambda in [0,1]
- Validate numeric parameters from LLMs using `coerce_bounded_positive_int()` (see §5.1.6)

### 16.3. Testing

#### 16.3.1. Conformance Test Suite

Each adapter MUST pass:
- Operation method coverage (all sync/async pairs)
- Error context attachment tests
- Context building tests (including failure cases)
- Batch operation tests (empty, single, multiple)
- Streaming tests (sync and async)
- Event loop guard tests
- Resource cleanup tests (including lifecycle state transitions)
- Namespace resolution tests (precedence rules)
- Delete operation helper tests
- Async iterator normalization tests
- Embedding function tests (sync/async, empty‑input hardening)
- Dimension hint management tests
- MMR selection tests

#### 16.3.2. Framework‑Specific Tests

- **AutoGen:** Tool creation, conversation context extraction, thread pool bridge
- **CrewAI:** Task context extraction, tool bridge executor, parameter coercion using `validated_k()`
- **LangChain:** Config context extraction, close() coroutine handling, tool creation, parameter coercion using `validated_k()`
- **LlamaIndex:** Callback manager context, VectorStore interface, streaming integration
- **Semantic Kernel:** Context+settings translation, kwargs forwarding, plugin wrapper

#### 16.3.3. Cross‑Adapter Tests

- All adapters produce identical results for same inputs (see §6.7)
- Error codes consistent across frameworks
- Observability fields follow same patterns
- Lifecycle behavior (close, use after close) consistent
- Namespace resolution identical across all

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
- Corpus Vector Protocol V1.0 Specification
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
| AutoGen | Agent tool interfaces + async/sync bridging | FunctionTool wrappers + thread pool bridge |
| CrewAI | No shared runtime context + LLM parameter safety | Task context extraction + parameter coercion |
| LangChain | Config evolution + sync‑in‑async deadlocks | Structural context extraction + worker thread bridge |
| LlamaIndex | Node‑based interface + callback propagation | Node↔Vector mapping + callback manager translation |
| Semantic Kernel | Dual context/settings + forward compatibility | Combined translation + kwargs fallback |

---

## Appendix B — Code Pattern Catalog (Normative)

### B.1. Context Building Patterns

```python
# Framework‑specific context building
def _build_ctx(self, *, framework_input=None, extra_context=None):
    try:
        ctx = core_ctx_from_framework(framework_input, **extra_context)
    except Exception:
        logger.warning("Context translation failed")
        return None
    
    if not _looks_like_operation_context(ctx):
        return None
    
    # Enrich with framework metadata
    attrs = getattr(ctx, "attrs", {})
    attrs.setdefault("framework", self._framework_name)
    return ctx
```

### B.2. Event Loop Safety Patterns

```python
# Guard pattern
_ensure_not_in_event_loop("sync_method")

# Tool bridge pattern (bounded thread pool)
def _run_in_tool_thread(fn):
    return _TOOL_BRIDGE_EXECUTOR.submit(fn).result()

# Close coroutine handling
result = close_fn()
if inspect.iscoroutine(result):
    result.close()  # Suppress warning
    logger.warning("Use aclose() for async close")
```

### B.3. Async Streaming Normalization Patterns

```python
# Normalize translator return shapes
aiter_or_awaitable = translator.arun_query_stream(...)
normalized = _normalize_async_iterator(aiter_or_awaitable)

if inspect.isawaitable(normalized):
    aiter = await normalized
else:
    aiter = normalized

if not _is_async_iterator(aiter):
    raise TypeError("Invalid stream shape")

async for chunk in aiter:
    yield chunk
```

### B.4. Resource Cleanup Patterns

```python
# Sync cleanup with idempotency and lock
def close(self):
    with self._close_lock:
        if self._closed:
            return
        self._closed = True
    _maybe_close_sync(self._resource)

# Async cleanup with fallback and lock
async def aclose(self):
    async with self._aclose_lock:
        if self._aclosed:
            return
        self._aclosed = True
    
    if hasattr(self._resource, "aclose"):
        await self._resource.aclose()
        self._closed = True
        return
    
    self.close()
```

### B.5. Delete Operation Helper Patterns

```python
# Shared filter/ID selection
def _select_filter_or_ids(self, *, ids, filter, empty_message):
    if filter is not None:
        return filter
    
    if ids and len(ids) > 0:
        return ids
    
    raise BadRequest(f"{empty_message} [INVALID_DELETE_SPEC]")
```

### B.6. Single Source of Truth Request Builders

```python
# Upsert request builder
def _build_upsert_request(self, texts, embeddings, metadatas, ids, namespace):
    documents = []
    for text, emb, meta, vid in zip(texts, embeddings, metadatas, ids):
        documents.append({
            "id": vid,
            "vector": [float(x) for x in emb],
            "metadata": meta,
            "namespace": namespace,
        })
    return documents

# Query request builder  
def _build_query_request(self, embedding, k, namespace, filter, include_vectors):
    return {
        "vector": [float(x) for x in embedding],
        "top_k": k,
        "namespace": namespace,
        "filters": filter,
        "include_metadata": True,
        "include_vectors": include_vectors,
    }
```

### B.7. MMR Implementation Patterns

```python
def mmr_select_indices(query_vec, candidates, k, lambda_mult):
    if k <= 0 or not candidates:
        return []
    
    if lambda_mult >= 1.0:
        # Pure relevance
        scores = [c.score for c in candidates]
        return sorted(range(len(candidates)), key=lambda i: scores[i], reverse=True)[:k]
    
    scores = [c.score for c in candidates]
    max_score = max(scores) if scores else 1.0
    norm_scores = [s / max_score for s in scores]
    
    # Similarity cache
    sim_cache = {}
    def sim(i, j):
        key = (min(i,j), max(i,j))
        if key not in sim_cache:
            a = candidates[i].vector.vector
            b = candidates[j].vector.vector
            sim_cache[key] = cosine_similarity(a, b) if a and b else 0.0
        return sim_cache[key]
    
    selected = []
    candidates_set = set(range(len(candidates)))
    
    # Pick first by relevance
    first = max(candidates_set, key=lambda i: norm_scores[i])
    selected.append(first)
    candidates_set.remove(first)
    
    while candidates_set and len(selected) < k:
        best_idx = None
        best_score = -float('inf')
        
        for i in candidates_set:
            rel = norm_scores[i]
            max_sim = max(sim(i, j) for j in selected)
            mmr = lambda_mult * rel - (1 - lambda_mult) * max_sim
            if mmr > best_score:
                best_score = mmr
                best_idx = i
        
        if best_idx is None:
            break
        selected.append(best_idx)
        candidates_set.remove(best_idx)
    
    return selected
```

---

## Appendix C — End‑to‑End Usage Examples

### C.1. AutoGen Agent with Vector Tools

```python
from corpus_sdk.vector.framework_adapters.autogen import (
    CorpusAutoGenVectorClient,
    create_autogen_vector_tools,
)
from autogen_agentchat.agents import AssistantAgent

# Create client with embedding function
client = CorpusAutoGenVectorClient(
    vector_adapter=my_vector_adapter,
    default_namespace="production",
    embedding_function=my_embed_fn,
)

# Create tools
tools = create_autogen_vector_tools(
    client,
    name_prefix="knowledge",
    description_prefix="Vector search operations"
)

# Use in agent
agent = AssistantAgent(
    name="vector_agent",
    tools=tools,
    model_client=model_client,
)
```

### C.2. CrewAI Crew with Vector Tools

```python
from corpus_sdk.vector.framework_adapters.crewai import (
    CorpusCrewAIVectorClient,
    create_crewai_vector_tools,
)
from crewai import Agent, Crew

client = CorpusCrewAIVectorClient(
    vector_adapter=my_vector_adapter,
    default_namespace="analytics",
    embedding_function=my_embed_fn,
)

tools = create_crewai_vector_tools(
    client,
    name_prefix="vector",
    description_prefix="Vector database operations"
)

agent = Agent(
    role="Knowledge Retriever",
    goal="Find relevant information using vector search",
    backstory="I specialize in semantic search",
    tools=tools,
)

crew = Crew(agents=[agent], tasks=[...])
```

### C.3. LangChain Agent with Vector Tools

```python
from corpus_sdk.vector.framework_adapters.langchain import (
    CorpusLangChainVectorClient,
    create_langchain_vector_tools,
)
from langchain.agents import AgentExecutor, create_openai_tools_agent

client = CorpusLangChainVectorClient(
    vector_adapter=my_vector_adapter,
    default_namespace="research",
    embedding_function=my_embed_fn,
)

tools = create_langchain_vector_tools(
    client,
    name_prefix="knowledge",
    description_prefix="Semantic search"
)

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)
```

### C.4. LlamaIndex Vector Index

```python
from corpus_sdk.vector.framework_adapters.llamaindex import (
    CorpusLlamaIndexVectorClient,
    CorpusVectorIndex,
)
from llama_index.core import VectorStoreIndex, Document

client = CorpusLlamaIndexVectorClient(
    vector_adapter=my_vector_adapter,
    default_namespace="kg",
)

vector_store = CorpusVectorIndex(client, namespace="docs")

# Create index from documents (LlamaIndex will embed)
documents = [Document(text="Hello world")]
index = VectorStoreIndex.from_documents(
    documents,
    vector_store=vector_store,
    embed_model=my_embed_model,  # LlamaIndex embedding model
)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("hello")
```

### C.5. Semantic Kernel Plugin Registration

```python
from corpus_sdk.vector.framework_adapters.semantic_kernel import (
    CorpusSemanticKernelVectorClient,
    CorpusSemanticKernelVectorPlugin,
)
import semantic_kernel as sk

client = CorpusSemanticKernelVectorClient(
    vector_adapter=my_vector_adapter,
    default_namespace="enterprise",
    embedding_function=my_embed_fn,
)

plugin = CorpusSemanticKernelVectorPlugin(client, namespace="enterprise")

kernel = sk.Kernel()
kernel.add_plugin(plugin, plugin_name="vector")

# Use in semantic function
result = await kernel.run_async(
    kernel.create_semantic_function(
        "Find documents about {{$input}} using vector.vector_search"
    ),
    input="machine learning"
)
```

---

## Appendix D — Error Code Reference

| Code | Description | Frameworks |
|------|-------------|------------|
| `BAD_OPERATION_CONTEXT` | Failed to build OperationContext | All |
| `BAD_TRANSLATED_SCHEMA` | Schema result has wrong type | All |
| `BAD_HEALTH_RESULT` | Health result not a mapping | All |
| `BAD_TRANSLATED_RESULT` | Query result has wrong type | All |
| `BAD_TRANSLATED_CHUNK` | Query chunk has wrong type | All |
| `BAD_UPSERT_RESULT` | Upsert result has wrong type | All |
| `BAD_DELETE_RESULT` | Delete result has wrong type | All |
| `BAD_ADAPTER_RESULT` | Adapter returned invalid data | All |
| `SYNC_WRAPPER_CALLED_IN_EVENT_LOOP` | Sync method called from async context | All |
| `INVALID_QUERY` | Query validation failed | All |
| `BAD_ASYNC_ITERATOR_SHAPE` | Async stream returned invalid shape | All |
| `INVALID_DELETE_SPEC` | Delete spec missing filter and ids | All |
| `BAD_EMBEDDINGS` | Embedding validation failed | All |
| `NO_EMBEDDING_FUNCTION` | No embedding function configured | All |
| `EMBEDDING_ERROR` | Embedding function raised error | All |
| `VECTOR_DIM_MISMATCH` | Vector dimension mismatch | All |
| `UNKNOWN_VECTOR_DIMENSION` | Cannot determine vector dimension | All |
| `EMPTY_INPUT_DIM_UNKNOWN` | Empty input with unknown dimension | All |
| `BAD_MMR_LAMBDA` | MMR lambda out of range | All |
| `BAD_TOP_K` | top‑k exceeds maximum | All |
| `FILTER_NOT_SUPPORTED` | Filtering not supported | All |
| `CAPABILITIES_NOT_AVAILABLE` | Capabilities not available | All |

---

## Appendix E — Implementation Status (Non‑Normative)

| Adapter | Status | Conformance | Framework Versions |
|---------|--------|-------------|-------------------|
| AutoGen | Stable | 100% | ≥0.4.0 |
| CrewAI | Stable | 100% | ≥0.30.0 |
| LangChain | Stable | 100% | 0.1.x, 0.2.x, 0.3.x |
| LlamaIndex | Stable | 100% | ≥0.10.0 |
| Semantic Kernel | Stable | 100% | ≥1.0.0 |

**Note:** This appendix is non‑normative and provided for informational purposes only. The authoritative conformance status is determined by the conformance test suite (§16.3) and the implementation’s own documentation.

---

## Appendix F — Migration from Existing Framework Adapters (Informative)

### From Custom AutoGen Vector Tools

```python
# Before
class MyAutoGenVectorTools:
    def search(self, query):
        return my_vector.search(query)

# After
from corpus_sdk.vector.framework_adapters.autogen import (
    CorpusAutoGenVectorClient,
    create_autogen_vector_tools,
)

client = CorpusAutoGenVectorClient(my_vector_adapter, embedding_function=my_embed_fn)
tools = create_autogen_vector_tools(client)
```

### From Custom CrewAI Vector Tools

```python
# Before
class MyCrewAIVectorTools:
    def _run(self, query):
        return my_vector.search(query)

# After
from corpus_sdk.vector.framework_adapters.crewai import (
    CorpusCrewAIVectorClient,
    create_crewai_vector_tools,
)

client = CorpusCrewAIVectorClient(my_vector_adapter, embedding_function=my_embed_fn)
tools = create_crewai_vector_tools(client)
```

### From Custom LangChain Vector Tools

```python
# Before
class MyLangChainTool(BaseTool):
    def _run(self, query):
        return my_vector.search(query)

# After
from corpus_sdk.vector.framework_adapters.langchain import (
    CorpusLangChainVectorClient,
    create_langchain_vector_tools,
)

client = CorpusLangChainVectorClient(my_vector_adapter, embedding_function=my_embed_fn)
tools = create_langchain_vector_tools(client)
```

### From Custom LlamaIndex VectorStore

```python
# Before
class MyVectorStore(VectorStore):
    def query(self, query):
        return my_vector.search(query.query_embedding, k=query.similarity_top_k)

# After
from corpus_sdk.vector.framework_adapters.llamaindex import (
    CorpusLlamaIndexVectorClient,
    CorpusVectorIndex,
)

client = CorpusLlamaIndexVectorClient(my_vector_adapter)
vector_store = CorpusVectorIndex(client)
```

### From Custom Semantic Kernel Plugin

```python
# Before
class MyVectorPlugin:
    @sk_function
    def search(self, context):
        return my_vector.search(context["query"])

# After
from corpus_sdk.vector.framework_adapters.semantic_kernel import (
    CorpusSemanticKernelVectorClient,
    CorpusSemanticKernelVectorPlugin,
)

client = CorpusSemanticKernelVectorClient(my_vector_adapter, embedding_function=my_embed_fn)
plugin = CorpusSemanticKernelVectorPlugin(client)
kernel.add_plugin(plugin, "vector")
```
