# GRAPH FRAMEWORK ADAPTERS SPECIFICATION 

**specification_version:** `1.0.0`  
**protocol_version:** `1.0.0`  

---

## Abstract

This specification defines the Corpus Framework Adapter Suite for Graph operations: a standardized set of production-grade adapters that bridge Corpus Graph Protocol V1.0 implementations with five leading AI orchestration frameworks—AutoGen, CrewAI, LangChain, LlamaIndex, and Semantic Kernel. The suite provides consistent patterns for context propagation, error handling, observability, resource management, and streaming across frameworks while preserving each framework's native interfaces. This document includes normative contracts for adapter behavior, cross-framework patterns, error taxonomy integration, observability requirements, and implementation guidelines for enterprise-scale graph operations.

> **Keywords:** Framework Adapters, AutoGen, CrewAI, LangChain, LlamaIndex, Semantic Kernel, Graph Operations, Context Propagation, Error Normalization, Observability, Streaming, Multi-Framework, Protocol Bridge, Production Hardening

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
  * [4.7. Resource Cleanup - Best Effort (MUST)](#47-resource-cleanup---best-effort-must)
  * [4.8. Event Loop Guards (MUST)](#48-event-loop-guards-must)
  * [4.9. Async Streaming Support (MUST)](#49-async-streaming-support-must)
  * [4.10. Query Building Semantics (MUST)](#410-query-building-semantics-must)
  * [4.11. Namespace Resolution (MUST)](#411-namespace-resolution-must)
  * [4.12. Dialect Fallback Behavior (SHOULD)](#412-dialect-fallback-behavior-should)
  * [4.13. SIEM-Safe Observability (MUST)](#413-siem-safe-observability-must)
  * [4.14. Testing Accommodations (INFORMATIVE)](#414-testing-accommodations-informative)
  * [4.15. Adapter Lifecycle Summary (INFORMATIVE)](#415-adapter-lifecycle-summary-informative)
  * [4.16. Thread Pool Executors for Tool Bridging (CONDITIONAL SHOULD)](#416-thread-pool-executors-for-tool-bridging-conditional-should)
* [5. Shared Utility Layer](#5-shared-utility-layer)
  * [5.1. Validation Utilities](#51-validation-utilities)
    * [5.1.1. Query Validation](#511-query-validation)
    * [5.1.2. Batch Operation Validation](#512-batch-operation-validation)
    * [5.1.3. Upsert Nodes Spec Validation](#513-upsert-nodes-spec-validation)
    * [5.1.4. Result Type Validation](#514-result-type-validation)
    * [5.1.5. Parameter Coercion for Tool Inputs (Framework-Specific)](#515-parameter-coercion-for-tool-inputs-framework-specific)
  * [5.2. Snapshot Utilities](#52-snapshot-utilities)
  * [5.3. Operation Context Detection (Heuristic)](#53-operation-context-detection-heuristic)
  * [5.4. Async Iterator Detection & Normalization](#54-async-iterator-detection--normalization)
  * [5.5. Resource Cleanup Helpers](#55-resource-cleanup-helpers)
  * [5.6. Error Context Decorator Factory](#56-error-context-decorator-factory)
  * [5.7. Capabilities Normalization](#57-capabilities-normalization)
* [6. Cross-Adapter Patterns](#6-cross-adapter-patterns)
  * [6.1. Unified Error Taxonomy Integration](#61-unified-error-taxonomy-integration)
  * [6.2. Consistent Observability](#62-consistent-observability)
  * [6.3. Operation Context Propagation](#63-operation-context-propagation)
  * [6.4. Idempotency Key Propagation (MUST)](#64-idempotency-key-propagation-must)
  * [6.5. Partial Failure Reporting](#65-partial-failure-reporting)
  * [6.6. Backpressure Integration](#66-backpressure-integration)
  * [6.7. Graph Operation Determinism (MUST)](#67-graph-operation-determinism-must)
  * [6.8. Translator Shim Equivalence (MUST)](#68-translator-shim-equivalence-must)
  * [6.9. Single Source of Truth Pattern (SHOULD)](#69-single-source-of-truth-pattern-should)
  * [6.10. Delete Operation Validation Pattern](#610-delete-operation-validation-pattern)
* [7. AutoGen Adapter Specification](#7-autogen-adapter-specification)
  * [7.1. Overview](#71-overview)
  * [7.2. Framework-Specific Challenges](#72-framework-specific-challenges)
  * [7.3. Data Types](#73-data-types)
  * [7.4. Core Class: `CorpusAutoGenGraphClient`](#74-core-class-corpusautogengraphclient)
    * [7.4.1. AutoGen Compatibility Surface](#741-autogen-compatibility-surface)
    * [7.4.2. Initialization](#742-initialization)
    * [7.4.3. Context Translation](#743-context-translation)
    * [7.4.4. Operations](#744-operations)
  * [7.5. Integration Helpers](#75-integration-helpers)
    * [7.5.1. `create_autogen_graph_tools()`](#751-create_autogen_graph_tools)
  * [7.6. Error Codes](#76-error-codes)
  * [7.7. AutoGen-Specific Context](#77-autogen-specific-context)
* [8. CrewAI Adapter Specification](#8-crewai-adapter-specification)
  * [8.1. Overview](#81-overview)
  * [8.2. Framework-Specific Challenges](#82-framework-specific-challenges)
  * [8.3. Data Types](#83-data-types)
  * [8.4. Core Class: `CorpusCrewAIGraphClient`](#84-core-class-corpuscrewaigraphclient)
    * [8.4.1. Initialization](#841-initialization)
    * [8.4.2. Task Context Translation](#842-task-context-translation)
    * [8.4.3. Operations](#843-operations)
    * [8.4.4. Tool Bridge Executor](#844-tool-bridge-executor)
  * [8.5. Integration Helpers](#85-integration-helpers)
    * [8.5.1. `create_crewai_graph_tools()`](#851-create_crewai_graph_tools)
  * [8.6. Error Codes](#86-error-codes)
  * [8.7. CrewAI-Specific Context](#87-crewai-specific-context)
* [9. LangChain Adapter Specification](#9-langchain-adapter-specification)
  * [9.1. Overview](#91-overview)
  * [9.2. Framework-Specific Challenges](#92-framework-specific-challenges)
  * [9.3. Data Types](#93-data-types)
  * [9.4. Core Class: `CorpusLangChainGraphClient`](#94-core-class-corpuslangchaingraphclient)
    * [9.4.1. Initialization](#941-initialization)
    * [9.4.2. Config Context Translation](#942-config-context-translation)
    * [9.4.3. Event Loop Safety](#943-event-loop-safety)
    * [9.4.4. Operations](#944-operations)
    * [9.4.5. Tool Bridge Executor](#945-tool-bridge-executor)
  * [9.5. Integration Helpers](#95-integration-helpers)
    * [9.5.1. `CorpusGraphTool` (Legacy)](#951-corpusgraphtool-legacy)
    * [9.5.2. `create_langchain_graph_tools()`](#952-create_langchain_graph_tools)
    * [9.5.3. `create_corpus_graph_tool()`](#953-create_corpus_graph_tool)
  * [9.6. Error Codes](#96-error-codes)
  * [9.7. LangChain-Specific Context](#97-langchain-specific-context)
* [10. LlamaIndex Adapter Specification](#10-llamaindex-adapter-specification)
  * [10.1. Overview](#101-overview)
  * [10.2. Framework-Specific Challenges](#102-framework-specific-challenges)
  * [10.3. Data Types](#103-data-types)
  * [10.4. Core Class: `CorpusLlamaIndexGraphClient`](#104-core-class-corpusllamaindexgraphclient)
    * [10.4.1. Initialization](#1041-initialization)
    * [10.4.2. Callback Manager Context Translation](#1042-callback-manager-context-translation)
    * [10.4.3. Operations](#1043-operations)
    * [10.4.4. Single Source of Truth Request Builders](#1044-single-source-of-truth-request-builders)
  * [10.5. Integration Helpers](#105-integration-helpers)
    * [10.5.1. `CorpusGraphStore`](#1051-corpusgraphstore)
  * [10.6. Error Codes](#106-error-codes)
  * [10.7. LlamaIndex-Specific Context](#107-llamaindex-specific-context)
* [11. Semantic Kernel Adapter Specification](#11-semantic-kernel-adapter-specification)
  * [11.1. Overview](#111-overview)
  * [11.2. Framework-Specific Challenges](#112-framework-specific-challenges)
  * [11.3. Data Types](#113-data-types)
  * [11.4. Core Class: `CorpusSemanticKernelGraphClient`](#114-core-class-corpus-semantic-kernel-graph-client)
    * [11.4.1. Initialization](#1141-initialization)
    * [11.4.2. Context + Settings Translation](#1142-context--settings-translation)
    * [11.4.3. Operations](#1143-operations)
    * [11.4.4. Forward-Compatible Kwargs Handling](#1144-forward-compatible-kwargs-handling)
  * [11.5. Integration Helpers](#115-integration-helpers)
    * [11.5.1. `CorpusSemanticKernelPlugin`](#1151-corpussemantickernelplugin)
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
  * [B.3. Async Streaming Patterns](#b3-async-streaming-patterns)
  * [B.4. Resource Cleanup Patterns](#b4-resource-cleanup-patterns)
  * [B.5. Delete Operation Validation Patterns](#b5-delete-operation-validation-patterns)
  * [B.6. Single Source of Truth Request Builders](#b6-single-source-of-truth-request-builders)
* [Appendix C — End-to-End Usage Examples](#appendix-c--end-to-end-usage-examples)
  * [C.1. AutoGen Agent with Graph Tools](#c1-autogen-agent-with-graph-tools)
  * [C.2. CrewAI Crew with Graph Tools](#c2-crewai-crew-with-graph-tools)
  * [C.3. LangChain Agent with Graph Tools](#c3-langchain-agent-with-graph-tools)
  * [C.4. LlamaIndex Knowledge Graph Index](#c4-llamaindex-knowledge-graph-index)
  * [C.5. Semantic Kernel Plugin Registration](#c5-semantic-kernel-plugin-registration)
* [Appendix D — Error Code Reference](#appendix-d--error-code-reference)
* [Appendix E — Implementation Status (Non-Normative)](#appendix-e--implementation-status-non-normative)
* [Appendix F — Migration from Existing Framework Adapters (Informative)](#appendix-f--migration-from-existing-framework-adapters-informative)

---

## 1. Introduction

### 1.1. Motivation

The AI framework landscape has fragmented into five dominant orchestration layers—AutoGen for multi-agent systems, CrewAI for role-based agent teams, LangChain for chain-of-thought pipelines, LlamaIndex for RAG and indexing, and Semantic Kernel for enterprise AI integration. Each framework defines its own interface for graph operations with subtly different expectations:

- **AutoGen** requires tool-based interfaces for agent graph access and uses fully async patterns.
- **CrewAI** expects graph operations attached to agents but provides no shared runtime context across agent executions; tool parameters come from LLMs and require defensive handling.
- **LangChain** defines tool interfaces and Runnable patterns but creates deadlock risks when sync methods are called from async contexts.
- **LlamaIndex** implements `GraphStore` with specific expectations about triplet operations and callback propagation.
- **Semantic Kernel** uses plugin-based architecture with context and settings objects that must be propagated to underlying operations.

Building and maintaining separate providers for each framework duplicates effort, fragments observability, and creates inconsistent error handling across an organization's AI stack. Framework-specific edge cases—like async streaming return shape variations, or context extraction failures—cause production outages that are difficult to debug without deep framework expertise.

The Corpus Framework Adapter Suite for Graph solves this by providing a single, battle-tested implementation of each framework's graph interface, backed by the Corpus Graph Protocol. Each adapter encapsulates the framework-specific hardening required for production deployments while sharing a common foundation for error handling, observability, and resource management. Organizations can standardize on Corpus graph operations once and use them across any supported framework without rebuilding adapter logic.

### 1.2. Scope

This specification defines five framework adapters for graph operations:

1. **AutoGen Adapter** — Implements graph tool interfaces with FunctionTool wrappers, context extraction from conversation objects, and fully async tool implementations (no thread pool needed).

2. **CrewAI Adapter** — Implements BaseTool interfaces with context extraction from agent tasks, bounded thread-pool execution for sync-in-async safety, defensive LLM parameter coercion, and JSON-safe snapshotting for tool outputs.

3. **LangChain Adapter** — Implements BaseTool interfaces with config context extraction, event-loop detection, worker-thread fallback, defensive parameter validation, and comprehensive validation for LLM-provided parameters.

4. **LlamaIndex Adapter** — Implements `GraphStore` protocol with callback manager context propagation, Single Source of Truth request builders, and triplet operation mapping. Includes RECOMMENDED strict validation for edge operations (id, src, dst, label, JSON properties); current implementation enforces at minimum non-null edges and presence of IDs.

5. **Semantic Kernel Adapter** — Implements plugin architecture with context+settings translation, forward-compatible kwargs handling, and graceful fallback for capability methods.

All adapters share:

- **Context propagation** — Framework-specific context (conversation, task, config, callback_manager, context/settings) flows into `OperationContext` and framework_ctx.
- **Error normalization** — All exceptions are enriched with `attach_context()` using framework-specific error codes.
- **Observability** — Dynamic context extraction captures operation types, namespaces, batch sizes, and routing fields.
- **Streaming support** — Both sync and async streaming with robust iterator normalization.
- **Resource management** — Best-effort cleanup via sync/async context managers.
- **Namespace resolution** — Consistent precedence: explicit args → spec.namespace → client defaults.
- **Delete operation validation** — Shared pattern for requiring filter or non-empty ID list, with `BAD_ADAPTER_RESULT` error code and optional `INVALID_DELETE_SPEC` in message.

### 1.3. Design Philosophy

- **Protocol-First (MUST).** Adapters require only duck-typed graph adapters implementing `GraphProtocolV1`, not strict inheritance. This allows minimal test doubles and lightweight integrations.

- **Framework Resilience (MUST).** Adapters defend against framework evolution by filtering context, normalizing inputs, and never assuming internal APIs remain stable. Static compatibility methods satisfy framework probes without leaking implementation details.

- **Observability-First (MUST).** Every graph operation attaches rich error context: framework identity, operation type, namespace, batch sizes, and routing fields. Exceptions crossing framework boundaries carry enough context to debug without log scraping.

- **Fail-Safe Context Translation (MUST).** Context translation from framework-specific structures to `OperationContext` must never break graph operations. If translation fails, adapters proceed without core context and attach diagnostic snapshots.

- **Async-Safe Sync Usage (MUST).** Sync APIs enforce guard rails preventing calls from inside active event loops. When bridging is required for tool integration, adapters use controlled worker-thread execution.

- **Streaming Robustness (MUST).** Async streaming methods must produce semantically equivalent results; chunk boundaries MAY differ across implementations as long as ordering and element integrity are preserved.

- **Defensive Parameter Handling (SHOULD).** For adapters that accept LLM-provided parameters (CrewAI, LangChain tools), numeric parameters SHOULD be coerced, clamped, and defaulted rather than raising exceptions.

- **Single Source of Truth (SHOULD).** Complex request shapes (bulk vertices, traversal) should use shared builders to prevent drift between sync/async implementations.

- **Best-Effort Resource Cleanup (SHOULD).** `close()` and `aclose()` provide best-effort cleanup but do not prevent subsequent operations. Clients SHOULD NOT rely on adapter behavior after close.

- **Edge Validation Flexibility (SHOULD).** Edge upsert validation MAY vary by adapter; at minimum, adapters MUST validate non-null edges and presence of IDs. Stricter validation (src, dst, label, JSON properties) is RECOMMENDED but not required. LlamaIndex adapter aims for strict validation in future releases.

---

## 2. Requirements Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [RFC2119] [RFC8174] when, and only when, they appear in all capitals.

**Example:**  
- "The adapter MUST reject non-string inputs" indicates a strict requirement that must be implemented and verified.  
- "The adapter SHOULD log warnings for large batches" indicates a recommendation that may be deviated from only with good reason.  

**Justified Deviation Example:**  
A developer might choose to disable strict validation in a controlled environment where they have verified all inputs are valid, and where the performance cost of validation is significant. This deviation MUST be documented in the code, explaining why it is safe and what assumptions are being made. The adapter MUST still provide a way to re-enable strict validation via configuration.

---

## 3. Terminology

**Adapter** — Concrete implementation of a framework-specific graph interface backed by a Corpus Graph Protocol V1 adapter.

**Graph Adapter** — The underlying graph implementation that provides the GraphProtocolV1 interface.

**Operation Context** — Core context object containing `request_id`, `idempotency_key`, `deadline_ms`, `traceparent`, `tenant`, and `attrs`.

**Framework Context** — Framework-specific context dictionary passed to the translator alongside core context (e.g., conversation, task, config).

**Translator** — `GraphTranslator` instance that orchestrates graph operations, handling batching, retries, and streaming.

**Framework Translator** — `GraphFrameworkTranslator` implementation that handles framework-specific translation of results.

**Event Loop Guard** — Runtime check preventing sync methods from being called inside an active asyncio event loop.

**Namespace Resolution** — Precedence rules determining which namespace value is used: explicit argument → spec.namespace → client default.

**Single Source of Truth** — Pattern where shared request builders ensure sync/async implementations remain consistent.

**Tool Bridge Executor** — Bounded thread pool used to execute sync graph calls from within async contexts in tool integrations (used by CrewAI and LangChain).

**SIEM-Safe** — Observability that excludes PII, raw content, and tenant identifiers, using hashes and structural metadata instead.

**Best-Effort Cleanup** — Resource cleanup that attempts to release resources but does not enforce a closed state; clients may continue using the adapter after cleanup calls.

---

## 4. Common Foundation Across All Adapters

### 4.1. Protocol-First Design (MUST)

All adapters MUST accept a `graph_adapter` or `adapter` parameter that implements GraphProtocolV1. Strict `isinstance` checks are NOT REQUIRED; behavioral duck typing suffices.

```python
# Valid graph_adapter implementations:
class MinimalGraphAdapter:
    def query(self, query, **kwargs): ...
    def capabilities(self): ...
    def health(self): ...
    def close(self): ...
    async def aclose(self): ...

class FullGraphAdapter:
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
    raise TypeError("adapter must implement GraphProtocolV1-like interface with 'query' and 'capabilities' methods")
```

### 4.2. Framework Resilience Strategy

All adapters implement three defensive layers:

1. **Context Filtering** — Extract only known, stable fields from framework-specific context objects. Unknown keys are ignored (see §4.5). Unknown fields are snapshotted for observability but not relied upon for correctness.

2. **Normalized Error Attachment** — All exceptions are enriched with `attach_context()` using framework-specific error codes and dynamic context (operation, namespace, batch sizes).

3. **Forward-Compatible Method Signatures** — Methods accept `**kwargs` and gracefully handle unsupported parameters by logging and ignoring, ensuring compatibility as frameworks evolve.

### 4.3. Error Context Attachment (MUST)

Every adapter MUST decorate its core graph methods with error-context decorators that capture:

- Operation name (`query`, `stream_query`, `upsert_nodes`, `delete_edges`, etc.)
- Framework identity and version
- Namespace (when available)
- Query text length (for query operations)
- Batch size (for batch operations)
- Framework-specific routing fields

```python
@with_graph_error_context("query_sync")
def query(self, query, ..., context=None, settings=None):
    # Implementation
    pass

@with_async_graph_error_context("query_async")
async def aquery(self, query, ..., context=None, settings=None):
    # Implementation
    pass
```

### 4.4. Dynamic Context Extraction Pattern

All adapters implement dynamic context extraction that captures per-call metrics:

```python
def _extract_dynamic_context(self, args, kwargs, operation):
    ctx = {
        "framework": self._framework_name,
        "framework_version": getattr(self, "_framework_version", None),
    }
    
    if operation in ("query", "stream_query") and args and isinstance(args[0], str):
        ctx["query_len"] = len(args[0])
    
    # Extract namespace if present
    namespace = kwargs.get("namespace") or getattr(kwargs.get("spec"), "namespace", None)
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
    - Use heuristic check (_looks_like_operation_context) to validate result
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
    
    # Enrich attrs with framework metadata (best-effort)
    try:
        attrs = getattr(ctx_candidate, "attrs", {}) or {}
        if isinstance(attrs, dict):
            attrs.setdefault("framework", self._framework_name)
            if self._framework_version:
                attrs.setdefault("framework_version", self._framework_version)
    except Exception:
        logger.debug("Failed to enrich OperationContext attrs", exc_info=True)
    
    return ctx_candidate
```

### 4.6. Thread-Safe Lazy Initialization (MUST)

Translators and other expensive resources MUST be initialized lazily with thread safety:

```python
@cached_property
def _translator(self) -> GraphTranslator:
    """Lazily construct and cache GraphTranslator with thread safety."""
    framework_translator = self._framework_translator or DefaultFrameworkTranslator()
    return create_graph_translator(
        adapter=self._graph,
        framework=self._framework_name,
        translator=framework_translator,
    )
```

### 4.7. Resource Cleanup - Best Effort (MUST)

All adapters MUST implement both sync and async context managers with best-effort cleanup:

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
    """
    Best-effort synchronous cleanup.
    
    Note: This method does NOT prevent subsequent use of the adapter.
    Clients SHOULD NOT rely on adapter behavior after close() is called.
    """
    if self._closed:
        return
    self._closed = True
    
    if hasattr(self._graph, "close"):
        try:
            result = self._graph.close()
            # Handle case where close() incorrectly returns coroutine
            if inspect.iscoroutine(result):
                result.close()
                logger.warning("Graph adapter has async-only close() - use aclose() for proper cleanup")
        except Exception:
            logger.debug("Failed to close graph adapter", exc_info=True)

async def aclose(self) -> None:
    """
    Best-effort asynchronous cleanup.
    
    Note: This method does NOT prevent subsequent use of the adapter.
    Clients SHOULD NOT rely on adapter behavior after aclose() is called.
    """
    if self._aclosed:
        return
    self._aclosed = True
    
    if hasattr(self._graph, "aclose"):
        try:
            await self._graph.aclose()
            self._closed = True
            return
        except Exception:
            logger.debug("Failed to async-close graph adapter", exc_info=True)
    
    if not self._closed:
        self.close()
```

**Important:** `close()` and `aclose()` provide best-effort cleanup but do NOT enforce a closed state. Adapters MAY continue to function after cleanup calls, though this behavior is not guaranteed. Clients SHOULD NOT rely on adapter behavior after calling `close()` or `aclose()`.

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
        f"Use a{api_name}() instead. [{ErrorCodes.SYNC_WRAPPER_CALLED_IN_EVENT_LOOP}]"
    )
```

The error message MUST include the error code `SYNC_WRAPPER_CALLED_IN_EVENT_LOOP` in the message for observability.

### 4.9. Async Streaming Support (MUST)

All async streaming methods MUST produce **semantically equivalent results** for the same input and model. Chunk boundaries MAY differ across implementations as long as:

- Chunk **order** is preserved.
- Each chunk's internal structure and invariants are preserved (no reordering, duplication, or loss).

All adapters MUST call the shared translator streaming primitive (for example, `GraphTranslator.arun_query_stream(...)` or the corresponding embedding/LLM streaming API). The translator is the **normative source of truth** for:

- Returning an `AsyncIterator` (or an awaitable that resolves to an `AsyncIterator`).
- Ensuring chunk shape and protocol invariants.

Adapters MAY add an additional normalization layer on top of the translator. This **adapter-level normalization** is:

- **RECOMMENDED** for LlamaIndex and Semantic Kernel.
- **OPTIONAL** (and MAY be omitted) for AutoGen, CrewAI, and LangChain.

#### 4.9.1. Option A — Adapter-Level Normalization (RECOMMENDED for LlamaIndex, Semantic Kernel)

Adapters that surface streaming as a first-class, strongly-typed API (for example, LlamaIndex, Semantic Kernel) SHOULD perform an explicit normalization step to guard against unexpected shapes, even if the translator already enforces its own contract.

```python
def _is_async_iterator(obj: Any) -> bool:
    """Return True if object implements AsyncIterator protocol."""
    return hasattr(obj, "__aiter__") and hasattr(obj, "__anext__")


def _normalize_async_iterator(aiter_or_awaitable: Any) -> Any:
    """
    Normalize either AsyncIterator or awaitable→AsyncIterator.

    Returns:
        - The awaitable unchanged, if `inspect.isawaitable(...)` is True.
        - The AsyncIterator unchanged, if it implements __aiter__/__anext__.

    Raises:
        TypeError with BAD_ASYNC_ITERATOR_SHAPE for invalid shapes.
    """
    if inspect.isawaitable(aiter_or_awaitable):
        return aiter_or_awaitable
    if _is_async_iterator(aiter_or_awaitable):
        return aiter_or_awaitable

    raise TypeError(
        f"Expected AsyncIterator or awaitable; got {type(aiter_or_awaitable).__name__} "
        f"[{ErrorCodes.BAD_ASYNC_ITERATOR_SHAPE}]"
    )


async def astream_query(self, ...):
    # ... setup ...
    aiter_or_awaitable = self._translator.arun_query_stream(...)
    normalized = _normalize_async_iterator(aiter_or_awaitable)

    if inspect.isawaitable(normalized):
        aiter = await normalized
    else:
        aiter = normalized

    if not _is_async_iterator(aiter):
        raise TypeError(
            f"Resolved value not an AsyncIterator [{ErrorCodes.BAD_ASYNC_ITERATOR_SHAPE}]"
        )

    async for chunk in aiter:
        yield chunk
```

**Rationale (Option A):**
- LlamaIndex and Semantic Kernel often plug directly into application code that assumes strict typing and clear failure modes.
- A small, explicit normalization layer yields clearer, framework-specific error codes (`BAD_ASYNC_ITERATOR_SHAPE`) if something upstream regresses, while still relying on the translator for the core streaming contract.

#### 4.9.2. Option B — Translator-Level Normalization Only (ACCEPTABLE for AutoGen, CrewAI, LangChain)

If the adapter trusts that `GraphTranslator.arun_query_stream()` (or the corresponding streaming primitive) always returns a valid `AsyncIterator` (or an awaitable resolving to one), it MAY skip explicit adapter-level normalization and directly iterate:

```python
async def astream_query(self, ...):
    async for chunk in self._translator.arun_query_stream(...):
        yield chunk
```

In this mode:
- The translator remains responsible for enforcing the streaming contract.
- Any exceptions arising from invalid shapes are still captured and enriched by the shared error-context decorators surrounding the streaming method.

**Rationale (Option B):**
- AutoGen, CrewAI, and LangChain streaming APIs are typically closer to "internal plumbing," where additional type guards in the adapter provide less marginal value compared to LlamaIndex/Semantic Kernel public surfaces.
- Relying solely on translator-level normalization keeps adapter code simpler while still benefiting from centralized contract enforcement and error-context enrichment.
```

All adapters MUST implement a consistent `_build_raw_query()` method:

```python
def _build_raw_query(
    self,
    query: str,
    *,
    params: Optional[Mapping[str, Any]],
    dialect: Optional[str],
    namespace: Optional[str],
    timeout_ms: Optional[int],
    stream: bool,
) -> Mapping[str, Any]:
    """
    Build raw query mapping for GraphTranslator.
    
    Required fields:
    - text: str
    - params: Dict[str, Any] (materialized)
    - stream: bool
    
    Optional fields:
    - dialect: str (if provided or default)
    - namespace: str (if provided or default)
    - timeout_ms: int (if provided or default)
    """
    effective_dialect = dialect or self._default_dialect
    effective_namespace = namespace or self._default_namespace
    effective_timeout = timeout_ms or self._default_timeout_ms
    
    raw = {
        "text": query,
        "params": dict(params or {}),
        "stream": bool(stream),
    }
    
    if effective_dialect is not None:
        raw["dialect"] = effective_dialect
    if effective_namespace is not None:
        raw["namespace"] = effective_namespace
    if effective_timeout is not None:
        raw["timeout_ms"] = int(effective_timeout)
    
    return raw
```

**Parameter Type Handling:** The `dict(params or {})` conversion will naturally raise `TypeError` if `params` is not mapping-like. These errors will be caught by error-context decorators and do not require explicit validation.

### 4.11. Namespace Resolution (MUST)

All adapters MUST implement consistent namespace precedence:

1. **Explicit argument** — If `namespace` is provided directly to the method call, it has highest precedence.
2. **Spec namespace** — For spec-based operations (UpsertNodesSpec, BulkVerticesSpec, etc.), `spec.namespace` is used if present.
3. **Client default** — If neither explicit nor spec namespace is provided, the client's `default_namespace` (set during initialization) is used.
4. **None** — If none of the above are set, namespace is omitted from the request.

```python
def _framework_ctx(self, *, operation: str, namespace: Optional[str] = None) -> Mapping[str, Any]:
    """Build framework context with resolved namespace."""
    ctx = {"framework": self._framework_name, "operation": operation}
    
    effective_namespace = namespace or self._default_namespace
    if effective_namespace is not None:
        ctx["namespace"] = effective_namespace
    
    return ctx
```

### 4.12. Dialect Fallback Behavior (SHOULD)

Adapters SHOULD implement dialect fallback for query operations:

```python
try:
    result = self._translator.query(raw_query, ...)
except NotSupported:
    if dialect is not None:  # Only retry if dialect was explicitly provided
        fallback_raw = dict(raw_query)
        fallback_raw.pop("dialect", None)
        result = self._translator.query(fallback_raw, ...)
    else:
        raise
```

This handles backends that reject unknown dialects but can execute queries without them.

### 4.13. SIEM-Safe Observability (MUST)

All logging MUST:

- Never log raw query text, parameters, or tenant identifiers
- Use truncation for long strings and containers
- Include `tenant_hash` instead of raw tenant (when available in context)
- Log operation completion with dimensions and latency

**Truncation thresholds (Normative):**  
- Strings longer than `MAX_STRING_LENGTH = 5000` characters MUST be truncated
- Containers with more than `MAX_CONTAINER_ITEMS = 200` items MUST be limited

```python
logger.debug(
    "Query completed: op=%s namespace=%s latency_ms=%.2f",
    operation, namespace, elapsed_ms
)
```

### 4.14. Testing Accommodations (INFORMATIVE)

Adapters SHOULD support test injection:

- Translator can be injected via `framework_translator` parameter
- Context building can be overridden in test subclasses
- Error codes are exposed for assertion
- `_closed`/`_aclosed` flags are observable

### 4.15. Adapter Lifecycle Summary (INFORMATIVE)

This section restates the lifecycle guidance from §4.7 in summary form:

- Adapters track `_closed`/`_aclosed` flags for idempotent cleanup
- `close()` and `aclose()` provide best-effort resource release
- These methods do NOT prevent subsequent operations
- Clients SHOULD NOT rely on adapter behavior after calling `close()` or `aclose()`
- Multiple calls to `close()` or `aclose()` are idempotent and safe

### 4.16. Thread Pool Executors for Tool Bridging (CONDITIONAL SHOULD)

For adapters that provide tool integration and need to bridge sync calls from async contexts (CrewAI, LangChain), any thread pool executor used SHOULD satisfy the following recommendations:

- The executor SHOULD be a **daemon** thread pool (`daemon=True`) so that it does not block interpreter shutdown.
- The pool SHOULD have a bounded work queue to provide backpressure; implementations MAY use a custom executor with `queue=Queue(maxsize=…)` or accept that the default `ThreadPoolExecutor` uses an unbounded queue.
- The executor MAY be created as a **module‑level singleton** shared by all instances of that adapter to avoid unbounded thread creation.
- On interpreter exit, daemon threads are abruptly terminated; this is acceptable because the pool only runs short‑lived graph calls, and abrupt termination will not leak resources (the underlying translator calls are expected to handle cancellation).
- No explicit shutdown of the pool is required, but implementations MAY register an `atexit` handler to attempt graceful shutdown (non‑normative).

**Note:** The default `ThreadPoolExecutor` in Python uses an unbounded work queue. If backpressure is required, implementers should consider a custom executor with a bounded queue. AutoGen adapter uses fully async tools and does NOT require a thread pool executor.

---

## 5. Shared Utility Layer

### 5.1. Validation Utilities

#### 5.1.1. Query Validation

```python
def validate_graph_query(query: str, *, operation: str, error_code: str) -> None:
    """Validate that query is a non-empty string."""
    if not isinstance(query, str):
        raise TypeError(f"{operation} expects str query; got {type(query).__name__}")
    if not query.strip():
        raise ValueError(f"{operation} query cannot be empty")
```

#### 5.1.2. Batch Operation Validation

```python
def validate_batch_operations(ops: List[BatchOperation], *, operation: str, error_code: str) -> None:
    """Validate batch operations list."""
    if not isinstance(ops, list):
        raise TypeError(f"{operation} expects List[BatchOperation]; got {type(ops).__name__}")
    
    for i, op in enumerate(ops):
        if not isinstance(op, BatchOperation):
            raise TypeError(f"{operation}[{i}] must be BatchOperation; got {type(op).__name__}")
        if not op.op:
            raise ValueError(f"{operation}[{i}].op cannot be empty")
```

#### 5.1.3. Upsert Nodes Spec Validation

```python
def validate_upsert_nodes_spec(spec: UpsertNodesSpec) -> None:
    """Validate UpsertNodesSpec structure."""
    if not isinstance(spec, UpsertNodesSpec):
        raise TypeError(f"Expected UpsertNodesSpec; got {type(spec).__name__}")
    
    if spec.nodes is None:
        raise ValueError("UpsertNodesSpec.nodes must not be None")
    
    try:
        nodes = list(spec.nodes)
    except TypeError:
        raise ValueError("UpsertNodesSpec.nodes must be iterable")
    
    if not nodes:
        raise ValueError("UpsertNodesSpec must contain at least one node")
    
    for i, node in enumerate(nodes):
        if not hasattr(node, "id") or not node.id:
            raise ValueError(f"Node at index {i} must have an ID")
```

#### 5.1.4. Result Type Validation

```python
def validate_graph_result_type(
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

#### 5.1.5. Parameter Coercion for Tool Inputs (Framework-Specific)

The following functions SHOULD be used by adapters that accept LLM‑provided parameters (CrewAI, LangChain tools) to safely convert and bound numeric inputs.

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
    Convert a possibly-LLM-provided value into a safe bounded positive int.

    Behavior:
      - If conversion fails, returns the provided default.
      - If converted value is out of bounds, clamps to [min_value, max_value].
      - MUST NOT raise an exception.

    This function is used to protect tool execution from malformed or malicious inputs.
    """
    try:
        # Allow strings and floats that represent integers ("25", 25.0).
        ivalue = int(value)
    except Exception:
        logger.debug("Invalid tool param %s=%r; defaulting to %d", name, value, default)
        return default

    if ivalue < min_value:
        return min_value
    if ivalue > max_value:
        return max_value
    return ivalue

def validated_max_chunks(value: Any, *, max_allowed: int = 100) -> int:
    """
    Specialization of coerce_bounded_positive_int for the 'max_chunks' parameter.

    - Converts value to int.
    - If conversion fails, returns 25 (default).
    - Clamps to [1, max_allowed].
    """
    return coerce_bounded_positive_int(
        value,
        name="max_chunks",
        default=25,
        min_value=1,
        max_value=max_allowed,
    )
```

**Note:** AutoGen tools are fully async and MAY use simpler validation (e.g., `int(max_chunks)` with bounds checking) since parameters come from trusted sources.

### 5.2. Snapshot Utilities

```python
def _safe_snapshot(value: Any, *, max_items: int = 200, max_str: int = 5000) -> Any:
    """
    Convert any value to a safe-to-log snapshot:
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

### 5.3. Operation Context Detection (Heuristic)

```python
def _looks_like_operation_context(obj: Any) -> bool:
    """
    Heuristic check for OperationContext-like objects.
    
    This is a best-effort structural check that MAY be liberal in what it accepts.
    Implementations MAY use stricter checks (requiring attrs + one of to_dict/request_id/traceparent)
    or looser checks (any of request_id, traceparent, tenant, attrs, to_dict).
    
    The exact heuristic is implementation-defined and MAY vary across adapters.
    """
    if obj is None:
        return False
    
    try:
        if isinstance(obj, OperationContext):
            return True
    except TypeError:
        pass
    
    # Example liberal heuristic (AutoGen, CrewAI, LangChain)
    attrs = ("request_id", "traceparent", "tenant", "attrs", "to_dict")
    return any(hasattr(obj, attr) for attr in attrs)
    
    # Example strict heuristic (LlamaIndex, Semantic Kernel)
    # has_attrs = hasattr(obj, "attrs")
    # has_to_dict = hasattr(obj, "to_dict")
    # has_request_id = hasattr(obj, "request_id")
    # has_traceparent = hasattr(obj, "traceparent")
    # return has_attrs and (has_to_dict or has_request_id or has_traceparent)
```

### 5.4. Async Iterator Detection & Normalization

```python
def _is_async_iterator(obj: Any) -> bool:
    """Return True if object is an AsyncIterator."""
    return hasattr(obj, "__aiter__") and hasattr(obj, "__anext__")

def _normalize_async_iterator(aiter_or_awaitable: Any) -> Any:
    """
    Normalize AsyncIterator or awaitable→AsyncIterator.
    
    Returns awaitable unchanged, AsyncIterator unchanged.
    May raise TypeError with BAD_ASYNC_ITERATOR_SHAPE for invalid shapes.
    """
    if inspect.isawaitable(aiter_or_awaitable):
        return aiter_or_awaitable
    if _is_async_iterator(aiter_or_awaitable):
        return aiter_or_awaitable
    
    raise TypeError(
        f"Expected AsyncIterator or awaitable; got {type(aiter_or_awaitable).__name__} "
        f"[{ErrorCodes.BAD_ASYNC_ITERATOR_SHAPE}]"
    )
```

### 5.5. Resource Cleanup Helpers

```python
def _maybe_close_sync(obj: Any) -> None:
    """Best-effort sync cleanup."""
    if obj is None:
        return
    
    close_fn = getattr(obj, "close", None)
    if callable(close_fn):
        try:
            result = close_fn()
            if inspect.iscoroutine(result):
                result.close()
                logger.warning("Object has async-only close() - use aclose()")
        except Exception:
            logger.debug("Failed to close object", exc_info=True)

async def _maybe_close_async(obj: Any) -> None:
    """Best-effort async cleanup, falling back to sync close."""
    if obj is None:
        return
    
    aclose_fn = getattr(obj, "aclose", None)
    if callable(aclose_fn):
        try:
            await aclose_fn()
            return
        except Exception:
            logger.debug("Failed to async-close object", exc_info=True)
    
    _maybe_close_sync(obj)
```

### 5.6. Error Context Decorator Factory

```python
def create_graph_error_context_decorator(
    framework: str,
    is_async: bool,
) -> Callable:
    """
    Create a decorator that attaches rich error context to graph operations.
    
    Returns a decorator that can be applied with operation name and static context.
    """
    def decorator(operation: str, **static_context: Any) -> Callable:
        def wrap(func: Callable) -> Callable:
            if is_async:
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        # Extract dynamic context from args/kwargs
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

### 5.7. Capabilities Normalization

```python
def graph_capabilities_to_dict(caps: Any) -> Dict[str, Any]:
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

---

## 6. Cross-Adapter Patterns

### 6.1. Unified Error Taxonomy Integration

All adapters map framework-specific exceptions to the Corpus error taxonomy:

```python
try:
    result = await self._translator.arun_query(...)
except NotSupported as e:
    if dialect is not None:
        # Handle dialect fallback
        pass
    else:
        raise
except BadRequest as e:
    if e.code == "INVALID_QUERY":
        # Map to framework-appropriate exception
        raise ValueError(f"Invalid query syntax: {e}") from e
    raise
except Exception as e:
    attach_context(e, framework=self._framework_name, ...)
    raise
```

### 6.2. Consistent Observability

All adapters emit:
- One metric per operation (including streaming)
- Structured logs with `tenant_hash` (when available), operation, namespace, latency
- Distributed trace context via `traceparent`

### 6.3. Operation Context Propagation

Framework-specific context flows into `OperationContext` via translation helpers:

```
framework_context → context_from_framework() → OperationContext
```

### 6.4. Idempotency Key Propagation (MUST)

When an `idempotency_key` is provided in the operation context, adapters MUST propagate this key to the underlying translator and MUST NOT perform any client-side behavior (such as automatic retries) that could break the exactly-once semantics provided by the backend. The adapter itself does not guarantee exactly-once execution—that depends on the backend honoring the idempotency key.

```python
# Adapters MUST propagate the key and avoid duplicate-write behavior
ctx = self._build_ctx(...)
if ctx and ctx.idempotency_key:
    # Pass through to translator; backend responsible for deduplication
    result = self._translator.upsert_nodes(..., idempotency_key=ctx.idempotency_key)
```

### 6.5. Partial Failure Reporting

Batch operations (batch, transaction) MAY experience partial failures. The adapter MUST handle these according to the following rules:

- If the underlying translator returns a structured result containing partial failures, the adapter MUST:
  - Return the complete `BatchResult` including both successful and failed operations
  - Log each failure with sufficient detail (index, error code, message)
  - Not raise an exception unless all operations fail

```json
// Example log entry for partial failure
{
  "ok": true,
  "code": "PARTIAL_SUCCESS",
  "operation": "batch",
  "processed_count": 5,
  "failed_count": 1,
  "failures": [
    {
      "index": 3,
      "error": "NODE_NOT_FOUND",
      "detail": "Node with id 'n123' does not exist"
    }
  ]
}
```

### 6.6. Backpressure Integration

Adapters SHOULD:
- Surface `ResourceExhausted` with `retry_after_ms` when rate-limited
- Include `throttle_scope` in error details
- Propagate backpressure hints from underlying provider

### 6.7. Graph Operation Determinism (MUST)

When backed by the same underlying graph adapter and translator configuration, all framework adapters MUST produce the same graph operation results for the same inputs, regardless of which framework adapter is used. This ensures that applications can switch frameworks without changing graph behavior, assuming identical backend configuration.

- **Query equivalence:** The same query string and parameters MUST return identical results (row sets, structure) across all adapters when using the same backend.
- **Mutation equivalence:** The same upsert/delete operations MUST produce identical state changes across all adapters when using the same backend.
- **Error equivalence:** The same invalid inputs MUST produce equivalent error types and codes across all adapters when using the same backend.

**Streaming chunk equivalence:** For streaming graph operations (`stream_query` / `astream_query`), adapters MUST produce semantically equivalent results regardless of chunk boundaries. Two streaming results are considered semantically equivalent if the concatenation of all `QueryChunk` items from one adapter yields the same sequence of data elements (e.g., rows, edges, nodes) as the concatenation from another adapter, when given identical inputs. Chunk boundaries MAY differ; adapters MAY split the result stream into chunks arbitrarily, but each chunk MUST contain only complete data elements (no partial rows/edges) and the overall order MUST be preserved.

### 6.8. Translator Shim Equivalence (MUST)

The `GraphTranslator` and `GraphFrameworkTranslator` layers MUST ensure that observable behavior is **equivalent** regardless of which underlying graph adapter implementation is used, assuming identical configuration. This means:

- Query results must have identical structure and content
- Error types and codes must be consistent
- Streaming chunk **content** must be semantically equivalent; chunk boundaries MAY differ as long as ordering and element integrity are preserved
- Batch operation results must report successes/failures identically

### 6.9. Single Source of Truth Pattern (SHOULD)

For complex request shapes (bulk vertices, traversal), adapters SHOULD implement shared request builders:

```python
def _build_bulk_vertices_request(self, spec: BulkVerticesSpec) -> Mapping[str, Any]:
    """Single source of truth for bulk vertices request shape."""
    return {
        "namespace": spec.namespace,
        "limit": spec.limit,
        "cursor": spec.cursor,
        "filter": spec.filter,
    }

def _build_traversal_request(self, spec: GraphTraversalSpec) -> Mapping[str, Any]:
    """Single source of truth for traversal request shape."""
    return {
        "start_nodes": list(spec.start_nodes),
        "max_depth": spec.max_depth,
        "direction": spec.direction,
        "relationship_types": spec.relationship_types,
        "node_filters": spec.node_filters,
        "relationship_filters": spec.relationship_filters,
        "return_properties": spec.return_properties,
        "namespace": spec.namespace,
    }
```

This prevents drift between sync and async implementations as specs evolve.

### 6.10. Delete Operation Validation Pattern

All adapters implement consistent validation for delete operations requiring either a filter or non-empty IDs:

```python
def _validate_delete_spec(
    self,
    *,
    spec_filter: Any,
    spec_ids: Any,
    empty_message: str,
) -> Any:
    """
    Validate delete spec has either filter or non-empty ID list.
    
    Returns the filter or materialized IDs.
    Raises BadRequest with BAD_ADAPTER_RESULT if neither is provided.
    The message SHOULD include [INVALID_DELETE_SPEC] for observability.
    """
    if spec_filter is not None:
        return spec_filter
    
    ids = list(spec_ids or [])
    if not ids:
        raise BadRequest(
            f"{empty_message} [INVALID_DELETE_SPEC]",
            code=ErrorCodes.BAD_ADAPTER_RESULT,
        )
    return ids
```

**Important:** The error code field MUST be `BAD_ADAPTER_RESULT`. The message SHOULD include `[INVALID_DELETE_SPEC]` for observability and log correlation.

---

## 7. AutoGen Adapter Specification

### 7.1. Overview

The AutoGen adapter exposes Corpus graph operations as AutoGen-friendly FunctionTool wrappers, enabling agent-based graph access. It provides fully async tools that integrate seamlessly with AutoGen's async agent runtime.

### 7.2. Framework-Specific Challenges

| Challenge | Solution |
|-----------|----------|
| AutoGen agents expect tool interfaces | `create_autogen_graph_tools()` produces FunctionTool wrappers |
| Context must propagate from conversation objects | `core_ctx_from_autogen()` extracts OperationContext |
| Tool outputs must be JSON-serializable | `_json_safe_snapshot()` with truncation limits |
| AutoGen uses fully async patterns | Tools are async only; no thread pool needed |

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

### 7.4. Core Class: `CorpusAutoGenGraphClient`

#### 7.4.1. AutoGen Compatibility Surface

```python
class CorpusAutoGenGraphClient:
    """
    AutoGen-oriented client wrapper around a Corpus GraphProtocolV1.
    
    Translates AutoGen conversation objects into OperationContext
    and delegates all graph operations to GraphTranslator.
    """
```

#### 7.4.2. Initialization

```python
def __init__(
    self,
    adapter: Optional[GraphProtocolV1] = None,
    *,
    graph_adapter: Optional[GraphProtocolV1] = None,
    default_dialect: Optional[str] = None,
    default_namespace: Optional[str] = None,
    default_timeout_ms: Optional[int] = None,
    framework_version: Optional[str] = None,
    framework_translator: Optional[GraphFrameworkTranslator] = None,
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
    # Enrich with framework metadata (best-effort)
    # Return None on failure
```

#### 7.4.4. Operations

All standard graph operations as defined in §4, with `conversation` parameter for context propagation.

### 7.5. Integration Helpers

#### 7.5.1. `create_autogen_graph_tools()`

```python
def create_autogen_graph_tools(
    client: "CorpusAutoGenGraphClient",
    *,
    name_prefix: str = "graph",
    description_prefix: str = "Corpus graph tool",
) -> List[Any]:
    """
    Create AutoGen-native FunctionTool wrappers for graph operations.
    
    - Lazy imports AutoGen
    - Creates async tools (no sync variants needed)
    - Returns JSON-safe snapshots for tool compatibility
    - Simple parameter validation (int conversion with bounds checks)
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
    BAD_BULK_VERTICES_RESULT = "BAD_BULK_VERTICES_RESULT"
    BAD_TRAVERSAL_RESULT = "BAD_TRAVERSAL_RESULT"
    BAD_BATCH_RESULT = "BAD_BATCH_RESULT"
    BAD_TRANSACTION_RESULT = "BAD_TRANSACTION_RESULT"
    BAD_ADAPTER_RESULT = "BAD_ADAPTER_RESULT"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
    
    # Validation codes (may be strings, not necessarily in ErrorCodes class)
    INVALID_QUERY = "INVALID_QUERY"
    INVALID_BATCH_OPS = "INVALID_BATCH_OPS"
```

### 7.7. AutoGen-Specific Context

The adapter extracts these fields from `conversation`:
- `agent_name` — Current agent identifier
- `conversation_id` — Active conversation
- `workflow_type` — Type of agent workflow
- `retriever_name` — Name of retriever component

Unknown fields are ignored.

---

## 8. CrewAI Adapter Specification

### 8.1. Overview

The CrewAI adapter exposes Corpus graph operations as CrewAI BaseTool wrappers, enabling role-based agent teams to access graph data. It solves context propagation across agents that operate without a shared runtime and defends against malformed LLM-provided parameters.

### 8.2. Framework-Specific Challenges

| Challenge | Solution |
|-----------|----------|
| No shared runtime context across agents | Extract context from per-call `task` parameter |
| Tool execution in async agent loops | Bounded thread pool with `_run_blocking_in_crewai_tool_thread()` |
| LLM-provided parameters may be malformed | `coerce_bounded_positive_int()` for numeric parameters (see §5.1.5) |
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

### 8.4. Core Class: `CorpusCrewAIGraphClient`

#### 8.4.1. Initialization

```python
def __init__(
    self,
    adapter: Optional[GraphProtocolV1] = None,
    *,
    graph_adapter: Optional[GraphProtocolV1] = None,
    default_dialect: Optional[str] = None,
    default_namespace: Optional[str] = None,
    default_timeout_ms: Optional[int] = None,
    framework_version: Optional[str] = None,
    framework_translator: Optional[GraphFrameworkTranslator] = None,
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
    # Enrich with framework metadata (best-effort)
    # Return None on failure
```

#### 8.4.3. Operations

All standard graph operations as defined in §4, with `task` parameter for context propagation.

#### 8.4.4. Tool Bridge Executor

```python
_CREWAI_TOOL_BRIDGE_EXECUTOR: Optional[ThreadPoolExecutor] = None
_CREWAI_TOOL_BRIDGE_EXECUTOR_LOCK = threading.Lock()

def _run_blocking_in_crewai_tool_thread(fn: Callable[[], T]) -> T:
    """Run sync function in bounded thread pool when called from event loop."""
    global _CREWAI_TOOL_BRIDGE_EXECUTOR
    with _CREWAI_TOOL_BRIDGE_EXECUTOR_LOCK:
        if _CREWAI_TOOL_BRIDGE_EXECUTOR is None:
            _CREWAI_TOOL_BRIDGE_EXECUTOR = ThreadPoolExecutor(
                max_workers=4,
                thread_name_prefix="corpus-crewai-tool",
            )
        executor = _CREWAI_TOOL_BRIDGE_EXECUTOR
    
    return executor.submit(fn).result()

def _shutdown_crewai_tool_bridge_executor() -> None:
    """Best-effort shutdown for tool bridge executor."""
    # Idempotent shutdown with error swallowing
```

### 8.5. Integration Helpers

#### 8.5.1. `create_crewai_graph_tools()`

```python
def create_crewai_graph_tools(
    client: "CorpusCrewAIGraphClient",
    *,
    name_prefix: str = "graph",
    description_prefix: str = "Corpus graph tool",
) -> List[Any]:
    """
    Create CrewAI-native BaseTool wrappers for graph operations.
    
    - Lazy imports CrewAI
    - Provides both _run (sync) and _arun (async) implementations
    - Uses thread pool for sync-in-async safety
    - For numeric parameters like max_chunks, uses `validated_max_chunks()` (see §5.1.5)
    - Returns JSON strings with size bounds and fallback truncation
    """
```

### 8.6. Error Codes

```python
class ErrorCodes:
    BAD_OPERATION_CONTEXT = "BAD_OPERATION_CONTEXT"
    BAD_TRANSLATED_SCHEMA = "BAD_TRANSLATED_SCHEMA"
    BAD_HEALTH_RESULT = "BAD_HEALTH_RESULT"
    BAD_TRANSLATED_RESULT = "BAD_TRANSLATED_RESULT"
    BAD_TRANSLATED_CHUNK = "BAD_TRANSLATED_CHUNK"
    BAD_UPSERT_RESULT = "BAD_UPSERT_RESULT"
    BAD_DELETE_RESULT = "BAD_DELETE_RESULT"
    BAD_BULK_VERTICES_RESULT = "BAD_BULK_VERTICES_RESULT"
    BAD_TRAVERSAL_RESULT = "BAD_TRAVERSAL_RESULT"
    BAD_TRANSACTION_RESULT = "BAD_TRANSACTION_RESULT"
    BAD_BATCH_RESULT = "BAD_BATCH_RESULT"
    BAD_ADAPTER_RESULT = "BAD_ADAPTER_RESULT"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
    
    INVALID_QUERY = "INVALID_QUERY"
    INVALID_BATCH_OPS = "INVALID_BATCH_OPS"
    INVALID_TOOL_PARAM = "INVALID_TOOL_PARAM"
```

### 8.7. CrewAI-Specific Context

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

The LangChain adapter exposes Corpus graph operations as LangChain BaseTool wrappers, enabling graph access in LangChain agents and chains. It solves the production problem of sync methods called from async contexts and provides defensive LLM-provided parameter validation.

### 9.2. Framework-Specific Challenges

| Challenge | Solution |
|-----------|----------|
| Sync methods called from async agent runtimes | Event loop detection + worker thread bridge |
| LLM-provided parameters may be malformed | `validated_max_chunks()` with coercion and clamping (see §5.1.5) |
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

### 9.4. Core Class: `CorpusLangChainGraphClient`

#### 9.4.1. Initialization

```python
def __init__(
    self,
    *,
    graph_adapter: Optional[GraphProtocolV1] = None,
    adapter: Optional[GraphProtocolV1] = None,
    default_dialect: Optional[str] = None,
    default_namespace: Optional[str] = None,
    default_timeout_ms: Optional[int] = None,
    framework_version: Optional[str] = None,
    framework_translator: Optional[GraphFrameworkTranslator] = None,
):
    # Standard initialization with adapter/graph_adapter resolution
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
    # Enrich with framework metadata (best-effort)
    # Handle both RunnableConfig and older dict formats
```

#### 9.4.3. Event Loop Safety

```python
def close(self) -> None:
    """Handle adapters that may return coroutine from close()."""
    if self._closed:
        return
    self._closed = True
    
    close_fn = getattr(self._graph, "close", None)
    if callable(close_fn):
        try:
            result = close_fn()
            if inspect.iscoroutine(result):
                result.close()  # Suppress "never awaited" warning
                logger.warning("Adapter has async-only close() - use aclose()")
        except Exception as e:
            logger.warning("Error closing graph adapter: %s", e)
```

#### 9.4.4. Operations

All standard graph operations as defined in §4, with `config` parameter for context propagation.

#### 9.4.5. Tool Bridge Executor

Same pattern as CrewAI (§8.4.4) but with `_LANGCHAIN_TOOL_BRIDGE_EXECUTOR`.

### 9.5. Integration Helpers

#### 9.5.1. `CorpusGraphTool` (Legacy)

```python
class CorpusGraphTool:
    """
    Legacy stub that raises ImportError with installation instructions.
    
    Use create_langchain_graph_tools() or create_corpus_graph_tool() instead.
    """
```

#### 9.5.2. `create_langchain_graph_tools()`

```python
def create_langchain_graph_tools(
    client: CorpusLangChainGraphClient,
    *,
    name_prefix: str = "graph",
    description_prefix: str = "Corpus graph tool",
) -> List[Any]:
    """
    Create LangChain-native BaseTool wrappers for graph operations.
    
    - Lazy imports LangChain BaseTool
    - Provides _run (sync) and _arun (async) implementations
    - Validates LLM-provided parameters with `validated_max_chunks()` (see §5.1.5)
    - Returns JSON strings with size bounds
    """
```

#### 9.5.3. `create_corpus_graph_tool()`

```python
def create_corpus_graph_tool(
    *,
    graph_adapter: GraphProtocolV1,
    default_dialect: Optional[str] = None,
    default_namespace: Optional[str] = None,
    default_timeout_ms: Optional[int] = None,
    framework_version: Optional[str] = None,
    name: str = "corpus_graph",
    description: Optional[str] = None,
    framework_translator: Optional[GraphFrameworkTranslator] = None,
) -> Any:
    """
    Convenience factory: creates client and returns single query tool.
    
    Maintains backward compatibility with older single-tool pattern.
    """
```

### 9.6. Error Codes

```python
class ErrorCodes:
    BAD_OPERATION_CONTEXT = "BAD_OPERATION_CONTEXT"
    BAD_TRANSLATED_SCHEMA = "BAD_TRANSLATED_SCHEMA"
    BAD_HEALTH_RESULT = "BAD_HEALTH_RESULT"
    BAD_TRANSLATED_RESULT = "BAD_TRANSLATED_RESULT"
    BAD_TRANSLATED_CHUNK = "BAD_TRANSLATED_CHUNK"
    BAD_UPSERT_RESULT = "BAD_UPSERT_RESULT"
    BAD_DELETE_RESULT = "BAD_DELETE_RESULT"
    BAD_BULK_VERTICES_RESULT = "BAD_BULK_VERTICES_RESULT"
    BAD_TRAVERSAL_RESULT = "BAD_TRAVERSAL_RESULT"
    BAD_TRANSACTION_RESULT = "BAD_TRANSACTION_RESULT"
    BAD_BATCH_RESULT = "BAD_BATCH_RESULT"
    BAD_ADAPTER_RESULT = "BAD_ADAPTER_RESULT"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
    
    INVALID_QUERY = "INVALID_QUERY"
    INVALID_BATCH_OPS = "INVALID_BATCH_OPS"
```

### 9.7. LangChain-Specific Context

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

The LlamaIndex adapter implements the `GraphStore` protocol, enabling Corpus graphs to be used in LlamaIndex's knowledge graph indices. It provides robust context propagation and includes RECOMMENDED strict validation for edge operations.

### 10.2. Framework-Specific Challenges

| Challenge | Solution |
|-----------|----------|
| GraphStore expects triplet operations (subj, rel, obj) | Configurable query templates for triplet mapping |
| Callback manager must propagate to operations | `core_ctx_from_llamaindex()` extracts context |
| Async streaming may return awaitable→AsyncIterator | `_normalize_async_iterator()` with explicit shape checking |
| Schema representation as string | `get_schema()` returns str(GraphSchema) |
| Edge validation | RECOMMENDED strict validation (id, src, dst, label, JSON properties); current implementation enforces at minimum non-null edges and presence of IDs |

### 10.3. Data Types

```python
class LlamaIndexContext(TypedDict, total=False):
    node_ids: Optional[List[str]]
    index_id: Optional[str]
    callback_manager: Optional[Any]
    trace_id: Optional[str]
    workflow: Optional[str]
```

### 10.4. Core Class: `CorpusLlamaIndexGraphClient`

#### 10.4.1. Initialization

```python
def __init__(
    self,
    adapter: Optional[GraphProtocolV1] = None,
    *,
    graph_adapter: Optional[GraphProtocolV1] = None,
    default_dialect: Optional[str] = None,
    default_namespace: Optional[str] = None,
    default_timeout_ms: Optional[int] = None,
    framework_version: Optional[str] = None,
    framework_translator: Optional[GraphFrameworkTranslator] = None,
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
    # Enrich with framework metadata (best-effort)
    # Return None on failure
```

#### 10.4.3. Operations

All standard graph operations as defined in §4, with `callback_manager` parameter for context propagation.

#### 10.4.4. Single Source of Truth Request Builders

```python
def _build_bulk_vertices_request(self, spec: BulkVerticesSpec) -> Mapping[str, Any]:
    """Single source of truth for bulk vertices request."""
    return {
        "namespace": spec.namespace,
        "limit": spec.limit,
        "cursor": spec.cursor,
        "filter": spec.filter,
    }

def _build_traversal_request(self, spec: GraphTraversalSpec) -> Mapping[str, Any]:
    """Single source of truth for traversal request."""
    return {
        "start_nodes": list(spec.start_nodes),
        "max_depth": spec.max_depth,
        "direction": spec.direction,
        "relationship_types": spec.relationship_types,
        "node_filters": spec.node_filters,
        "relationship_filters": spec.relationship_filters,
        "return_properties": spec.return_properties,
        "namespace": spec.namespace,
    }
```

### 10.5. Integration Helpers

#### 10.5.1. `CorpusGraphStore`

```python
class CorpusGraphStore(_LlamaIndexGraphStore):
    """
    LlamaIndex GraphStore implementation backed by CorpusLlamaIndexGraphClient.
    
    Maps triplet operations (subj, rel, obj) to graph queries via configurable templates.
    """
    
    def __init__(
        self,
        client: "CorpusLlamaIndexGraphClient",
        *,
        namespace: Optional[str] = None,
        get_query: Optional[str] = None,
        get_rel_map_query: Optional[str] = None,
        upsert_triplet_query: Optional[str] = None,
        delete_triplet_query: Optional[str] = None,
    ):
        """Initialize with client and optional query templates."""
        self._client = client
        self._namespace = namespace
        self._get_query = get_query
        self._get_rel_map_query = get_rel_map_query
        self._upsert_triplet_query = upsert_triplet_query
        self._delete_triplet_query = delete_triplet_query

        # Validation of query templates (normative)
        if get_query is not None and not isinstance(get_query, str):
            raise TypeError("get_query must be a string or None")
        if get_rel_map_query is not None and not isinstance(get_rel_map_query, str):
            raise TypeError("get_rel_map_query must be a string or None")
        if upsert_triplet_query is not None and not isinstance(upsert_triplet_query, str):
            raise TypeError("upsert_triplet_query must be a string or None")
        if delete_triplet_query is not None and not isinstance(delete_triplet_query, str):
            raise TypeError("delete_triplet_query must be a string or None")
```

### 10.6. Error Codes

```python
class ErrorCodes:
    BAD_OPERATION_CONTEXT = "BAD_OPERATION_CONTEXT"
    BAD_TRANSLATED_SCHEMA = "BAD_TRANSLATED_SCHEMA"
    BAD_HEALTH_RESULT = "BAD_HEALTH_RESULT"
    BAD_TRANSLATED_RESULT = "BAD_TRANSLATED_RESULT"
    BAD_TRANSLATED_CHUNK = "BAD_TRANSLATED_CHUNK"
    BAD_UPSERT_RESULT = "BAD_UPSERT_RESULT"
    BAD_DELETE_RESULT = "BAD_DELETE_RESULT"
    BAD_BULK_VERTICES_RESULT = "BAD_BULK_VERTICES_RESULT"
    BAD_TRAVERSAL_RESULT = "BAD_TRAVERSAL_RESULT"
    BAD_BATCH_RESULT = "BAD_BATCH_RESULT"
    BAD_TRANSACTION_RESULT = "BAD_TRANSACTION_RESULT"
    BAD_ADAPTER_RESULT = "BAD_ADAPTER_RESULT"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
    
    BAD_ASYNC_ITERATOR_SHAPE = "BAD_ASYNC_ITERATOR_SHAPE"
    INVALID_DELETE_SPEC = "INVALID_DELETE_SPEC"
    
    INVALID_QUERY = "INVALID_QUERY"
    INVALID_BATCH_OPS = "INVALID_BATCH_OPS"
```

### 10.7. LlamaIndex-Specific Context

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

The Semantic Kernel adapter exposes Corpus graph operations as SK plugins, enabling graph access in Semantic Kernel applications. It solves context propagation from SK's dual context/settings objects and provides forward-compatible method signatures.

### 11.2. Framework-Specific Challenges

| Challenge | Solution |
|-----------|----------|
| Context comes from both context and settings objects | `core_ctx_from_semantic_kernel()` handles both |
| Capabilities methods may evolve with new parameters | Forward kwargs with graceful TypeError fallback |
| Plugin architecture requires thin wrapper | `CorpusSemanticKernelPlugin` passthrough layer |
| Async streaming may return awaitable→AsyncIterator | `_normalize_async_iterator()` with explicit shape checking |

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

### 11.4. Core Class: `CorpusSemanticKernelGraphClient`

#### 11.4.1. Initialization

```python
def __init__(
    self,
    adapter: Optional[GraphProtocolV1] = None,
    *,
    graph_adapter: Optional[GraphProtocolV1] = None,
    default_dialect: Optional[str] = None,
    default_namespace: Optional[str] = None,
    default_timeout_ms: Optional[int] = None,
    framework_version: Optional[str] = None,
    framework_translator: Optional[GraphFrameworkTranslator] = None,
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
    # Enrich with framework metadata (best-effort)
    # Return None on failure
```

#### 11.4.3. Operations

All standard graph operations as defined in §4, with `context` and `settings` parameters for context propagation.

#### 11.4.4. Forward-Compatible Kwargs Handling

```python
@with_graph_error_context("capabilities_sync")
def capabilities(self, **kwargs: Any) -> Mapping[str, Any]:
    """
    Sync capabilities with forward-compatible kwargs handling.
    
    Attempts to pass kwargs to translator; falls back gracefully if not supported.
    """
    _ensure_not_in_event_loop("capabilities")
    
    try:
        caps = self._translator.capabilities(**kwargs)
    except TypeError:
        if kwargs:
            logger.debug("GraphTranslator.capabilities does not accept kwargs; ignoring")
        caps = self._translator.capabilities()
    
    return graph_capabilities_to_dict(caps)
```

### 11.5. Integration Helpers

#### 11.5.1. `CorpusSemanticKernelPlugin`

```python
class CorpusSemanticKernelPlugin:
    """
    Semantic Kernel plugin wrapper backed by CorpusSemanticKernelGraphClient.
    
    Provides passthrough methods for all graph operations with consistent
    namespace resolution and context propagation.
    """
    
    def __init__(
        self,
        client: "CorpusSemanticKernelGraphClient",
        *,
        namespace: Optional[str] = None,
    ):
        """Initialize with client and optional default namespace."""
        self._client = client
        self._namespace = namespace
    
    def query(
        self,
        query: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        dialect: Optional[str] = None,
        namespace: Optional[str] = None,
        timeout_ms: Optional[int] = None,
        context: Optional[Any] = None,
        settings: Optional[Any] = None,
        extra_context: Optional[Mapping[str, Any]] = None,
    ) -> QueryResult:
        """Query passthrough with namespace resolution."""
        effective_namespace = namespace if namespace is not None else self._namespace
        return self._client.query(
            query,
            params=params,
            dialect=dialect,
            namespace=effective_namespace,
            timeout_ms=timeout_ms,
            context=context,
            settings=settings,
            extra_context=extra_context,
        )
    
    # All other operations follow same pattern
```

### 11.6. Error Codes

```python
class ErrorCodes:
    BAD_OPERATION_CONTEXT = "BAD_OPERATION_CONTEXT"
    BAD_TRANSLATED_SCHEMA = "BAD_TRANSLATED_SCHEMA"
    BAD_HEALTH_RESULT = "BAD_HEALTH_RESULT"
    BAD_TRANSLATED_RESULT = "BAD_TRANSLATED_RESULT"
    BAD_TRANSLATED_CHUNK = "BAD_TRANSLATED_CHUNK"
    BAD_UPSERT_RESULT = "BAD_UPSERT_RESULT"
    BAD_DELETE_RESULT = "BAD_DELETE_RESULT"
    BAD_BULK_VERTICES_RESULT = "BAD_BULK_VERTICES_RESULT"
    BAD_TRAVERSAL_RESULT = "BAD_TRAVERSAL_RESULT"
    BAD_TRANSACTION_RESULT = "BAD_TRANSACTION_RESULT"
    BAD_BATCH_RESULT = "BAD_BATCH_RESULT"
    BAD_ADAPTER_RESULT = "BAD_ADAPTER_RESULT"
    SYNC_WRAPPER_CALLED_IN_EVENT_LOOP = "SYNC_WRAPPER_CALLED_IN_EVENT_LOOP"
    
    BAD_ASYNC_ITERATOR_SHAPE = "BAD_ASYNC_ITERATOR_SHAPE"
    INVALID_DELETE_SPEC = "INVALID_DELETE_SPEC"
    
    INVALID_QUERY = "INVALID_QUERY"
    INVALID_BATCH_OPS = "INVALID_BATCH_OPS"
```

### 11.7. Semantic Kernel-Specific Context

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

| Corpus Error Code | Framework Adapter Mapping | Retryable | Notes |
|-------------------|--------------------------|-----------|-------|
| `BAD_OPERATION_CONTEXT` | Log warning, continue without context | No | |
| `BAD_TRANSLATED_SCHEMA` | Raise TypeError with context | No | |
| `BAD_HEALTH_RESULT` | Raise TypeError with details | No | |
| `BAD_TRANSLATED_RESULT` | Raise TypeError with details | No | |
| `BAD_TRANSLATED_CHUNK` | Raise TypeError with details | No | |
| `BAD_UPSERT_RESULT` | Raise TypeError with details | No | |
| `BAD_DELETE_RESULT` | Raise TypeError with details | No | |
| `BAD_BULK_VERTICES_RESULT` | Raise TypeError with details | No | |
| `BAD_TRAVERSAL_RESULT` | Raise TypeError with details | No | |
| `BAD_BATCH_RESULT` | Raise TypeError with details | No | |
| `BAD_TRANSACTION_RESULT` | Raise TypeError with details | No | |
| `BAD_ADAPTER_RESULT` | Raise BadRequest with context | No | Used for delete spec validation |
| `SYNC_WRAPPER_CALLED_IN_EVENT_LOOP` | Raise RuntimeError | No | |
| `INVALID_QUERY` | Raise ValueError | No | |
| `INVALID_BATCH_OPS` | Raise ValueError | No | |
| `BAD_ASYNC_ITERATOR_SHAPE` | Raise TypeError | No | Used by adapters with explicit normalization |
| `INVALID_DELETE_SPEC` | Used in message string only | No | Error code field is `BAD_ADAPTER_RESULT` |

### 12.2. Retry Semantics

Adapters MUST NOT retry automatically unless configured to do so. When retrying:
- Honor `retry_after_ms` if present
- Use exponential backoff with jitter
- Do not retry validation errors (INVALID_* codes)
- Consider per-tenant retry budgets

### 12.3. Circuit Breaking Guidance

Implementations MAY implement circuit breakers:
- Open on repeated Unavailable or ResourceExhausted
- Half-open after configured timeout
- Per-tenant, per-operation circuits RECOMMENDED

---

## 13. Observability and Monitoring

### 13.1. Metrics Taxonomy (MUST)

All adapters MUST expose:

```
graph_operations_total{framework,operation,namespace,code}
graph_latency_ms{framework,operation,namespace,quantile}
graph_batch_size{framework,operation}  # histogram
graph_stream_chunks_total{framework,operation}
```

### 13.2. Structured Logging (MUST)

```json
{
  "timestamp": "2026-02-26T10:00:00Z",
  "level": "INFO",
  "framework": "langchain",
  "operation": "query",
  "tenant_hash": "a1b2c3...",
  "trace_id": "00-4bf9...",
  "namespace": "production",
  "query_len": 156,
  "latency_ms": 127.4,
  "code": "OK"
}
```

**Note:** `tenant_hash` is included only when available in `OperationContext.attrs`. Adapters do not generate tenant hashes.

### 13.3. Distributed Tracing (SHOULD)

- Propagate `traceparent` from operation context
- Create spans for each graph operation
- Include attributes: `framework`, `operation`, `namespace`, `tenant_hash` (when available)
- Final span status matches operation outcome

---

## 14. Security Considerations

### 14.1. Tenant Isolation (MUST)

- `tenant` in operation context MUST be used for isolation
- Never log raw tenant identifiers; use `tenant_hash` when available
- Caches MUST key by `tenant_hash` when `cache_scope="tenant"`

### 14.2. Credential Handling (MUST)

- Credentials for underlying graph adapters provisioned out-of-band
- Never log, snapshot, or expose credentials in error context

### 14.3. Log Redaction (MUST)

- All logs use `_safe_snapshot()` for object serialization
- Strings >5000 characters truncated
- Containers >200 items limited
- No raw query text, parameters, or vectors in logs
- Tenant identifiers never logged raw; `tenant_hash` used when available

---

## 15. Performance Characteristics

### 15.1. Latency Targets (Indicative)

These indicative ranges are not service-level agreements (SLAs) and may vary significantly based on backend implementation, dataset size, network topology, and deployment environment. They are provided for general guidance only.

| Operation Type | Typical Range | Notes |
|----------------|---------------|-------|
| Simple query | 10–100 ms | Depends on graph complexity |
| Complex traversal | 50–500 ms | Depth and filter dependent |
| Batch operation (10 ops) | 50–200 ms | Includes batching overhead |
| Streaming query | First chunk: 10–50 ms | Subsequent chunks streaming rate |
| Capabilities/Health | 1–10 ms | Cached where possible |

### 15.2. Concurrency Considerations

- All adapters are thread-safe for concurrent use
- Translator initialized lazily with locks
- Resource cleanup safe under concurrent access
- Tool bridge executors bounded (max_workers=4) for CrewAI/LangChain

### 15.3. Caching Strategies

- Graph schema can be cached with TTL
- Query results cacheable by `(namespace, query_text, params_hash)`
- Cache keys MUST include `tenant_hash` when tenant isolation is required
- Respect `cache_scope` and `cache_tags` when provided
- Never cache across tenant boundaries

---

## 16. Implementation Guidelines

### 16.1. Adapter Implementation Order

1. Copy shared utilities from existing adapter
2. Implement `__init__` with validation
3. Add error context decorators
4. Implement core graph methods (query, stream_query, etc.)
5. Add context extraction and building
6. Implement best-effort resource cleanup
7. Add validation helpers (`_validate_upsert_edges_spec`, `_validate_delete_spec`)
8. Add Single Source of Truth request builders
9. Implement integration helpers (tools, plugins, stores)
10. Write conformance tests

### 16.2. Validation Requirements (MUST)

- Validate adapter has required methods (`query`, `capabilities`)
- Validate query strings are non-empty
- Validate batch operations list and each operation
- Validate UpsertNodesSpec structure
- Validate UpsertEdgesSpec has non-None, iterable edges; each edge MUST have an ID (src/dst/label validation RECOMMENDED but not required; LlamaIndex aims for strict validation in future releases)
- Validate delete specs have either filter or non-empty ids (error code `BAD_ADAPTER_RESULT`, message SHOULD include `[INVALID_DELETE_SPEC]`)
- For CrewAI/LangChain tools, numeric parameters SHOULD use coercion with `coerce_bounded_positive_int()` or `validated_max_chunks()`

### 16.3. Testing

#### 16.3.1. Conformance Test Suite

Each adapter MUST pass:
- Operation method coverage (all sync/async pairs)
- Error context attachment tests
- Context building tests (including failure cases)
- Batch operation tests (empty, single, multiple)
- Streaming tests (sync and async) verifying semantic equivalence
- Event loop guard tests
- Resource cleanup tests (idempotency, best-effort)
- Namespace resolution tests (precedence rules)
- Delete operation validation tests

#### 16.3.2. Framework-Specific Tests

- **AutoGen:** Tool creation, conversation context extraction
- **CrewAI:** Task context extraction, tool bridge executor, parameter coercion using `coerce_bounded_positive_int()`
- **LangChain:** Config context extraction, close() coroutine handling, tool creation, parameter coercion using `validated_max_chunks()`
- **LlamaIndex:** Callback manager context, GraphStore triplet mapping, request builders, template validation, edge validation (minimum requirements)
- **Semantic Kernel:** Context+settings translation, kwargs forwarding, plugin wrapper

#### 16.3.3. Cross-Adapter Tests

- All adapters produce identical results for same inputs when backed by identical graph adapter and translator configuration (see §6.7)
- Error taxonomy consistent across frameworks
- Observability fields follow same patterns
- Namespace resolution identical across all
- Delete validation patterns consistent (all use `BAD_ADAPTER_RESULT` with `[INVALID_DELETE_SPEC]` in message)

---

## 17. Versioning and Compatibility

### 17.1. Semantic Versioning (MUST)

Adapter packages MUST use Semantic Versioning:
- MAJOR: Breaking changes to public API
- MINOR: Additive, backward-compatible features
- PATCH: Bug fixes and internal improvements

### 17.2. Framework Version Compatibility

Adapters MUST document supported framework versions in package metadata (e.g., `pyproject.toml`) and/or README.

**Recommended testing matrix:**
- AutoGen: ≥0.4.0
- CrewAI: ≥0.30.0
- LangChain: ≥0.1.0, ≤0.3.x
- LlamaIndex: ≥0.10.0
- Semantic Kernel: ≥1.0.0

### 17.3. Deprecation Policy

- Deprecated features documented for one minor version
- Removal only in MAJOR version bump
- Migration guides provided for breaking changes

---

## 18. References

### 18.1. Normative References

- [RFC2119] Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, March 1997.
- [RFC8174] Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words", BCP 14, RFC 8174, May 2017.
- Corpus Graph Protocol V1.0 Specification
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
| AutoGen | Agent tool interfaces + async-only runtime | FunctionTool wrappers, fully async tools |
| CrewAI | No shared runtime context + LLM parameter safety | Task context extraction + parameter coercion |
| LangChain | Config evolution + sync-in-async deadlocks | Structural context extraction + worker thread bridge |
| LlamaIndex | Triplet operations + callback propagation | Configurable query templates + RECOMMENDED strict validation |
| Semantic Kernel | Dual context/settings + forward compatibility | Combined translation + kwargs fallback |

---

## Appendix B — Code Pattern Catalog (Normative)

### B.1. Context Building Patterns

```python
# Framework-specific context building (best-effort)
def _build_ctx(self, *, framework_input=None, extra_context=None):
    try:
        ctx = core_ctx_from_framework(framework_input, **extra_context)
    except Exception:
        logger.warning("Context translation failed")
        return None
    
    if not _looks_like_operation_context(ctx):
        return None
    
    # Enrich with framework metadata (best-effort)
    try:
        attrs = getattr(ctx, "attrs", {})
        if isinstance(attrs, dict):
            attrs.setdefault("framework", self._framework_name)
            if self._framework_version:
                attrs.setdefault("framework_version", self._framework_version)
    except Exception:
        pass
    
    return ctx
```

### B.2. Event Loop Safety Patterns

```python
# Guard pattern
_ensure_not_in_event_loop("sync_method")

# Tool bridge pattern (bounded thread pool) - CrewAI/LangChain only
def _run_in_tool_thread(fn):
    return _TOOL_BRIDGE_EXECUTOR.submit(fn).result()

# Close coroutine handling
result = close_fn()
if inspect.iscoroutine(result):
    result.close()  # Suppress warning
    logger.warning("Use aclose() for async close")
```

### B.3. Async Streaming Patterns

```python
# Option 1: Adapter-level normalization (LlamaIndex, Semantic Kernel)
aiter_or_awaitable = translator.arun_query_stream(...)
normalized = _normalize_async_iterator(aiter_or_awaitable)

if inspect.isawaitable(normalized):
    aiter = await normalized
else:
    aiter = normalized

if not _is_async_iterator(aiter):
    raise TypeError(f"Invalid stream shape [{ErrorCodes.BAD_ASYNC_ITERATOR_SHAPE}]")

async for chunk in aiter:
    yield chunk

# Option 2: Trust translator (AutoGen, CrewAI, LangChain)
async for chunk in translator.arun_query_stream(...):
    yield chunk
```

### B.4. Resource Cleanup Patterns

```python
# Sync cleanup with idempotency (best-effort)
def close(self):
    if self._closed:
        return
    self._closed = True
    _maybe_close_sync(self._resource)

# Async cleanup with fallback
async def aclose(self):
    if self._aclosed:
        return
    self._aclosed = True
    
    if hasattr(self._resource, "aclose"):
        await self._resource.aclose()
        self._closed = True
        return
    
    self.close()
```

### B.5. Delete Operation Validation Patterns

```python
# Shared validation for delete specs
def _validate_delete_spec(self, *, spec_filter, spec_ids, empty_message):
    if spec_filter is not None:
        return spec_filter
    
    ids = list(spec_ids or [])
    if not ids:
        raise BadRequest(
            f"{empty_message} [INVALID_DELETE_SPEC]",
            code=ErrorCodes.BAD_ADAPTER_RESULT,
        )
    return ids
```

### B.6. Single Source of Truth Request Builders

```python
# Bulk vertices request builder
def _build_bulk_vertices_request(self, spec):
    return {
        "namespace": spec.namespace,
        "limit": spec.limit,
        "cursor": spec.cursor,
        "filter": spec.filter,
    }

# Traversal request builder  
def _build_traversal_request(self, spec):
    return {
        "start_nodes": list(spec.start_nodes),
        "max_depth": spec.max_depth,
        "direction": spec.direction,
        "relationship_types": spec.relationship_types,
        "node_filters": spec.node_filters,
        "relationship_filters": spec.relationship_filters,
        "return_properties": spec.return_properties,
        "namespace": spec.namespace,
    }
```

---

## Appendix C — End-to-End Usage Examples

### C.1. AutoGen Agent with Graph Tools

```python
from corpus_sdk.graph.framework_adapters.autogen import (
    CorpusAutoGenGraphClient,
    create_autogen_graph_tools,
)
from autogen_agentchat.agents import AssistantAgent

# Create client
client = CorpusAutoGenGraphClient(
    graph_adapter=my_graph_adapter,
    default_namespace="production"
)

# Create tools (fully async)
tools = create_autogen_graph_tools(
    client,
    name_prefix="knowledge",
    description_prefix="Knowledge graph operations"
)

# Use in agent
agent = AssistantAgent(
    name="graph_agent",
    tools=tools,
    model_client=model_client,
)
```

### C.2. CrewAI Crew with Graph Tools

```python
from corpus_sdk.graph.framework_adapters.crewai import (
    CorpusCrewAIGraphClient,
    create_crewai_graph_tools,
)
from crewai import Agent, Crew

# Create client
client = CorpusCrewAIGraphClient(
    graph_adapter=my_graph_adapter,
    default_namespace="analytics"
)

# Create tools  
tools = create_crewai_graph_tools(
    client,
    name_prefix="graph",
    description_prefix="Graph database operations"
)

# Create agent with tools
agent = Agent(
    role="Graph Researcher",
    goal="Query the knowledge graph",
    backstory="I specialize in graph queries",
    tools=tools,
)

crew = Crew(agents=[agent], tasks=[...])
```

### C.3. LangChain Agent with Graph Tools

```python
from corpus_sdk.graph.framework_adapters.langchain import (
    CorpusLangChainGraphClient,
    create_langchain_graph_tools,
)
from langchain.agents import AgentExecutor, create_openai_tools_agent

# Create client
client = CorpusLangChainGraphClient(
    graph_adapter=my_graph_adapter,
    default_namespace="research"
)

# Create tools
tools = create_langchain_graph_tools(
    client,
    name_prefix="knowledge",
    description_prefix="Knowledge graph queries"
)

# Use in agent
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)
```

### C.4. LlamaIndex Knowledge Graph Index

```python
from corpus_sdk.graph.framework_adapters.llamaindex import (
    CorpusLlamaIndexGraphClient,
    CorpusGraphStore,
)
from llama_index.core import KnowledgeGraphIndex

# Create client
client = CorpusLlamaIndexGraphClient(
    graph_adapter=my_graph_adapter,
    default_namespace="kg"
)

# Create GraphStore with triplet queries
graph_store = CorpusGraphStore(
    client,
    namespace="kg",
    get_query="MATCH (n {{id: $subj}})-[r]->(m) RETURN n.id, type(r), m.id",
    upsert_triplet_query=(
        "MERGE (s {{id: $subj}}) "
        "MERGE (o {{id: $obj}}) "
        "MERGE (s)-[r:{{label: $rel}}]->(o)"
    )
)

# Use in index
index = KnowledgeGraphIndex.from_documents(
    documents,
    graph_store=graph_store
)
```

### C.5. Semantic Kernel Plugin Registration

```python
from corpus_sdk.graph.framework_adapters.semantic_kernel import (
    CorpusSemanticKernelGraphClient,
    CorpusSemanticKernelPlugin,
)
import semantic_kernel as sk

# Create client
client = CorpusSemanticKernelGraphClient(
    graph_adapter=my_graph_adapter,
    default_namespace="enterprise"
)

# Create plugin
plugin = CorpusSemanticKernelPlugin(
    client,
    namespace="enterprise"
)

# Register with kernel
kernel = sk.Kernel()
kernel.add_plugin(plugin, plugin_name="graph")

# Use in semantic function
result = await kernel.run_async(
    kernel.create_semantic_function(
        "Find entities related to: {{$input}} using graph.query"
    ),
    input="machine learning"
)
```

---

## Appendix D — Error Code Reference

| Code | Description | Frameworks | Notes |
|------|-------------|------------|-------|
| `BAD_OPERATION_CONTEXT` | Failed to build OperationContext | All | |
| `BAD_TRANSLATED_SCHEMA` | Schema result has wrong type | All | |
| `BAD_HEALTH_RESULT` | Health result not a mapping | All | |
| `BAD_TRANSLATED_RESULT` | Query result has wrong type | All | |
| `BAD_TRANSLATED_CHUNK` | Query chunk has wrong type | All | |
| `BAD_UPSERT_RESULT` | Upsert result has wrong type | All | |
| `BAD_DELETE_RESULT` | Delete result has wrong type | All | |
| `BAD_BULK_VERTICES_RESULT` | Bulk vertices result wrong type | All | |
| `BAD_TRAVERSAL_RESULT` | Traversal result wrong type | All | |
| `BAD_BATCH_RESULT` | Batch result wrong type | All | |
| `BAD_TRANSACTION_RESULT` | Transaction result wrong type | All | |
| `BAD_ADAPTER_RESULT` | Adapter returned invalid data | All | Used for delete spec validation |
| `SYNC_WRAPPER_CALLED_IN_EVENT_LOOP` | Sync method called from async context | All | |
| `INVALID_QUERY` | Query validation failed | All | |
| `INVALID_BATCH_OPS` | Batch operations validation failed | All | |
| `BAD_ASYNC_ITERATOR_SHAPE` | Async stream returned invalid shape | LlamaIndex, Semantic Kernel | |
| `INVALID_DELETE_SPEC` | Delete spec missing filter and ids | Used in message only | Error code field is `BAD_ADAPTER_RESULT` |
| `INVALID_TOOL_PARAM` | Invalid tool parameter | CrewAI | |

---

## Appendix E — Implementation Status (Non-Normative)

| Adapter | Status | Conformance | Framework Versions | Notes |
|---------|--------|-------------|-------------------|-------|
| AutoGen | Stable | 100% | ≥0.4.0 | Fully async tools, no thread pool |
| CrewAI | Stable | 100% | ≥0.30.0 | Parameter coercion, thread pool |
| LangChain | Stable | 100% | 0.1.x, 0.2.x, 0.3.x | Parameter validation, thread pool |
| LlamaIndex | Stable | 100% | ≥0.10.0 | RECOMMENDED strict validation (id/src/dst/label/JSON); current enforces minimum |
| Semantic Kernel | Stable | 100% | ≥1.0.0 | Strict validation, explicit streaming checks |

**Note:** This appendix is non‑normative and provided for informational purposes only. The authoritative conformance status is determined by the conformance test suite (§16.3) and the implementation’s own documentation.

---

## Appendix F — Migration from Existing Framework Adapters (Informative)

### From Custom AutoGen Graph Tools

```python
# Before
class MyAutoGenGraphTools:
    def query(self, query):
        return my_graph.query(query)

# After
from corpus_sdk.graph.framework_adapters.autogen import (
    CorpusAutoGenGraphClient,
    create_autogen_graph_tools,
)

client = CorpusAutoGenGraphClient(my_graph_adapter)
tools = create_autogen_graph_tools(client)
```

### From Custom CrewAI Graph Tools

```python
# Before
class MyCrewAIGraphTools:
    def _run(self, query):
        return my_graph.query(query)

# After
from corpus_sdk.graph.framework_adapters.crewai import (
    CorpusCrewAIGraphClient,
    create_crewai_graph_tools,
)

client = CorpusCrewAIGraphClient(my_graph_adapter)
tools = create_crewai_graph_tools(client)
```

### From Custom LangChain Graph Tools

```python
# Before
class MyLangChainTool(BaseTool):
    def _run(self, query):
        return my_graph.query(query)

# After
from corpus_sdk.graph.framework_adapters.langchain import (
    CorpusLangChainGraphClient,
    create_langchain_graph_tools,
)

client = CorpusLangChainGraphClient(my_graph_adapter)
tools = create_langchain_graph_tools(client)
```

### From Custom LlamaIndex GraphStore

```python
# Before
class MyGraphStore(GraphStore):
    def get(self, subj):
        return my_graph.query(f"MATCH ... WHERE id = '{subj}'")

# After
from corpus_sdk.graph.framework_adapters.llamaindex import (
    CorpusLlamaIndexGraphClient,
    CorpusGraphStore,
)

client = CorpusLlamaIndexGraphClient(my_graph_adapter)
graph_store = CorpusGraphStore(
    client,
    get_query="MATCH (n {{id: $subj}})-[r]->(m) RETURN ..."
)
```

### From Custom Semantic Kernel Plugin

```python
# Before
class MyGraphPlugin:
    @sk_function
    def query(self, context):
        return my_graph.query(context["query"])

# After
from corpus_sdk.graph.framework_adapters.semantic_kernel import (
    CorpusSemanticKernelGraphClient,
    CorpusSemanticKernelPlugin,
)

client = CorpusSemanticKernelGraphClient(my_graph_adapter)
plugin = CorpusSemanticKernelPlugin(client)
kernel.add_plugin(plugin, "graph")
```
