# ============================================
# Safe Calculator — Demonstrates try/except
# ============================================

print("🧮 SAFE CALCULATOR")
print("=" * 40)

while True:
    print("\nChoose operation:")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Exit")

    choice = input("\nYour choice (1-5): ").strip()

    if choice == "5":
        print("👋 Goodbye!")
        break

    if choice not in ["1", "2", "3", "4"]:
        print("❌ Invalid choice. Try again.")
        continue

    # ---- Get numbers (with error handling) ----
    try:
        a = float(input("First number: "))
        b = float(input("Second number: "))
    except ValueError:
        print("❌ Invalid input! Please enter numbers only.")
        continue

    # ---- Do the operation ----
    try:
        if choice == "1":
            result = a + b
            op = "+"
        elif choice == "2":
            result = a - b
            op = "-"
        elif choice == "3":
            result = a * b
            op = "*"
        elif choice == "4":
            result = a / b       # might divide by zero
            op = "/"

        print(f"\n✅ {a} {op} {b} = {result}")

    except ZeroDivisionError:
        print("\n❌ Cannot divide by zero!")
