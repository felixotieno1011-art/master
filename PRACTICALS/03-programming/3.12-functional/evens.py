from functools import reduce

numbers = [3, 8, 1, 9, 4]       # ← list FIRST

doubled = list(map(lambda n: n * 2, numbers))
print("doubled:", doubled)

total = reduce(lambda a, b: a + b, numbers)
print("sum:", total)

def double(n):                   # ← function defined
    return n + 2

doubled2 = list(map(double, numbers))   # ← then used
print("with def:", doubled2)
