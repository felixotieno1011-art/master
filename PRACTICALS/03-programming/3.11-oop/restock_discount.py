class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def discount(self, pct):
        self.price = self.price - (self.price * pct / 100)

    def restock(self, amount):
        self.quantity = self.quantity + amount

    def show(self):
        print(f"{self.name}: {self.price} KES x{self.quantity}")

item = Product("USB Cable", 200, 10)
item.show()
item.restock(5)
item.show()
item.discount(10)
item.show()
