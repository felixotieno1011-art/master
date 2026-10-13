class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def discount(self, pct):
        self.price = self.price - (self.price * pct / 100)

    def show(self):
        print(f"{self.name}: {self.price} KES x{self.quantity}")

sugar = Product("sugar", 120, 50)
sugar.show()
sugar.discount(10)
sugar.show()
