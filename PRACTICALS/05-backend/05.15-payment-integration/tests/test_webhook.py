# tests/test_webhook.py
import sys, os, hmac, hashlib, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mock_mpesa import app, SECRET
import pytest

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def make_sig(body_bytes):
    return hmac.new(SECRET, body_bytes, hashlib.sha256).hexdigest()


def test_valid_callback_marks_paid(client):
    # TODO 1
    body = {"transaction_id": "TXN-TEST-001", "order_id": 1}
    body_bytes = json.dumps(body).encode()

    # TODO 2
    sig = make_sig(body_bytes)

    # TODO 3
    response = client.post(
        "/webhook/mpesa",
        data=body_bytes,
        headers={"Content-Type": "application/json", "X-Signature": sig}
    )

    # TODO 4
    assert response.status_code == 200

    # TODO 5
    assert response.get_json()["status"] == "ok"


def test_bad_signature_rejected(client):
    body = {"transaction_id": "TXN-BAD-SIG", "order_id": 1}
    body_bytes = json.dumps(body).encode()

    # TODO 6
    response = client.post(
        "/webhook/mpesa",
        data=body_bytes,
        headers={"Content-Type": "application/json", "X-Signature": "wrong"}
    )

    # TODO 7
    assert response.status_code == 401


def test_replay_returns_already_processed(client):
    # TODO 8
    body = {"transaction_id": "TXN-REPLAY-001", "order_id": 1}
    body_bytes = json.dumps(body).encode()
    sig = make_sig(body_bytes)

    headers = {"Content-Type": "application/json", "X-Signature": sig}

    first = client.post("/webhook/mpesa", data=body_bytes, headers=headers)
    second = client.post("/webhook/mpesa", data=body_bytes, headers=headers)

    # TODO 9
    assert first.status_code == 200
    assert second.status_code == 200

    # TODO 10
    assert second.get_json()["status"] == "already processed"


def test_missing_transaction_id(client):
    # TODO 11
    body = {"order_id": 1}  # no transaction_id
    body_bytes = json.dumps(body).encode()
    sig = make_sig(body_bytes)

    response = client.post(
        "/webhook/mpesa",
        data=body_bytes,
        headers={"Content-Type": "application/json", "X-Signature": sig}
    )

    # TODO 12
    assert response.status_code == 400
