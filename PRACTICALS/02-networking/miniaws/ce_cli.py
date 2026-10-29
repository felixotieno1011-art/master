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

    # Load billing events
    try:
        data = billing_mod._load()
        events = data.get("events", [])
    except Exception:
        events = []

    # Filter by time period
    filtered = []
    for e in events:
        ts = e.get("time", "")
        try:
            d = datetime.fromisoformat(ts).date()
        except Exception:
            continue
        if start_date:
            try:
                if d < datetime.fromisoformat(start_date).date():
                    continue
            except Exception:
                pass
        if end_date:
            try:
                if d > datetime.fromisoformat(end_date).date():
                    continue
            except Exception:
                pass
        filtered.append(e)

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
