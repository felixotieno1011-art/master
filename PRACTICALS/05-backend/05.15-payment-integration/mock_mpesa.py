# mock_mpesa.py
from flask import Flask, request, jsonify
import sqlite3, hashlib, hmac, os, time

app = Flask(__name__)
DB = "payments.db"
SECRET = b"my-secret-key"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            amount INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS processed_callbacks (
            idempotency_key TEXT PRIMARY KEY,
            processed_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    # TODO 1: seed one order
    conn.execute("INSERT OR IGNORE INTO orders (id, amount, status) VALUES (1, 1000, 'pending')")
    conn.commit()
    conn.close()

@app.route("/webhook/mpesa", methods=["POST"])
def mpesa_webhook():
    # TODO 2: read the JSON body
    body = request.get_json()
    if not body:
        return jsonify({"error": "No JSON body"}), 400

    # TODO 3: verify HMAC signature
    signature = request.headers.get("X-Signature", "")
    expected = hmac.new(SECRET, request.get_data(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return jsonify({"error": "Invalid signature"}), 401

    # TODO 4: extract idempotency key
    idempotency_key = body.get("transaction_id")
    if not idempotency_key:
        return jsonify({"error": "Missing transaction_id"}), 400

    conn = sqlite3.connect(DB)

    # TODO 5: check if key exists
    existing = conn.execute(
        "SELECT 1 FROM processed_callbacks WHERE idempotency_key = ?",
        (idempotency_key,)
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({"status": "already processed"}), 200

    # TODO 6: mark order paid
    order_id = body.get("order_id", 1)
    conn.execute("UPDATE orders SET status='paid' WHERE id=?", (order_id,))

    # TODO 7: insert the idempotency key
    conn.execute(
        "INSERT INTO processed_callbacks (idempotency_key) VALUES (?)",
        (idempotency_key,)
    )
    conn.commit()
    conn.close()

    # TODO 8: return success
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    init_db()
    app.run(port=5000)
