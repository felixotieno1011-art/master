# SEARCH ALGORITHMS PRACTICE

# 1. Sorted list of 10 numbers
numbers = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]


# 2. Linear search
def linear_search(items, target):
    for i in range(len(items)):
        if items[i] == target:
            return i
    return -1


# 3. Binary search (list must be sorted)
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


# 4. Test both
print("Looking for 23...")
result1 = linear_search(numbers, 23)
result2 = binary_search(numbers, 23)

if result1 != -1:
    print("Linear found at index", result1)
else:
    print("Linear: not found")

if result2 != -1:
    print("Binary found at index", result2)
else:
    print("Binary: not found")

print()

print("Looking for 100...")
result3 = linear_search(numbers, 100)
result4 = binary_search(numbers, 100)

if result3 != -1:
    print("Linear found at index", result3)
else:
    print("Linear: not found")

if result4 != -1:
    print("Binary found at index", result4)
else:
    print("Binary: not found")
