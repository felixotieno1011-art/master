# ============================================
# Mini ATM — demonstrates functions and scope
# ============================================

# Global variable
balance = 1000

# ---- Function 1 ----
def show_menu():
    print("\n===== ATM MENU =====")
    print("1. Check Balance")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Exit")
    print("====================\n")

# ---- Function 2 ----
def check_balance():
    print(f"\n💰 Your balance is: KES {balance}")
    return balance

# ---- Function 3 ----
def deposit(amount):
    global balance              # we WANT to change the global balance
    balance = balance + amount
    print(f"\n✅ Deposited KES {amount}")
    print(f"   New balance: KES {balance}")

# ---- Function 4 ----
def withdraw(amount):
    global balance
    if amount > balance:
        print(f"\n❌ Insufficient funds! Balance is KES {balance}")
        return False
    balance = balance - amount
    print(f"\n✅ Withdrew KES {amount}")
    print(f"   New balance: KES {balance}")
    return True

# ---- Main Program ----
print("🏧 Welcome to Mini ATM")

while True:
    show_menu()
    choice = input("Choose (1-4): ").strip()

    if choice == "1":
        check_balance()
    elif choice == "2":
        amount = int(input("Amount to deposit: "))
        deposit(amount)
    elif choice == "3":
        amount = int(input("Amount to withdraw: "))
        withdraw(amount)
    elif choice == "4":
        print("\n👋 Goodbye!")
        break
    else:
        print("\n❌ Invalid choice. Try again.")
