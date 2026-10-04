"""Cost tracking — mimicking AWS billing."""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

proj = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(proj))

BILLING_FILE = os.path.join(str(proj), "state", "billing.json")

# Realistic AWS pricing (simplified)
PRICING = {
    "ec2.run-instances.t3.micro":  0.0104,   # $/hour
    "ec2.run-instances.t3.small":  0.0208,
    "ec2.run-instances.t3.medium": 0.0416,
    "ec2.run-instances.t3.large":  0.0832,
    "s3.mb-bucket":                0.00,     # free
    "s3.upload":                   0.000023, # $/GB
    "vpc.create":                  0.00,     # free
    "vpc.create-igw":              0.045,    # $/hour
    "vpc.create-nat":              0.045,    # $/hour
    "cloudwatch.metric":           0.0000003,
}


def _load():
    if not os.path.isfile(BILLING_FILE):
        return {"events": [], "total": 0.0}
    try:
        with open(BILLING_FILE) as f:
            return json.load(f)
    except Exception:
        return {"events": [], "total": 0.0}


def _save(data):
    os.makedirs(os.path.dirname(BILLING_FILE), exist_ok=True)
    with open(BILLING_FILE, "w") as f:
        json.dump(data, f, indent=2)


def charge(key, quantity=1, note=""):
    """Record a charge."""
    rate = PRICING.get(key)
    if rate is None:
        rate = 0.0
    amount = rate * quantity

    data = _load()
    data["events"].append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "key": key,
        "quantity": quantity,
        "rate": rate,
        "amount": round(amount, 6),
        "note": note,
    })
    data["total"] = round(data.get("total", 0.0) + amount, 6)
    _save(data)
    return amount


def get_total():
    return _load()["total"]


def reset():
    _save({"events": [], "total": 0.0})
    return True


def show():
    data = _load()
    total = data.get("total", 0.0)
    events = data.get("events", [])

    print(f"💰 MiniAWS Billing Summary")
    print(f"   Total (simulated): ${total:.4f}")
    print(f"   Events: {len(events)}")
    print()
    if not events:
        print("   (no charges yet)")
        return

    print(f"   {'TIME':<22} {'SERVICE.ACTION':<30} {'AMOUNT':>10}")
    print("   " + "-" * 65)
    for e in events[-20:]:
        t = e["time"][:19]
        k = e["key"]
        amt = e["amount"]
        print(f"   {t:<22} {k:<30} ${amt:>9.6f}")
    if len(events) > 20:
        print(f"   ... and {len(events) - 20} more")


def main():
    if len(sys.argv) < 2:
        print("usage: billing.py <show|total|reset|charge>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "show":
        show()
    elif cmd == "total":
        print(f"${get_total():.4f}")
    elif cmd == "reset":
        reset()
        print("✅ billing reset")
    elif cmd == "charge":
        if len(sys.argv) < 3:
            print("usage: billing.py charge <key> [quantity]")
            sys.exit(1)
        key = sys.argv[2]
        qty = float(sys.argv[3]) if len(sys.argv) > 3 else 1
        amt = charge(key, qty)
        print(f"✅ charged ${amt:.6f} for {key}")
    else:
        print(f"unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
