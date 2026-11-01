import sqlite3

class User:
    table = "users"

    def __init__(self, name, email):
        self.id = None
        self.name = name
        self.email = email

def save(self):
    conn = sqlite3.connect("mini_orm.db")
    cursor = conn.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        (self.name, self.email)
    )
    self.id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"Saved {self.name} with id={self.id}")

def create_table():
    conn = sqlite3.connect("mini_orm.db")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT, "
        "email TEXT)"
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_table()
    print("Table ready.")
