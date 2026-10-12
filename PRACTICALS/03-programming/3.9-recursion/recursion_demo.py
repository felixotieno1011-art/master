# ============================================
# Recursion Demo
# ============================================

print("=" * 50)
print("1. COUNTDOWN (simple recursion)")
print("=" * 50)

def countdown(n):
    print(f"   countdown({n}) called")
    if n == 0:
        print(f"   ✅ Base case! Stop here.")
        return
    countdown(n - 1)
    print(f"   ← Returning from countdown({n})")

countdown(3)

print()
print("=" * 50)
print("2. FACTORIAL (recursion with return)")
print("=" * 50)

def factorial(n):
    print(f"   factorial({n})")
    if n <= 1:
        return 1
    result = n * factorial(n - 1)
    print(f"   factorial({n}) = {n} * factorial({n-1}) = {result}")
    return result

print(f"\nfactorial(5) = {factorial(5)}")

print()
print("=" * 50)
print("3. FIND NESTED FILE (real-world recursion)")
print("=" * 50)

def find_file(folder, target):
    """Recursively search a nested structure (like POS product categories)."""
    for item in folder:
        if item["type"] == "file" and item["name"] == target:
            print(f"   ✅ Found '{target}' at {item['path']}")
            return True
        elif item["type"] == "folder":
            print(f"   📁 Entering '{item['name']}'")
            if find_file(item["children"], target):
                return True
    return False

# Simulated POS product categories
categories = [
    {"type": "file", "name": "README.md", "path": "/"},
    {"type": "folder", "name": "electronics", "children": [
        {"type": "file", "name": "phones.json", "path": "/electronics"},
        {"type": "folder", "name": "accessories", "children": [
            {"type": "file", "name": "chargers.json", "path": "/electronics/accessories"},
            {"type": "file", "name": "cases.json", "path": "/electronics/accessories"},
        ]}
    ]},
    {"type": "folder", "name": "food", "children": [
        {"type": "file", "name": "snacks.json", "path": "/food"},
    ]}
]

print("\nSearching for chargers.json...")
find_file(categories, "chargers.json")
