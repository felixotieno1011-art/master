def recursive_sum(n):
    if n == 0:
        return 0
    return n + recursive_sum(n - 1)

print(f"recursive_sum(5) = {recursive_sum(5)}")
print(f"recursive_sum(10) = {recursive_sum(10)}")
