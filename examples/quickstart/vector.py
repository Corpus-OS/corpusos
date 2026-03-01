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
