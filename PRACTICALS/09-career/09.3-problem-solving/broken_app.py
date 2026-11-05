import json

def load_config():
    with open("config.json", "r") as f:
        data = json.load(f)
        return data["database"]["host"]

if __name__ == "__main__":
    print("Starting app...")
    host = load_config()
    print(f"Connected to {host}")
