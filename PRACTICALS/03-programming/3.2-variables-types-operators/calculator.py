# ============================================
# Mini Calculator — demonstrates types & operators
# ============================================

print("🧮 MINI CALCULATOR")
print("=" * 40)

# ---- Get input ----
a = input("Enter first number: ")
b = input("Enter second number: ")

# ---- Convert to floats ----
a = float(a)
b = float(b)

# ---- Show the types ----
print(f"\nType of a: {type(a)}")
print(f"Type of b: {type(b)}")

# ---- Show all operations ----
print("\n📊 RESULTS")
print("=" * 40)

print(f"{a} + {b}  = {a + b}")
print(f"{a} - {b}  = {a - b}")
print(f"{a} * {b}  = {a * b}")
print(f"{a} / {b}  = {a / b}")
print(f"{a} // {b} = {a // b}  (floor divide)")
print(f"{a} % {b}  = {a % b}  (remainder)")
print(f"{a} ** {b} = {a ** b}  (power)")

# ---- Comparison ----
print("\n🔍 COMPARISONS")
print(f"a == b? {a == b}")
print(f"a > b?  {a > b}")
print(f"a < b?  {a < b}")

# ---- Logical ----
print("\n🧠 LOGICAL")
print(f"Both positive? {(a > 0) and (b > 0)}")
print(f"Either zero?   {(a == 0) or (b == 0)}")
print(f"Not equal?     {not (a == b)}")
