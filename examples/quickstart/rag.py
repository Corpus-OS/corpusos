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
