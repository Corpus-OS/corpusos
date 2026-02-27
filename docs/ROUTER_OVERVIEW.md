# Corpus Router: The Intelligent Control Plane for AI Infrastructure

*Commercial Product Document • Last Updated: 2025*

> **Stop wasting 40% of your AI budget on the wrong providers.**  
> Corpus Router learns which providers work best for your specific workloads—across LLMs, vectors, graphs, and embeddings—reducing costs while eliminating vendor lock-in.

## 📋 Table of Contents
- [What Corpus Router Solves](#what-corpus-router-solves)
- [The Protocol-First Difference](#the-protocol-first-difference)
- [Technical Architecture](#technical-architecture)
- [Key Capabilities](#key-capabilities)
- [Enterprise Features](#enterprise-features)
- [Getting Started](#getting-started)

## 🎯 TL;DR for Executives
- **What:** Intelligent routing layer for AI infrastructure (LLM, vector, graph, embedding)
- **Why:** Cuts costs, eliminates framework/vendor lock-in, automates compliance
- **How:** Universal protocol + self-learning routing + enterprise policy engine
- **For:** Teams spending >$10K/month on AI infrastructure with multiple providers
- **Migration:** Wrap existing code, don't rewrite. Gradual rollout over 8-12 weeks.

---

## 🔥 What Corpus Router Solves

### The Infrastructure Crisis at Scale
Every AI team hits the same wall:

**1. Framework Prison**
Your 50,000 lines of LangChain code can't talk to LlamaIndex. Your Semantic Kernel skills don't work in CrewAI. Every framework change means a rewrite.

**2. Provider Chaos**
OpenAI errors ≠ Anthropic errors ≠ Cohere errors. Each needs custom handling, retry logic, rate limiting, and monitoring.

**3. Cost Blindness**  
No unified view of spending across providers. Manual optimization can't keep up with weekly price changes and new model releases.

**4. Compliance Risk**
Manual processes for data residency (HIPAA, GDPR) that fail at scale. Audit trails scattered across 6+ systems.

**5. Operational Tax**
2-3 engineers full-time managing integrations instead of building features. Months to add new providers.

### Why Now? The 2025 Inflection Point

| 2023 | 2024 | **2025** |
|------|------|----------|
| 1-2 LLM providers | 4-5 options | **10+ specialized providers** |
| Simple RAG | Basic vector search | **Multi-modal with graphs** |
| One framework | Framework wars begin | **6+ frameworks, no clear winner** |
| Manual cost mgmt | Spreadsheets | **Real-time optimization required** |
| Basic compliance | Regional requirements | **Industry-specific compliance frameworks** |

**Manual management no longer works.** The market changes weekly; human-scale decision-making can't keep up.

---

## 🔄 The Protocol-First Difference

Every other solution starts wrong:

| Solution | Their Pitch | Reality |
|----------|-------------|---------|
| **Framework-First**<br>(LangChain, LlamaIndex) | "Build in our framework" | **Framework lock-in** |
| **Provider-First**<br>(OpenRouter, etc.) | "Use our service for these vendors" | **Service dependency** |
| **Gateway-First**<br>(Generic API gateways) | "We'll proxy your HTTP calls" | **No semantic understanding** |
| **🔄 Corpus Router** | "Universal wire format" | **True interoperability** |

Corpus defines the **TCP/IP layer for AI infrastructure**. Not another framework, not another service—the protocol everything speaks.

---

## 🏗️ Technical Architecture

### The Protocol-Native Control Plane

Corpus Router doesn't invent new APIs. It routes **Corpus Protocol** traffic—the same protocol defined in `corpus_sdk/llm/llm_base.py`:

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Applications                        │
│  (Any framework, any language, any deployment)             │
│                                                             │
│  • LangChain chains & agents                               │
│  • LlamaIndex query engines                                │
│  • Semantic Kernel planners                                │
│  • CrewAI multi-agent teams                                │
│  • AutoGen conversational flows                            │
│  • MCP tool servers                                        │
│  • Custom microservices                                    │
│  • Legacy systems                                          │
└──────────────────────────────┬──────────────────────────────┘
                                │
                                │ Corpus Protocol (Wire Format)
                                │ • Same envelopes as corpus_sdk
                                │ • Same error taxonomy  
                                │ • Same OperationContext
                                │
                                ▼
                 ┌─────────────────────────────────────┐
                 │         Corpus Router               │
                 │                                     │
                 │  • Multi-provider routing           │
                 │  • Self-learning optimization       │
                 │  • Policy enforcement               │
                 │  • Unified observability            │
                 │  • Multi-tenant isolation           │
                 └─────────────────────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
┌──────────────┐             ┌────────────────┐             ┌──────────────┐
│  LLM Providers│             │  Vector & Graph│             │  Your Existing│
│               │             │    Databases   │             │    Code      │
│ • OpenAI     │             │ • Pinecone     │             │ • LangChain  │
│ • Anthropic  │             │ • Weaviate     │             │   chains     │
│ • Cohere     │             │ • Qdrant       │             │ • LlamaIndex │
│ • Mistral AI │             │ • Neo4j        │             │   indexes    │
│ • Google     │             │ • TigerGraph   │             │ • Custom RAG │
│ • Azure      │             │ • Chroma       │             │   pipelines  │
│ • AWS Bedrock│             │ • ...          │             │ • ...        │
└──────────────┘             └────────────────┘             └──────────────┘
```

### Built on Real Code: The `corpus_sdk` Foundation

Corpus Router is built directly on the codebase. Here's how it actually works:

**1. Same Protocol Envelopes**
```python
# From corpus_sdk/llm/llm_base.py - this is the actual wire format
{
    "op": "llm.complete",                    # Operation from the protocol
    "ctx": {                                 # OperationContext dataclass
        "request_id": "...",
        "deadline_ms": 1234567890,           # Absolute epoch ms
        "tenant": "...",                     # Never logged raw
        "attrs": {"region": "eu", "priority": "high"}
    },
    "args": {                                # Operation-specific
        "messages": [...],
        "model": "gpt-4",
        "temperature": 0.7
    }
}

# Response follows the same structure:
{
    "ok": True,
    "code": "OK",                           # From the normalized error taxonomy
    "ms": 1245.3,
    "result": {                             # LLMCompletion dataclass
        "text": "...",
        "model": "gpt-4-0613",
        "model_family": "gpt-4",
        "usage": {
            "prompt_tokens": 15,
            "completion_tokens": 125,
            "total_tokens": 140
        },
        "finish_reason": "stop",
        "tool_calls": []
    }
}
```

**2. Same Error Taxonomy**
```python
# From corpus_sdk/llm/llm_base.py - actual exception hierarchy
LLMAdapterError
├── BadRequest           # Invalid parameters
├── AuthError            # Authentication failures
├── ResourceExhausted    # Rate limits, quotas
├── TransientNetwork     # Retryable network issues
├── Unavailable          # Backend unavailable
├── NotSupported         # Unsupported operations
├── ModelOverloaded      # Specific model overloaded
└── DeadlineExceeded     # Operation timeout
```

**3. Same Adapter Pattern**
```python
# Router extends the same BaseLLMAdapter pattern
class RouterLLMAdapter(BaseLLMAdapter):
    """Router's intelligent routing adapter"""
    
    def __init__(self, providers: List[BaseLLMAdapter], policies: PolicyEngine):
        super().__init__(mode="thin")  # Router handles policies globally
        self.providers = providers
        self.policies = policies
        self.learning_engine = SelfLearningEngine()
    
    async def _do_complete(self, *, messages, ctx=None, **kwargs):
        # Apply policies using the same OperationContext
        if not self.policies.allow(ctx, "llm.complete", kwargs):
            raise ResourceExhausted("Policy violation")
        
        # Select best provider
        provider = await self.learning_engine.select_provider(
            op="llm.complete",
            ctx=ctx,
            args=kwargs,
            candidates=self.providers
        )
        
        # Execute with chosen provider
        return await provider.complete(messages=messages, ctx=ctx, **kwargs)
```

---

## 🎯 Key Capabilities

### 1. Self-Learning Routing

**Privacy-first learning from metadata only:**
```python
# From corpus_sdk/llm/llm_base.py - no PII in metrics
@staticmethod
def _tenant_hash(t: Optional[str]) -> Optional[str]:
    """Hash tenant for metrics/logging. Raw tenant identifiers NEVER emitted."""
    if not t:
        return None
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:12]

@staticmethod  
def _messages_fingerprint(messages: List[Mapping[str, str]]) -> str:
    """Stable fingerprint without leaking content."""
    h = hashlib.sha256()
    for m in messages:
        h.update(str(m.get("role", "")).encode("utf-8"))
        h.update(b"\x1f")
        h.update(str(m.get("content", "")).encode("utf-8"))
        h.update(b"\x1e")
    return h.hexdigest()
```

**Optimizes across dimensions:**
- **Cost vs. quality:** GPT-4 for customers, Claude Haiku for internal
- **Provider selection:** Which vector DB for real-time vs. batch
- **Regional routing:** EU data → EU providers
- **Model matching:** Which LLM works best for this prompt type

### 2. Multi-Domain Unification

Unlike solutions that only handle LLM routing, Corpus manages **all four AI infrastructure domains**:

| Domain | Base Adapter Class | Key Operations | Example Providers |
|--------|-------------------|----------------|-------------------|
| **LLM** | `BaseLLMAdapter` | `complete`, `stream`, `count_tokens` | OpenAI, Anthropic, Cohere |
| **Vector** | `BaseVectorAdapter` | `query`, `upsert`, `delete` | Pinecone, Weaviate, Qdrant |
| **Graph** | `BaseGraphAdapter` | `query`, `upsert_nodes`, `traverse` | Neo4j, TigerGraph, Neptune |
| **Embedding** | `BaseEmbeddingAdapter` | `embed`, `embed_batch` | OpenAI, Cohere, sentence-transformers |

### 3. Enterprise Policy Engine

**Define once, enforce everywhere:**
```python
class PolicyEngine:
    def allow(self, ctx: OperationContext, op: str, args: dict) -> bool:
        # Check budgets (tenant is always hashed in metrics)
        if self._budget_exceeded(ctx.tenant):
            return False
        
        # Check compliance using attrs
        if ctx.attrs.get("region") == "eu":
            return self._is_eu_compliant(op, args)
        
        # Check rate limits
        return self._rate_limit_allows(ctx.tenant, op)

# Router applies these before any provider calls
async def route_request(self, envelope):
    ctx = _ctx_from_wire(envelope["ctx"])  # Same helper from llm_base.py
    if not self.policies.allow(ctx, envelope["op"], envelope["args"]):
        raise ResourceExhausted(
            "Policy violation", 
            details={"policy": "budget_exceeded"}
        )
    # Continue with routing...
```

**Policy dimensions:**
- **Budgets:** Per-tenant, per-project, per-domain spending limits
- **Compliance:** Data residency, certified providers, regulatory requirements  
- **Performance:** Latency SLAs, success rate requirements
- **Security:** Allowed/denied providers, encryption requirements
- **Cost Optimization:** Maximum cost per operation, quality thresholds

### 4. Unified Observability

**One dashboard for everything:**
```
┌─────────────────────────────────────────────────────┐
│               Corpus Router Dashboard               │
├─────────────────────────────────────────────────────┤
│  • Total Cost: $42,847.32 (month-to-date)          │
│  • P95 Latency: LLM: 1.2s, Vector: 45ms, Graph: 320ms │
│  • Error Rate: 0.7% (goal: <1%)                    │
│  • Top Cost Drivers:                                │
│      - tenant_alpha: $18,492.10 (43%)              │
│      - tenant_beta: $12,394.85 (29%)               │
│      - tenant_gamma: $11,960.37 (28%)              │
│  • Provider Distribution:                           │
│      - OpenAI: 42% of traffic                      │
│      - Anthropic: 28%                              │
│      - Cohere: 15%                                 │
│      - Pinecone: 10%                               │
│      - Neo4j: 5%                                   │
└─────────────────────────────────────────────────────┘
```

---

## 🏢 Enterprise Features

### Multi-Tenant Architecture

**Complete isolation using the SDK's context system:**
- Each tenant gets their own routing decisions (learned from their traffic only)
- Per-tenant policy enforcement using `OperationContext.tenant`
- Isolated cost tracking and budgets
- Separate performance SLAs
- Unique compliance requirements per tenant

**Enterprise security built on SDK foundations:**
- SSO integration (Okta, Azure AD, Google)
- RBAC with fine-grained permissions
- Audit trails for all operations using `request_id` from context
- Integration with existing SIEM systems
- Secret management (Hashicorp Vault, AWS Secrets Manager)

### Deployment Options

| | Managed Service | On-Premises | Hybrid |
|---|---|---|---|
| **Infrastructure** | Corpus-managed | Your infrastructure | Mixed |
| **Data Residency** | Multi-region | Your control | Your control |
| **Compliance** | SOC 2, ISO 27001 | Your certifications | Your certifications |
| **SLA** | 99.95% | Your SLA | Mixed |
| **Support** | 24/7 with SLAs | Optional professional services | Optional professional services |

---

## 🚀 Getting Started

### With Existing AI Infrastructure

**Phase 1: Instrumentation (Week 1)**
```bash
pip install corpus_sdk
# Your existing code continues working
```

**Phase 2: Wrap Critical Workflows (Week 2-3)**
```python
from corpus_sdk.llm.llm_base import BaseLLMAdapter, LLMCapabilities, LLMCompletion

class ExistingChainAdapter(BaseLLMAdapter):
    def __init__(self, chain):
        super().__init__(mode="thin")
        self.chain = chain  # No changes to your code
    
    async def _do_complete(self, *, messages, ctx=None, **kwargs):
        result = await self.chain.arun(self._to_prompt(messages))
        return LLMCompletion(
            text=result,
            model="existing-chain",
            model_family="existing",
            usage=TokenUsage(0, 0, 0),
            finish_reason="stop"
        )

# Register with Router
router.add_adapter("production-chain", ExistingChainAdapter(your_chain))
```

**Phase 3: Parallel Run (Month 1)**
- 10% traffic → Router
- Compare with existing system
- Gradually increase Router traffic

**Phase 4: Full Migration (Month 2)**
- 100% traffic → Router
- Existing system as fallback
- Start adding new providers

**Phase 5: Optimization (Month 3+)**
- Enable self-learning routing
- Add cost optimization policies
- Implement advanced features

### Greenfield Projects
Start with Corpus Protocol from day one. Build adapters using the actual base classes from `corpus_sdk`.

---

## 🤝 Next Steps

**Try the SDK:** `pip install corpus_sdk`

**Contact:**
- **Website:** [https://corpusos.com](https://corpusos.com)
- **Documentation:** [https://docs.corpusos.com/router](https://docs.corpusos.com/router)
- **GitHub:** [https://github.com/corpus-io](https://github.com/corpus-io)
- **Sales:** sales@corpusos.com
- **Support:** support@corpusos.com

---

*Corpus Router v1.0 • [https://corpusos.com](https://corpusos.com) • © 2024 Corpus Technologies*
