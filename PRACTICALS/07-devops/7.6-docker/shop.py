# SPEC — Console Shop Inventory (Part 3 Project)
# 1. Product class: name, price, quantity
# 2. List holds all products
# 3. add_product() — create + append
# 4. show_all() — print every product
# 5. search_product() — find by name (partial match)
# 6. Menu loop until Quit

class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def show(self):

        print(f"{self.name}: {self.price} KES x{self.quantity}")
products = []
def add_product():
    name = input("Product name? ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    try:
        price = float(input("Price? "))
        quantity = int(input("Quantity? "))
    except ValueError:
        print("Invalid number. Product not added.")
        return
    p = Product(name, price, quantity)
    products.append(p)
    print("Product added!")

def show_all():
    if not products:
        print("No products yet.")
        return
    for p in products:
        p.show()

def search_product():
    term = input("Search for? ")
    found = False
    for p in products:
        if term.lower() in p.name.lower():
            p.show()
            found = True
    if not found:
        print("Not found.")

print("=== SHOP INVENTORY ===")

while True:
    print("\n1. Add product")
    print("2. Show all")
    print("3. Search")
    print("4. Quit")
    choice = input("Pick: ")

    if choice == "1":
        add_product()
    elif choice == "2":
        show_all()
    elif choice == "3":
        search_product()
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid choice.")
