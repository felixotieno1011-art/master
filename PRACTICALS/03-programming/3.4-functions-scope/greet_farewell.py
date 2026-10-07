def greet(name):
    print(f"Hello {name}! Welcome")

def farewell(name):
    print(f"Goodbye {name}! See you soon")

name = input("What is your name? ")
choice = input("Greet or Farewell? (g/f): ")

if choice == "g":
    greet(name)
elif choice == "f":
    farewell(name)
else:
    print("Invalid choice")
