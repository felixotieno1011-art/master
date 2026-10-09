# ============================================
# Search Race — Linear vs Binary Search
# Demonstrates how algorithms scale
# ============================================

import time

# ---- Linear Search — O(n) ----
def linear_search(items, target):
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1

# ---- Binary Search — O(log n) ----
def binary_search(items, target):
    low = 0
    high = len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

# ---- Test with different sizes ----
def test_size(n):
    data = list(range(n))       # [0, 1, 2, ..., n-1]
    target = n - 1              # last item (worst case)

    print(f"\n📊 Testing with {n:,} items")

    # Linear
    start = time.time()
    result1 = linear_search(data, target)
    linear_time = time.time() - start

    # Binary
    start = time.time()
    result2 = binary_search(data, target)
    binary_time = time.time() - start

    print(f"   Linear Search (O(n)):    {linear_time:.6f} sec")
    print(f"   Binary Search (O(log n)): {binary_time:.6f} sec")

    if binary_time > 0:
        speedup = linear_time / binary_time
        print(f"   ⚡ Binary was {speedup:.0f}x faster!")

# ---- Run the race ----
print("🏁 SEARCH ALGORITHM RACE")
print("=" * 50)

for size in [1000, 10000, 100000, 1000000]:
    test_size(size)

print("\n" + "=" * 50)
print("💡 Notice: as size grows, linear search grows")
print("   directly, but binary search barely grows at all.")
