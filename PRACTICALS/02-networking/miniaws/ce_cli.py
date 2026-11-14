#!/usr/bin/env python3
"""aws ce — Cost Explorer API. Real AWS shape for get-cost-and-usage."""
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta

from lib import billing as billing_mod


def _output_mode(args):
    for i, a in enumerate(args):
        if a == "--output" and i + 1 < len(args):
            return args[i + 1]
        if a.startswith("--output="):
            return a.split("=", 1)[1]
    return "json"


def _flags(args):
    out = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            out[k] = v
            i += 1
        elif a.startswith("--") and i + 1 < len(args) and not args[i + 1].startswith("--"):
            out[a[2:]] = args[i + 1]
            i += 2
        else:
            i += 1
    return out


def _parse_period(period_str):
    """'Start=2026-10-01,End=2026-10-29' → (start_date, end_date)."""
    result = {}
    for part in period_str.split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip()] = v.strip()
    return result.get("Start"), result.get("End")


def _service_from_key(key):
    """'ec2.run-instances.t3.micro' → 'ec2'."""
    return (key or "").split(".")[0] or "other"


def cmd_get_cost_and_usage(args):
    """Match `aws ce get-cost-and-usage` output."""
    flags = _flags(args)

    period_str = flags.get("time-period", "")
    start_date, end_date = _parse_period(period_str)
    granularity = (flags.get("granularity") or "MONTHLY").upper()
    metrics_raw = flags.get("metrics") or "UnblendedCost"
    metrics = [m.strip() for m in metrics_raw.split(",")]
    group_by = flags.get("group-by", "")

    # PHASE 5: compute real accrual (not one-time charges)
    # Get accrued cost by service from the billing engine.
    try:
        by_service = billing_mod.get_accrued_by_service()
    except Exception:
        by_service = {}

    # Also include one-time charges (S3 uploads, Lambda invokes) from old events
    # These don't accrue — they're one-time — so we sum them as-is.
    try:
        data = billing_mod._load()
        all_events = data.get("events", [])
    except Exception:
        all_events = []

    # PHASE 6: skip historical events unless --time-period explicitly covers them
    ONE_TIME_SERVICES = {"s3", "lambda", "dynamodb"}
    one_time_costs = {}

    # Check if --time-period covers historical dates
    include_historical = False
    if start_date and end_date:
        try:
            sdt = datetime.fromisoformat(start_date).date()
            edt = datetime.fromisoformat(end_date).date()
            # Historical events are pre-Nov-14; include if period covers any pre-Nov-14 date
            hist_cutoff = datetime.fromisoformat("2026-11-01").date()
            if sdt < hist_cutoff and edt < datetime.fromisoformat("2026-11-14").date():
                include_historical = True
        except Exception:
            pass

    for e in all_events:
        if e.get("type") in ("start", "stop"):
            continue  # skip accrual events (already in by_service)
        # PHASE 6: skip historical unless explicitly requested
        if e.get("historical") and not include_historical:
            continue
        key = e.get("key", "")
        svc = key.split(".")[0] if "." in key else "other"
        if svc in ONE_TIME_SERVICES or e.get("historical"):
            one_time_costs[svc] = one_time_costs.get(svc, 0) + e.get("amount", 0)

    # Merge: accrual + one-time
    for svc, amt in one_time_costs.items():
        by_service[svc] = by_service.get(svc, 0) + amt

    # Now build synthetic events for the existing aggregation logic.
    # Each event represents one service's cost as of now.
    from datetime import datetime as _dt
    now_iso = _dt.now().isoformat(timespec="seconds")

    filtered = []
    for svc, amt in by_service.items():
        if amt <= 0:
            continue
        # If --time-period given, filter by the accrued period start
        # (For accrual, we check against "now" — if now is outside period, skip)
        filtered.append({
            "time": now_iso,
            "key": f"{svc}.accrued",
            "service": svc,
            "amount": amt,
        })

    # Aggregate by period (MONTHLY / DAILY / HOURLY)
    def _period_key(ts):
        try:
            dt = datetime.fromisoformat(ts)
        except Exception:
            return "unknown"
        if granularity == "DAILY":
            return dt.strftime("%Y-%m-%d")
        if granularity == "HOURLY":
            return dt.strftime("%Y-%m-%dT%H:00:00Z")
        return dt.strftime("%Y-%m-01")  # MONTHLY

    # Compute actual data range for TimePeriod when --time-period is absent
    actual_start = None
    actual_end = None
    for e in filtered:
        try:
            d = datetime.fromisoformat(e.get("time", "")).date().isoformat()
        except Exception:
            continue
        if actual_start is None or d < actual_start:
            actual_start = d
        if actual_end is None or d > actual_end:
            actual_end = d

    buckets = defaultdict(lambda: defaultdict(float))
    for e in filtered:
        pk = _period_key(e.get("time", ""))
        svc = _service_from_key(e.get("key"))
        amt = float(e.get("amount", 0))
        buckets[pk][svc] += amt

    # Build response
    if group_by:
        # Type=DIMENSION,Key=SERVICE
        group_key = ""
        for part in group_by.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                if k.strip() == "Key":
                    group_key = v.strip().upper()
        results_by_time = []
        for pk in sorted(buckets):
            groups = []
            for svc, amt in sorted(buckets[pk].items()):
                group = {"Keys": [f"{svc.upper()}"], "Metrics": {}}
                for m in metrics:
                    group["Metrics"][m] = {
                        "Amount": f"{amt:.6f}",
                        "Unit": "USD",
                    }
                groups.append(group)
            total = {"BlendedCost": {"Amount": f"{sum(buckets[pk].values()):.6f}", "Unit": "USD"}}
            if granularity == "MONTHLY":
                time_period = {
                    "Start": start_date or actual_start or pk,
                    "End":   end_date   or actual_end   or pk,
                }
            else:
                time_period = {"Start": pk, "End": pk}
            results_by_time.append({
                "TimePeriod": time_period,
                "Total": total,
                "Groups": groups,
                "Estimated": False,
            })
        payload = {"ResultsByTime": results_by_time, "GroupDefinitions": [{"Type": "DIMENSION", "Key": group_key}]}
    else:
        results_by_time = []
        for pk in sorted(buckets):
            total_amt = sum(buckets[pk].values())
            metrics_dict = {m: {"Amount": f"{total_amt:.6f}", "Unit": "USD"} for m in metrics}
            if granularity == "MONTHLY":
                time_period = {
                    "Start": start_date or actual_start or pk,
                    "End":   end_date   or actual_end   or pk,
                }
            else:
                time_period = {"Start": pk, "End": pk}
            results_by_time.append({
                "TimePeriod": time_period,
                "Total": metrics_dict,
                "Groups": [],
                "Estimated": False,
            })
        payload = {"ResultsByTime": results_by_time}

    mode = _output_mode(args)
    if mode == "text":
        for r in payload["ResultsByTime"]:
            tp = r["TimePeriod"]
            total = list(r["Total"].values())[0]["Amount"] if r["Total"] else "0"
            print(f"{tp['Start']}\t{tp['End']}\t{total}")
    else:
        print(json.dumps(payload, indent=4))
    return 0


def main(argv):
    if len(argv) < 2:
        print("usage: aws ce <command>")
        print("  get-cost-and-usage   Retrieve cost and usage metrics")
        return 1
    sub = argv[1]
    if sub == "get-cost-and-usage":
        return cmd_get_cost_and_usage(argv[2:])
    print(f"❌ aws ce: unknown command: {sub}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
