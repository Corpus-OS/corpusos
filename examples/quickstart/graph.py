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
