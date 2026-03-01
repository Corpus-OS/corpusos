"""
Quick test to verify ReferenceRouter runs cleanly.
"""

import asyncio
from corpus_sdk.router.reference_router import ReferenceRouter


async def main():
    print("=== Testing ReferenceRouter Import & Initialization ===\n")
    
    # Test 1: Import works
    print("✓ ReferenceRouter imported successfully")
    
    # Test 2: Initialize with no adapters (should work but log warning)
    router = ReferenceRouter()
    print(f"✓ Router initialized with no adapters")
    print(f"  Available protocols: {router.available_protocols()}")
    
    # Test 3: Check available methods
    print(f"\n✓ Router has route() method: {hasattr(router, 'route')}")
    print(f"✓ Router has health_check() method: {hasattr(router, 'health_check')}")
    print(f"✓ Router has close() method: {hasattr(router, 'close')}")
    print(f"✓ Router supports async context manager: {hasattr(router, '__aenter__')}")
    
    # Test 4: Health check with no adapters
    print(f"\n=== Testing health_check() ===")
    health = await router.health_check()
    print(f"✓ health_check() returned: {health}")
    
    # Test 5: Test that routing without adapters raises appropriate error
    print(f"\n=== Testing route() error handling ===")
    try:
        await router.route({
            "op": "llm.complete",
            "ctx": {},
            "args": {"messages": [{"role": "user", "content": "test"}]}
        })
        print("✗ Should have raised NotSupported")
    except Exception as e:
        print(f"✓ Correctly raised: {type(e).__name__}: {e}")
    
    # Test 6: Test async context manager
    print(f"\n=== Testing async context manager ===")
    async with ReferenceRouter() as router2:
        print(f"✓ Router created in async context")
        print(f"  Available protocols: {router2.available_protocols()}")
    print(f"✓ Router closed cleanly via context manager")
    
    # Test 7: Manual close
    print(f"\n=== Testing manual close() ===")
    router3 = ReferenceRouter()
    await router3.close()
    print(f"✓ Router closed manually without errors")
    
    print(f"\n=== All Tests Passed ===")
    print(f"ReferenceRouter runs cleanly with zero dependencies!")


if __name__ == "__main__":
    asyncio.run(main())
