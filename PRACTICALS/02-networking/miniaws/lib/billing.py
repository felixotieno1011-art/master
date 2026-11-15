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
    "lambda.invoke":               0.0000208,   # per invocation
    "dynamodb.write":              0.00000125,  # per write unit
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
    events = data.get("events", [])
    legacy_total = data.get("total", 0.0)
    accrued_total = get_accrued_total()

    print(f"💰 MiniAWS Billing Summary")
    print(f"   Total accrued:   ${accrued_total:.6f}  (from live resources)")
    print(f"   Legacy charges:  ${legacy_total:.6f}  (from old charge events)")
    print(f"   Combined:        ${accrued_total + legacy_total:.6f}")
    print(f"   Events: {len(events)}")
    print()
    if not events:
        print("   (no charges yet)")
        return

    print(f"   {'TIME':<22} {'EVENT':<40} {'AMOUNT':>10}")
    print("   " + "-" * 75)
    for e in events[-20:]:
        t = e.get("time", "")[:19]
        etype = e.get("type", "charge")
        if etype in ("start", "stop"):
            # Accrual events have no "amount" — show the resource and rate
            svc = e.get("service", "")
            res = e.get("resource", "")
            k = f"{etype}:{svc}:{res}"
            if etype == "start":
                rate = e.get("rate", 0)
                info = f"@ ${rate:.4f}/hr"
            else:
                info = "(stopped)"
            print(f"   {t:<22} {k:<40} {info:>10}")
        else:
            # Legacy charge() events
            k = e.get("key", "?")
            amt = e.get("amount", 0.0)
            print(f"   {t:<22} {k:<40} ${amt:>9.6f}")
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

# ============================================================
# Billing Model B — start/stop tracking with time-based accrual
# ============================================================

from datetime import datetime as _dt


def _parse_time(iso):
    """Parse ISO time string into Unix timestamp."""
    try:
        return _dt.fromisoformat(str(iso).replace("Z", "")).timestamp()
    except Exception:
        return 0.0


def record_start(resource_id, service, rate, note=""):
    """Log that a resource started (called at creation time).

    Deduplicates: if the resource already has an unmatched start event
    (still running), skip — prevents double-counting from repeated calls.
    """
    if not resource_id:
        return False

    data = _load()
    events = data.get("events", [])

    # Count pending starts for this resource
    starts = sum(1 for e in events
                 if e.get("type") == "start" and e.get("resource") == resource_id)
    stops = sum(1 for e in events
                if e.get("type") == "stop" and e.get("resource") == resource_id)

    if starts > stops:
        # Already running, don't double-count
        return False

    events.append({
        "type": "start",
        "time": datetime.now().isoformat(timespec="seconds"),
        "resource": resource_id,
        "service": service,
        "rate": float(rate),
        "note": note,
    })
    data["events"] = events
    _save(data)
    return True


def record_stop(resource_id, service=None, note=""):
    """Log that a resource stopped (called at delete time)."""
    if not resource_id:
        return False
    data = _load()
    events = data.get("events", [])
    starts = sum(1 for e in events
                 if e.get("type") == "start" and e.get("resource") == resource_id)
    stops = sum(1 for e in events
                if e.get("type") == "stop"  and e.get("resource") == resource_id)
    if starts <= stops:
        return False
    events.append({
        "type": "stop",
        "time": datetime.now().isoformat(timespec="seconds"),
        "resource": resource_id,
        "service": service or "",
        "note": note,
    })
    data["events"] = events
    _save(data)
    return True


def get_accrued_total():
    """Compute total cost from start/stop events.

    For each 'start', find matching 'stop' (or use now()).
    Cost = rate × hours.
    """
    data = _load()
    events = data.get("events", [])

    # Build map: resource_id → list of (start_time, rate, service)
    starts = {}
    total = 0.0
    now_ts = _dt.now().timestamp()

    for e in events:
        if e.get("type") == "start":
            rid = e.get("resource")
            if rid:
                starts.setdefault(rid, []).append({
                    "time": _parse_time(e.get("time")),
                    "rate": float(e.get("rate", 0)),
                    "service": e.get("service", "unknown"),
                })
        elif e.get("type") == "stop":
            rid = e.get("resource")
            if rid and rid in starts and starts[rid]:
                start = starts[rid].pop(0)
                stop_ts = _parse_time(e.get("time"))
                hours = max(stop_ts - start["time"], 0) / 3600
                total += start["rate"] * hours

    # Still running
    for rid, pending in starts.items():
        for start in pending:
            hours = max(now_ts - start["time"], 0) / 3600
            total += start["rate"] * hours

    return total


def get_accrued_by_service():
    """Same as get_accrued_total but grouped by service."""
    data = _load()
    events = data.get("events", [])

    starts = {}
    by_service = {}
    now_ts = _dt.now().timestamp()

    for e in events:
        if e.get("type") == "start":
            rid = e.get("resource")
            if rid:
                starts.setdefault(rid, []).append({
                    "time": _parse_time(e.get("time")),
                    "rate": float(e.get("rate", 0)),
                    "service": e.get("service", "unknown"),
                })
        elif e.get("type") == "stop":
            rid = e.get("resource")
            if rid and rid in starts and starts[rid]:
                start = starts[rid].pop(0)
                stop_ts = _parse_time(e.get("time"))
                hours = max(stop_ts - start["time"], 0) / 3600
                by_service[start["service"]] = by_service.get(start["service"], 0) + start["rate"] * hours

    for rid, pending in starts.items():
        for start in pending:
            hours = max(now_ts - start["time"], 0) / 3600
            by_service[start["service"]] = by_service.get(start["service"], 0) + start["rate"] * hours

    return by_service


def reset_with_backup():
    """Reset billing but keep a backup of old events."""
    import shutil
    backup = BILLING_FILE + ".before-model-B"
    if os.path.isfile(BILLING_FILE):
        shutil.copy(BILLING_FILE, backup)
    _save({"events": [], "total": 0.0})
    return True


if __name__ == "__main__":
    main()
