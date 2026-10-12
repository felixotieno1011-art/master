# 1. Go through the list, compare each pair side by side
# 2. If left > right → swap them
# 3. Repeat until no more swaps
# 4. Return sorted list
def bubble_sort(numbers):
    n = len(numbers)
    for i in range(n):
        for j in range(n - 1):
            if numbers[j] > numbers[j + 1]:
                numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
    return numbers

print(bubble_sort([300, 120, 480, 90, 250]))
