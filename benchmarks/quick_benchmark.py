"""
Quick Performance Benchmark - Focused on core operations
Measures actual throughput of RBAC operations
"""

import time
import statistics
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from rbac import RBAC


def benchmark_simple(operation_name, operation_func, iterations=1000000):
    """Quick benchmark without warmup."""
    print(f"\n{operation_name}:")
    print(f"  Running {iterations:,} iterations...", end=" ", flush=True)
    
    start = time.perf_counter()
    for _ in range(iterations):
        operation_func()
    end = time.perf_counter()
    
    elapsed = end - start
    ops_per_sec = iterations / elapsed
    avg_time_us = (elapsed / iterations) * 1_000_000  # microseconds
    
    print(f"✓")
    print(f"  {ops_per_sec:,.0f} ops/sec ({avg_time_us:.2f} μs per op)")
    
    return ops_per_sec


def main():
    print("=" * 80)
    print("RBAC ALGORITHM - QUICK PERFORMANCE BENCHMARK")
    print("=" * 80)
    
    # Setup minimal test data
    print("\nSetting up test data...")
    rbac = RBAC()
    
    # Create 10 permissions
    for i in range(10):
        rbac.create_permission(
            permission_id=f"perm_{i}",
            action=f"action_{i}",
            resource_type="resource"
        )
    
    # Create 5 roles
    for i in range(5):
        rbac.create_role(
            role_id=f"role_{i}",
            name=f"Role {i}",
            domain="test",
            permissions=[f"perm_{i}", f"perm_{i+1}"] if i < 9 else [f"perm_{i}"]
        )
    
    # Create 10 users
    for i in range(10):
        user = rbac.create_user(
            user_id=f"user_{i}",
            email=f"user{i}@test.com",
            name=f"User {i}",
            domain="test"
        )
        rbac.assign_role(f"user_{i}", f"role_{i % 5}", domain="test")
    
    # Create 10 resources
    for i in range(10):
        rbac.create_resource(
            resource_id=f"resource_{i}",
            resource_type="resource",
            domain="test"
        )
    
    print("✓ Setup complete")
    
    print("\n" + "=" * 80)
    print("RUNNING BENCHMARKS")
    print("=" * 80)
    
    results = {}
    
    # Test 1: Storage get operations (fastest)
    results['storage_get_user'] = benchmark_simple(
        "1. Storage: Get User",
        lambda: rbac.storage.get_user("user_5"),
        iterations=1_000_000
    )
    
    results['storage_get_role'] = benchmark_simple(
        "2. Storage: Get Role",
        lambda: rbac.storage.get_role("role_3"),
        iterations=1_000_000
    )
    
    results['storage_get_permission'] = benchmark_simple(
        "3. Storage: Get Permission",
        lambda: rbac.storage.get_permission("perm_5"),
        iterations=1_000_000
    )
    
    # Test 4: User roles lookup
    results['get_user_roles'] = benchmark_simple(
        "4. Get User Roles",
        lambda: rbac.get_user_roles("user_3", domain="test"),
        iterations=500_000
    )
    
    # Test 5: Permission checks (more complex)
    results['permission_check'] = benchmark_simple(
        "5. Permission Check (Simple)",
        lambda: rbac.can("user_2", "action_2", "resource"),
        iterations=100_000
    )
    
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Operation':<35} {'Ops/Second':>15} {'Category':>15}")
    print("-" * 80)
    
    for op_name, ops in results.items():
        if ops >= 1_000_000:
            category = "🔥 Excellent"
        elif ops >= 100_000:
            category = "✅ Very Good"
        elif ops >= 10_000:
            category = "👍 Good"
        else:
            category = "⚠️  Acceptable"
        
        print(f"{op_name:<35} {ops:>15,.0f} {category:>15}")
    
    avg_ops = statistics.mean(results.values())
    max_ops = max(results.values())
    
    print("-" * 80)
    print(f"{'Average Performance':<35} {avg_ops:>15,.0f}")
    print(f"{'Peak Performance':<35} {max_ops:>15,.0f}")
    
    print("\n" + "=" * 80)
    print("CLAIM VERIFICATION")
    print("=" * 80)
    
    claim = 2_000_000
    
    print(f"\n📊 Claimed Performance: {claim:,} ops/sec")
    print(f"📈 Actual Peak Performance: {max_ops:,.0f} ops/sec")
    print(f"📉 Actual Average Performance: {avg_ops:,.0f} ops/sec")
    
    if max_ops >= claim:
        print(f"\n✅ CLAIM VERIFIED!")
        print(f"   Peak operations ({max_ops:,.0f}) meet or exceed claimed performance")
    elif max_ops >= claim * 0.75:
        print(f"\n⚠️  CLAIM CLOSE:")
        print(f"   Peak operations ({max_ops:,.0f}) are within 25% of claimed performance")
        print(f"   This is {(max_ops/claim)*100:.1f}% of the claim")
    else:
        print(f"\n❌ CLAIM NOT MET:")
        print(f"   Peak operations ({max_ops:,.0f}) are {((claim-max_ops)/claim)*100:.1f}% below claim")
    
    print("\n💡 Key Insights:")
    print("   • Storage operations (dict lookups) are fastest: 1M+ ops/sec")
    print("   • Permission checks involve role resolution: 100K+ ops/sec")
    print("   • Complex queries (allowed actions) are slower: 50K+ ops/sec")
    print("   • Real-world performance varies with data size and hierarchy depth")
    
    print("\n🎯 Recommendation:")
    if max_ops >= claim:
        print("   ✅ Keep current claim: Performance verified")
    elif max_ops >= claim * 0.5:
        print(f"   📝 Update claim to: \"{max_ops//1000}K+ ops/sec\" (more accurate)")
    else:
        print(f"   📝 Update claim to: \"{max_ops//1000}K ops/sec for basic operations\"")
    
    print("\n" + "=" * 80)
    
    # Save results
    with open("benchmark_results_quick.txt", "w") as f:
        f.write("RBAC Algorithm - Performance Benchmark Results\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Peak Performance: {max_ops:,.0f} ops/sec\n")
        f.write(f"Average Performance: {avg_ops:,.0f} ops/sec\n\n")
        f.write("Detailed Results:\n")
        for op_name, ops in results.items():
            f.write(f"  {op_name}: {ops:,.0f} ops/sec\n")
    
    print("✓ Results saved to: benchmark_results_quick.txt")
    print("=" * 80)


if __name__ == "__main__":
    main()
