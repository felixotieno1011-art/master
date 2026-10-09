from collections import deque

history = deque()

while True:
    print("\n--- Menu ---")
    print("1. Add message")
    print("2. Undo")
    print("3. Show history")
    print("4. Exit")
    
    choice = input("Choose (1-4): ")

    if choice == "1":
        msg = input("Enter message: ")
        history.append(msg)
        print(f"✅ Added: '{msg}'")

    elif choice == "2":
        if not history:
            print("⚠️ History is empty, nothing to undo.")
        else:
            removed = history.pop()
            print(f"↩️ Undone: '{removed}' was removed.")

    elif choice == "3":
        if not history:
            print("📭 History is empty.")
        else:
            print(f"📜 History: {list(history)}")

    elif choice == "4":
        print(f"👋 Exiting. Final history had {len(history)} items.")
        break

    else:
        print(f"❌ Invalid choice: '{choice}'")
