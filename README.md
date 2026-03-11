# Corpus OS 

<img width="1128" height="191" alt="image" src="https://github.com/user-attachments/assets/cb2fe4ef-be6a-4406-b899-23ad1ed30c08" />


![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-Apache--2.0-green)
![LLM Protocol](https://img.shields.io/badge/LLM%20Protocol-100%25%20Conformant-brightgreen)
![Vector Protocol](https://img.shields.io/badge/Vector%20Protocol-100%25%20Conformant-brightgreen)
![Graph Protocol](https://img.shields.io/badge/Graph%20Protocol-100%25%20Conformant-brightgreen)
![Embedding Protocol](https://img.shields.io/badge/Embedding%20Protocol-100%25%20Conformant-brightgreen)
![Tests](https://img.shields.io/badge/Conformance%20Tests-3%2C330-brightgreen)

Reference implementation of the **[Corpus OS](https://corpusos.com)** — a **wire-first, vendor-neutral** SDK for interoperable AI frameworks and data backends across four domains: **LLM**, **Embedding**, **Vector**, and **Graph**.

---
**Contact:** [team@corpusos.com](mailto:team@corpusos.com) 
**Website:** [https://corpusos.com](https://corpusos.com) 
**Docs:** [https://docs.corpusos.com](https://docs.corpusos.com) 

---

```
┌──────────────────────────────────────────────────────────────────────┐
│  Your App / Agents / RAG Pipelines                                   │
│  (LangChain · LlamaIndex · Semantic Kernel · CrewAI · AutoGen · MCP) │
├──────────────────────────────────────────────────────────────────────┤
│  Corpus OS Protocol and SDK.                                         │
│  One protocol · One error taxonomy · One metrics model               │
├──────────┬──────────────┬────────────┬───────────────────────────────┤
│ LLM/v1   │ Embedding/v1 │ Vector/v1  │ Graph/v1                      │
├──────────┴──────────────┴────────────┴───────────────────────────────┤
│  Any Provider: OpenAI · Anthropic · Pinecone · Neo4j · ...           │
└──────────────────────────────────────────────────────────────────────┘
```

**Keep your frameworks. Standardize your infrastructure.**

> **Open-Core Model**: The **[Corpus OS](https://corpusos.com)** Protocol Suite and SDK are **fully open source** (Apache-2.0). Corpus Router and official production adapters are **commercial**, optional, and built on the same public protocols. Using this SDK does **not** lock you into CORPUS Router.

---

## Table of Contents

1. [Why CORPUS](#why-corpus)
2. [How CORPUS Compares](#how-corpus-compares)
3. [When Not to Use CORPUS](#when-not-to-use-corpus)
4. [Install](#install)
5. [Quick Start](#-quick-start)
6. [Domain Examples](#domain-examples)
7. [Core Concepts](#core-concepts)
8. [Error Taxonomy & Observability](#error-taxonomy--observability)
9. [Performance & Configuration](#performance--configuration)
10. [Testing & Conformance](#testing--conformance)
11. [Documentation Layout](#-documentation-layout)
12. [FAQ](#faq)
13. [Contributing](#contributing)
14. [License & Commercial Options](#license--commercial-options)

---

## Why Corpus OS

Modern AI platforms juggle multiple LLM, embedding, vector, and graph backends. Each vendor ships unique APIs, error schemes, rate limits, and capabilities — making cross-provider integration brittle and costly.

**The problem:**

- **Provider proliferation** — Dozens of incompatible APIs across AI infrastructure
- **Duplicate integration** — Different error handling, observability, and resilience patterns rewritten per provider and framework
- **Vendor lock-in** — Applications tightly coupled to specific backend choices
- **Operational complexity** — Inconsistent monitoring and debugging across services

**Corpus OS provides:**

- **Stable, runtime-checkable protocols** across all four domains
- **Normalized errors** with retry hints and machine-actionable scopes
- **SIEM-safe metrics** (low-cardinality, tenant-hashed, no PII)
- **Deadline propagation** for cancellation and cost control
- **Two modes** — compose under your own router (`thin`) or use lightweight built-in infra (`standalone`)
- **Wire-first design** — canonical JSON envelopes implementable in any language, with this SDK as reference

Corpus OS is **not** a replacement for LangChain, LlamaIndex, Semantic Kernel, CrewAI, AutoGen, or MCP. Use those for agent-specific orchestration, agents, tools, and RAG pipelines. Use Corpus OS to standardize the **infrastructure layer underneath them**. Your app teams keep their frameworks. Your platform team gets one protocol, one error taxonomy, and one observability model across everything.

---

## How Corpus OS Compares

| Aspect | LangChain / LlamaIndex | OpenRouter | MCP | **Corpus OS** |
|---|---|---|---|---|
| **Scope** | Application framework | LLM unification | Tools & data sources | **AI infrastructure protocols** |
| **Domains** | LLM + Tools | LLM only | Tools + Data | **LLM + Vector + Graph + Embedding** |
| **Error Standardization** | Partial | Limited | N/A | **Comprehensive taxonomy** |
| **Multi-Provider Routing** | Basic | Managed service | N/A | **Protocol for any router** |
| **Observability** | Basic | Limited | N/A | **Built-in metrics + tracing** |
| **Vendor Neutrality** | High | Service-dependent | High | **Protocol-first, no lock-in** |

### Who is this for?

- **App developers** — Keep using your framework of choice. Talk to all backends through Corpus OS protocols. Swap providers or frameworks without rewriting integration code.
- **Framework maintainers** — Implement one CORPUS adapter per protocol. Instantly support any conformant backend.
- **Backend vendors** — Implement `llm/v1`, `embedding/v1`, `vector/v1`, or `graph/v1` once, run the conformance suite, and your service works with every framework.
- **Platform / infra teams** — Unified observability: normalized error codes, deadlines, and metrics. One set of dashboards and SLOs across all AI traffic.
- **MCP users** — The Corpus OS MCP server exposes protocols as standard MCP tools. Any MCP client can call into your infra with consistent behavior.

### Integration Patterns

| Pattern | How It Works | What You Get |
|---|---|---|
| Framework → Corpus OS → Providers | Framework uses Corpus OS as client | Unified errors/metrics across providers |
| Corpus OS → Framework-as-adapter → Providers | Framework wrapped as Corpus OS adapter | Reuse existing chains/indices as "providers" |
| Mixed | Both of the above | Gradual migration, no big-bang rewrites |

Large teams typically run all three patterns at once.

---

## When Not to Use CORPUS

You probably don't need Corpus OS if:

- **Single-provider and happy** — One backend, fine with their SDK and breaking changes.
- **No governance pressure** — No per-tenant isolation, budgets, audit trails, or data residency.
- **No cross-domain orchestration** — Not coordinating LLM + Vector + Graph + Embedding together.
- **Quick throwaway prototype** — Lock-in, metrics, and resilience aren't worth thinking about yet.

If any of these stop being true, `corpus_sdk` is the incremental next step.

---

## Install

```bash
pip install corpus_sdk
```

Python ≥ 3.10 recommended. No heavy runtime dependencies.

---

## ⚡ Quick Start

```python
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
```

A complete quick start with all four protocols is in [`docs/guides/QUICK_START.md`](docs/guides/QUICK_START.md).

---

## Domain Examples

> **Minimal viable adapter:** Implement `_do_capabilities`, your core operation (`_do_embed`, `_do_complete`, `_do_query`, etc.), and `_do_health`. All other methods have safe no-op defaults — you only override what you need.

> In all examples, swap `Example*Adapter` with your actual adapter class that inherits the corresponding base and implements `_do_*` hooks.

<details>
<summary><strong>Embeddings</strong></summary>

```python
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
```
</details>

<details>
<summary><strong>LLM</strong></summary>

```python
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
```
</details>

<details>
<summary><strong>Vector</strong></summary>

```python

import asyncio
from corpus_sdk.vector.vector_base import (
    BaseVectorAdapter, VectorCapabilities, QuerySpec, UpsertSpec, UpsertResult,
    QueryResult, Vector, VectorMatch, OperationContext, VectorID
)

class QuickVectorAdapter(BaseVectorAdapter):
    def __init__(self):
        super().__init__()
        # Simple in-memory storage
        self.vectors = {}
    
    async def _do_capabilities(self) -> VectorCapabilities:
        return VectorCapabilities(
            server="quick-vector",
            version="1.0.0",
            max_dimensions=3
        )

    async def _do_upsert(self, spec: UpsertSpec, *, ctx=None) -> UpsertResult:
        """Store vectors in memory"""
        ns = spec.namespace or "default"
        if ns not in self.vectors:
            self.vectors[ns] = []
        self.vectors[ns].extend(spec.vectors)
        
        return UpsertResult(
            upserted_count=len(spec.vectors),
            failed_count=0,
            failures=[]
        )

    async def _do_query(self, spec: QuerySpec, *, ctx=None) -> QueryResult:
        """Search for similar vectors"""
        ns = spec.namespace or "default"
        stored_vectors = self.vectors.get(ns, [])
        
        # Simple cosine similarity
        def cosine_sim(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            mag_a = sum(x * x for x in a) ** 0.5
            mag_b = sum(x * x for x in b) ** 0.5
            return dot / (mag_a * mag_b) if mag_a and mag_b else 0
        
        matches = []
        for vec in stored_vectors:
            score = cosine_sim(spec.vector, vec.vector)
            matches.append(VectorMatch(vector=vec, score=score, distance=1-score))
        
        # Sort by score descending
        matches.sort(key=lambda m: m.score, reverse=True)
        top_matches = matches[:spec.top_k] if spec.top_k else matches
        
        return QueryResult(
            matches=top_matches,
            query_vector=spec.vector,
            namespace=ns,
            total_matches=len(top_matches),
        )

    async def _do_health(self, *, ctx=None) -> dict:
        return {"ok": True, "server": "quick-vector", "version": "1.0.0"}

# Usage - Complete flow
async def main():
    print("=" * 80)
    print("Quick Vector Adapter Demo")
    print("=" * 80)
    
    adapter = QuickVectorAdapter()
    ctx = OperationContext(request_id="req-3", tenant="acme")
    
    # Test 1: Capabilities
    caps = await adapter.capabilities()
    print(f"\n✅ Capabilities:")
    print(f"   Server: {caps.server} v{caps.version}")
    print(f"   Max dimensions: {caps.max_dimensions}")
    
    # Test 2: Upsert vectors
    vectors_to_add = [
        Vector(id=VectorID("v1"), vector=[0.1, 0.2, 0.3], metadata={"label": "first"}),
        Vector(id=VectorID("v2"), vector=[0.4, 0.5, 0.6], metadata={"label": "second"}),
        Vector(id=VectorID("v3"), vector=[0.7, 0.8, 0.9], metadata={"label": "third"}),
    ]
    
    upsert_result = await adapter.upsert(
        UpsertSpec(vectors=vectors_to_add),
        ctx=ctx
    )
    print(f"\n✅ Upsert:")
    print(f"   Upserted: {upsert_result.upserted_count} vectors")
    print(f"   Failed: {upsert_result.failed_count} vectors")
    
    # Test 3: Query for similar vectors (top_k=2 REQUIRED by SDK)
    query_result = await adapter.query(
        QuerySpec(vector=[0.1, 0.2, 0.3], top_k=2),
        ctx=ctx
    )
    print(f"\n✅ Query (top 2):")
    print(f"   Query vector: {query_result.query_vector}")
    print(f"   Total matches: {query_result.total_matches}")
    print(f"   Results:")
    for i, match in enumerate(query_result.matches, 1):
        print(f"      {i}. ID: {match.vector.id}, Score: {match.score:.3f}, Distance: {match.distance:.3f}")
        print(f"         Metadata: {match.vector.metadata}")
    
    # Test 4: Query all vectors (with top_k=10)
    query_result_all = await adapter.query(
        QuerySpec(vector=[0.5, 0.5, 0.5], top_k=10),
        ctx=ctx
    )
    print(f"\n✅ Query (all matches):")
    print(f"   Query vector: [0.5, 0.5, 0.5]")
    print(f"   Total matches: {query_result_all.total_matches}")
    for i, match in enumerate(query_result_all.matches, 1):
        print(f"      {i}. ID: {match.vector.id}, Score: {match.score:.3f}")
    
    # Test 5: Namespace support
    ns_vectors = [
        Vector(id=VectorID("ns1"), vector=[0.9, 0.8, 0.7], metadata={"type": "namespace_test"}),
    ]
    upsert_ns = await adapter.upsert(
        UpsertSpec(vectors=ns_vectors, namespace="test-namespace"),
        ctx=ctx
    )
    print(f"\n✅ Namespace Support:")
    print(f"   Upserted {upsert_ns.upserted_count} vector(s) to 'test-namespace'")
    
    query_ns = await adapter.query(
        QuerySpec(vector=[0.9, 0.8, 0.7], top_k=5, namespace="test-namespace"),
        ctx=ctx
    )
    print(f"   Query in 'test-namespace': {query_ns.total_matches} match(es)")
    
    # Test 6: Health check
    health = await adapter.health()
    print(f"\n✅ Health Check:")
    print(f"   OK: {health.get('ok', False)}")
    print(f"   Server: {health.get('server', 'unknown')} v{health.get('version', 'unknown')}")
    
    print("\n" + "=" * 80)
    print("✅ All tests passed!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())

```
</details>

<details>
<summary><strong>Graph</strong></summary>

```python
import asyncio
from corpus_sdk.graph.graph_base import (
    BaseGraphAdapter, GraphCapabilities, UpsertNodesSpec,
    Node, GraphID, OperationContext, GraphQuerySpec, QueryResult
)

class QuickGraphAdapter(BaseGraphAdapter):
    def __init__(self):
        super().__init__()
        # Simple in-memory storage
        self.nodes = {}
    
    async def _do_capabilities(self) -> GraphCapabilities:
        return GraphCapabilities(
            server="quick-graph",
            version="1.0.0",
            supported_query_dialects=("cypher",),
            supports_stream_query=True,
            supports_bulk_vertices=True,
            supports_batch=True,
            supports_schema=True,
        )

    async def _do_upsert_nodes(self, spec: UpsertNodesSpec, *, ctx=None):
        # Store nodes in memory
        for node in spec.nodes:
            self.nodes[str(node.id)] = node
        
        from corpus_sdk.graph.graph_base import UpsertResult
        return UpsertResult(
            upserted_count=len(spec.nodes),
            failed_count=0,
            failures=[]
        )

    async def _do_query(self, spec: GraphQuerySpec, *, ctx=None) -> QueryResult:
        return QueryResult(
            records=[{"id": 1, "name": "Ada"}],
            summary={"rows": 1},
            dialect=spec.dialect,
            namespace=spec.namespace or "default",
        )

    async def _do_health(self, *, ctx=None) -> dict:
        return {"ok": True, "server": "quick-graph", "version": "1.0.0"}

# Usage
async def main():
    print("=" * 80)
    print("Quick Graph Adapter Demo")
    print("=" * 80)
    
    async with QuickGraphAdapter() as adapter:
        ctx = OperationContext(request_id="req-4", tenant="acme")
        
        # Test 1: Capabilities
        caps = await adapter.capabilities()
        print(f"\n✅ Capabilities:")
        print(f"   Server: {caps.server} v{caps.version}")
        print(f"   Supported dialects: {caps.supported_query_dialects}")
        print(f"   Supports streaming: {caps.supports_stream_query}")
        print(f"   Supports bulk vertices: {caps.supports_bulk_vertices}")
        print(f"   Supports batch: {caps.supports_batch}")
        print(f"   Supports schema: {caps.supports_schema}")
        
        # Test 2: Upsert nodes
        result = await adapter.upsert_nodes(
            UpsertNodesSpec(nodes=[
                Node(
                    id=GraphID("user:1"),
                    labels=("User",),
                    properties={"name": "Ada"}
                ),
                Node(
                    id=GraphID("user:2"),
                    labels=("User",),
                    properties={"name": "Bob"}
                )
            ])
        )
        print(f"\n✅ Upsert Nodes:")
        print(f"   Upserted: {result.upserted_count} nodes")
        print(f"   Failed: {result.failed_count} nodes")
        
        # Test 3: Query the graph
        query_result = await adapter.query(
            GraphQuerySpec(
                text="MATCH (u:User) RETURN u.name",
                dialect="cypher"
            )
        )
        print(f"\n✅ Query:")
        print(f"   Query: MATCH (u:User) RETURN u.name")
        print(f"   Dialect: {query_result.dialect}")
        print(f"   Records: {query_result.records}")
        print(f"   Summary: {query_result.summary}")
        
        # Test 4: Check stored nodes
        print(f"\n✅ Storage Check:")
        print(f"   Total nodes in memory: {len(adapter.nodes)}")
        for node_id, node in adapter.nodes.items():
            print(f"   - {node_id}: labels={node.labels}, properties={node.properties}")
        
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
```
</details>

<details>
<summary><strong> RAG flow </strong></summary>

```python
"""
RAG (Retrieval-Augmented Generation) Example
Demonstrates combining Embedding, Vector, and LLM protocols
"""
import asyncio
from corpus_sdk.llm.llm_base import (
    BaseLLMAdapter, OperationContext, LLMCompletion,
    TokenUsage, LLMCapabilities
)
from corpus_sdk.embedding.embedding_base import (
    BaseEmbeddingAdapter, EmbedSpec, EmbeddingVector, 
    EmbeddingCapabilities, EmbedResult
)
from corpus_sdk.vector.vector_base import (
    BaseVectorAdapter, VectorCapabilities, QuerySpec, UpsertSpec, UpsertResult,
    QueryResult, Vector, VectorMatch, VectorID
)


# 1. Embedding Adapter
class QuickEmbeddingAdapter(BaseEmbeddingAdapter):
    async def _do_capabilities(self) -> EmbeddingCapabilities:
        return EmbeddingCapabilities(
            server="quick-embeddings",
            version="1.0.0",
            supported_models=("quick-embed-001",),
            max_batch_size=128,
            max_text_length=8192,
        )

    async def _do_embed(self, spec: EmbedSpec, *, ctx=None) -> EmbedResult:
        # Deterministic embedding based on text content
        vec = [hash(spec.text + str(i)) % 1000 / 1000.0 for i in range(384)]
        return EmbedResult(
            embedding=EmbeddingVector(
                vector=vec,
                text=spec.text,
                model=spec.model,
                dimensions=len(vec)
            ),
            model=spec.model,
            text=spec.text,
            tokens_used=len(spec.text.split()),
            truncated=False,
        )

    async def _do_health(self, *, ctx=None) -> dict:
        return {"ok": True, "server": "quick-embeddings"}


# 2. Vector Store Adapter
class QuickVectorAdapter(BaseVectorAdapter):
    def __init__(self):
        super().__init__()
        self.vectors = {}
    
    async def _do_capabilities(self) -> VectorCapabilities:
        return VectorCapabilities(
            server="quick-vector",
            version="1.0.0",
            max_dimensions=384
        )

    async def _do_upsert(self, spec: UpsertSpec, *, ctx=None) -> UpsertResult:
        ns = spec.namespace or "default"
        if ns not in self.vectors:
            self.vectors[ns] = []
        self.vectors[ns].extend(spec.vectors)
        
        return UpsertResult(
            upserted_count=len(spec.vectors),
            failed_count=0,
            failures=[]
        )

    async def _do_query(self, spec: QuerySpec, *, ctx=None) -> QueryResult:
        ns = spec.namespace or "default"
        stored = self.vectors.get(ns, [])
        
        # Cosine similarity
        def cosine_sim(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            mag_a = sum(x * x for x in a) ** 0.5
            mag_b = sum(x * x for x in b) ** 0.5
            return dot / (mag_a * mag_b) if mag_a and mag_b else 0
        
        matches = []
        for vec in stored:
            score = cosine_sim(spec.vector, vec.vector)
            matches.append(VectorMatch(vector=vec, score=score, distance=1-score))
        
        matches.sort(key=lambda m: m.score, reverse=True)
        top_k = matches[:spec.top_k] if spec.top_k else matches
        
        return QueryResult(
            matches=top_k,
            query_vector=spec.vector,
            namespace=ns,
            total_matches=len(top_k),
        )

    async def _do_health(self, *, ctx=None) -> dict:
        return {"ok": True, "server": "quick-vector"}


# 3. LLM Adapter
class QuickLLMAdapter(BaseLLMAdapter):
    async def _do_capabilities(self) -> LLMCapabilities:
        return LLMCapabilities(
            server="quick-llm",
            version="1.0.0",
            model_family="gpt-4",
            max_context_length=8192,
        )

    async def _do_complete(self, messages, model, **kwargs) -> LLMCompletion:
        # Extract the last user message
        user_msg = messages[-1]["content"] if messages else ""
        
        # Simple mock: generate response based on context presence
        if "Corpus SDK" in user_msg:
            response = "Based on the documentation, Corpus SDK is a protocol suite that provides standardized interfaces for LLM, Embedding, Vector, and Graph operations. It enables backend-agnostic AI applications."
        elif "domains" in user_msg.lower():
            response = "The SDK supports four core domains: LLM (language models), Embedding (text vectorization), Vector (similarity search), and Graph (knowledge graphs)."
        elif "integrate" in user_msg.lower() or "backend" in user_msg.lower():
            response = "To integrate a backend, create an adapter class that inherits from the appropriate base (BaseLLMAdapter, BaseEmbeddingAdapter, etc.) and implement the _do_* hook methods like _do_complete, _do_embed, or _do_query."
        else:
            response = "I can provide information about Corpus SDK based on the available documentation."
            
        return LLMCompletion(
            text=response,
            model=model,
            model_family="gpt-4",
            usage=TokenUsage(
                prompt_tokens=len(user_msg.split()),
                completion_tokens=len(response.split()),
                total_tokens=len(user_msg.split()) + len(response.split())
            ),
            finish_reason="stop",
        )

    async def _do_count_tokens(self, text, *, model=None, ctx=None) -> int:
        return len(text.split())

    async def _do_health(self, *, ctx=None) -> dict:
        return {"ok": True, "server": "quick-llm"}


# 4. RAG Pipeline
class RAGPipeline:
    """Combines embedding, vector search, and LLM for RAG"""
    
    def __init__(self):
        self.embedder = QuickEmbeddingAdapter()
        self.vector_db = QuickVectorAdapter()
        self.llm = QuickLLMAdapter()
        self.ctx = OperationContext(request_id="rag-demo", tenant="quickstart")
    
    async def index_documents(self, documents: list[str]) -> int:
        """Index documents into the vector database"""
        vectors = []
        
        for i, doc in enumerate(documents):
            # Embed the document
            embed_result = await self.embedder.embed(
                EmbedSpec(text=doc, model="quick-embed-001"),
                ctx=self.ctx
            )
            
            # Create vector with metadata
            vectors.append(Vector(
                id=VectorID(f"doc-{i}"),
                vector=embed_result.embedding.vector,
                metadata={"text": doc, "doc_id": i}
            ))
        
        # Upsert to vector store
        result = await self.vector_db.upsert(
            UpsertSpec(vectors=vectors),
            ctx=self.ctx
        )
        
        return result.upserted_count
    
    async def query(self, question: str, top_k: int = 3) -> dict:
        """Answer a question using RAG"""
        
        # Step 1: Embed the question
        question_embed = await self.embedder.embed(
            EmbedSpec(text=question, model="quick-embed-001"),
            ctx=self.ctx
        )
        
        # Step 2: Search for relevant documents
        search_results = await self.vector_db.query(
            QuerySpec(vector=question_embed.embedding.vector, top_k=top_k),
            ctx=self.ctx
        )
        
        # Step 3: Build context from top matches
        context_docs = [
            match.vector.metadata["text"]
            for match in search_results.matches
        ]
        context = "\n\n".join(f"[{i+1}] {doc}" for i, doc in enumerate(context_docs))
        
        # Step 4: Generate answer with LLM
        prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {question}

Answer:"""
        
        completion = await self.llm.complete(
            messages=[{"role": "user", "content": prompt}],
            model="quick-llm-001",
            ctx=self.ctx
        )
        
        return {
            "answer": completion.text,
            "sources": context_docs,
            "relevance_scores": [m.score for m in search_results.matches],
            "tokens_used": completion.usage.total_tokens,
        }


# Usage Example
async def main():
    print("=" * 70)
    print("RAG Pipeline Demo - Corpus SDK")
    print("=" * 70)
    
    # Initialize pipeline
    rag = RAGPipeline()
    
    # Knowledge base documents
    documents = [
        "Corpus SDK is a protocol suite for building LLM applications with standardized interfaces.",
        "The SDK supports four core domains: LLM, Embedding, Vector, and Graph protocols.",
        "Adapters implement _do_* hooks (_do_complete, _do_embed, _do_query, etc.) to integrate any backend.",
        "All SDK examples are tested and production-ready, ensuring reliability.",
        "The protocol-based design enables swapping backends without changing application code.",
    ]
    
    # Index documents
    print("\n📚 Indexing documents...")
    count = await rag.index_documents(documents)
    print(f"✅ Indexed {count} documents\n")
    
    # Ask questions
    questions = [
        "What is Corpus SDK?",
        "How many domains does the SDK support?",
        "How do I integrate my backend?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'─' * 70}")
        print(f"Question {i}: {question}")
        print('─' * 70)
        
        result = await rag.query(question, top_k=2)
        
        print(f"\n💡 Answer:\n{result['answer']}\n")
        print(f"📊 Relevance Scores: {[f'{s:.3f}' for s in result['relevance_scores']]}")
        print(f"🔢 Tokens Used: {result['tokens_used']}")
        print(f"\n📎 Sources:")
        for j, source in enumerate(result['sources'], 1):
            print(f"  [{j}] {source}")
    
    print("\n" + "=" * 70)
    print("✅ RAG Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

```
</details>

Full implementations with batch operations, streaming, and multi-cloud scenarios are in [`docs/guides/ADAPTER_RECIPES.md`](docs/guides/ADAPTER_RECIPES.md).

---

## Core Concepts

- **Protocol vs Base** — Protocols define required behavior. Bases implement validation, deadlines, observability, and error normalization. You implement `_do_*` hooks.
- **OperationContext** — Carries `request_id`, `idempotency_key`, `deadline_ms`, `traceparent`, `tenant`, and cache hints across all operations.
- **Wire Protocol** — Canonical envelopes (`op`, `ctx`, `args`) and response shapes (`ok`, `code`, `result`) defined in [`docs/spec/PROTOCOL.md`](docs/spec/PROTOCOL.md).
- **Corpus OS-Compatible** — Implementations that honor the envelopes, reserved `op` strings, and error taxonomy. Validated by the conformance suite.

---

## Error Taxonomy & Observability

All domains share a **normalized error taxonomy**: `BadRequest`, `AuthError`, `ResourceExhausted`, `TransientNetwork`, `Unavailable`, `NotSupported`, `DeadlineExceeded`, plus domain-specific errors like `TextTooLong`, `ModelOverloaded`, `DimensionMismatch`, and `IndexNotReady`.

Errors carry **machine-actionable hints** (`retry_after_ms`, `throttle_scope`) so routers and control planes can react consistently across providers. A pluggable `MetricsSink` protocol lets you bring your own metrics backend. Bases emit one `observe` per operation, hash tenants before recording, and never log prompts, vectors, or raw tenant IDs.

Full details in [`docs/spec/ERRORS.md`](docs/spec/ERRORS.md) and [`docs/spec/METRICS.md`](docs/spec/METRICS.md).

---

## Performance & Configuration

Base overhead is typically **<10 ms** relative to vendor SDK calls: validation <1 ms, metrics <0.1 ms, cache lookup (standalone) <0.5 ms. Async-first design avoids blocking and supports high concurrency. Batch operations (`embed_batch`, vector upserts, graph batch) are preferred for throughput.

Benchmarks and deployment patterns in [`docs/guides/IMPLEMENTATION.md`](docs/guides/IMPLEMENTATION.md).

### Modes: `thin` vs `standalone`

Once you're ready for production, choose a mode:

| Mode | Infra Hooks | When to Use |
|---|---|---|
| **`thin`** (default) | All no-ops | You have an external control plane (router, scheduler, limiter) |
| **`standalone`** | Deadline enforcement, circuit breaker, token-bucket limiter, in-memory TTL cache | Lightweight deployments without external infra |

Use `thin` under a router to prevent double-stacking resiliency. Use `standalone` for prototyping or single-service deployments.

---

## Testing & Conformance

### One-Command Testing

```bash
# All protocols at once
make test-all-conformance

# Specific protocols
make test-llm-conformance
make test-vector-conformance
make test-graph-conformance
make test-embedding-conformance
```

### CLI

```bash
corpus-sdk verify                        # All protocols
corpus-sdk verify -p llm -p vector       # Selected protocols
corpus-sdk test-llm-conformance          # Single protocol
```

### Direct pytest

```bash
pytest tests/ -v --cov=corpus_sdk --cov-report=html
```

Requirements for "CORPUS-Compatible" certification are in [`docs/conformance/CERTIFICATION.md`](docs/conformance/CERTIFICATION.md).

---

## 📚 Documentation Layout

**Spec (normative):** [`docs/spec/`](docs/spec/)

| File | Contents |
|---|---|
| `SPECIFICATION.md` | Full protocol suite specification (all domains, cross-cutting behavior) |
| `PROTOCOL.md` | Wire-level envelopes, streaming semantics, canonical `op` registry |
| `ERRORS.md` | Canonical error taxonomy & mapping rules |
| `METRICS.md` | Metrics schema & SIEM-safe observability |
| `SCHEMA.md` | JSON/type shapes |
| `VERSIONING.md` | Semantic versioning & compatibility rules |

**Guides (how-to):** [`docs/guides/`](docs/guides/)

| File | Contents |
|---|---|
| `QUICK_START.md` | End-to-end flows for all four protocols |
| `IMPLEMENTATION.md` | How to implement adapters |
| `ADAPTER_RECIPES.md` | Real-world multi-cloud and RAG scenarios |
| `CONFORMANCE_GUIDE.md` | How to run & interpret conformance suites |

**Conformance (testing):** [`docs/conformance/`](docs/conformance/) — Per-protocol test specs, schema conformance, behavioral conformance, and certification requirements.

---

## FAQ

<details>
<summary><strong>Is the SDK open source?</strong></summary>

Yes. The SDK (protocols, bases, example adapters) is open source under Apache-2.0. CORPUS Router and official production adapters are commercial.
</details>

<details>
<summary><strong>Do I have to use CORPUS Router?</strong></summary>

No. The SDK composes with any router or control plane. CORPUS Router is optional and adheres to the same public protocols.
</details>

<details>
<summary><strong>How does CORPUS relate to LangChain / LlamaIndex / MCP / OpenRouter?</strong></summary>

They're complementary. LangChain/LlamaIndex are application frameworks. MCP standardizes tools and data sources. OpenRouter unifies LLM providers. CORPUS standardizes the infrastructure layer (LLM + Vector + Graph + Embedding) underneath all of them with consistent errors, metrics, and capabilities discovery.
</details>

<details>
<summary><strong>Why async-only?</strong></summary>

Modern AI workloads require high concurrency. Async-first prevents blocking the event loop. Sync wrappers can be built on top if needed.
</details>

<details>
<summary><strong>What happens if my adapter raises a non-normalized error?</strong></summary>

Bases catch unexpected exceptions and record them as `UnhandledException` in metrics. Wrap provider errors in normalized exceptions for proper handling.
</details>

<details>
<summary><strong>Can CORPUS Router run on-prem?</strong></summary>

Yes. Available as managed cloud or on-prem deployment for regulated and air-gapped environments.
</details>

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Double-stacked resiliency (timeouts firing twice) | Ensure `mode="thin"` under your router |
| Circuit breaker opens frequently | Reduce concurrency or switch to `thin` with external circuit breaker |
| Cache returns stale results | Verify sampling params in cache key; check `cache_ttl_s` |
| `DeadlineExceeded` on fast operations | Ensure `deadline_ms` is absolute epoch time, not relative. Check NTP sync. |
| Health check failures | Inspect `_do_health` implementation; verify backend reachability and credentials |

```python
# Debug mode
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("corpus_sdk").setLevel(logging.DEBUG)
```

---

## Contributing

```bash
git clone https://github.com/Corpus-OS/corpusos.git
cd corpus-sdk
pip install -e ".[dev]"
pytest
```

Follow PEP-8 (ruff/black). Type hints required on all public APIs. Include tests for new features. Maintain low-cardinality metrics — never add PII to `extra` fields. Observe SemVer.

We especially welcome **community adapter contributions** for new LLM, vector, graph, and embedding backends.

Community questions: [GitHub Discussions](https://github.com/corpus/corpus-sdk/discussions) preferred.

---

## License & Commercial Options

**License:** Apache-2.0 ([`LICENSE`](LICENSE))

| Need | Solution | Cost |
|---|---|---|
| Learning / prototyping | `corpus_sdk` + example adapters | **Free (OSS)** |
| Production with your own infra | `corpus_sdk` + your adapters | **Free (OSS)** |
| Production with official adapters | `corpus_sdk` + Official Adapters | **Commercial** |
| Enterprise multi-provider | `corpus_sdk` + CORPUS Router (Managed or On-Prem) | **Commercial** |

---
**Contact:** [team@corpusos.com](mailto:team@corpusos.com) 
**Website:** [https://corpusos.com](https://corpusos.com) 
**Docs:** [https://docs.corpusos.com](https://docs.corpusos.com) 

---

**Built by the Corpus OS team** — wire-level AI infrastructure you integrate once and connect anywhere.
