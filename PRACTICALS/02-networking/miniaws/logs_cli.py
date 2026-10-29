#!/usr/bin/env python3
"""aws logs — CloudWatch Logs API. Real AWS shape for filter-log-events."""
import json
import sys
import time

from core import cloudwatch as cw


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


def _log_groups_list():
    """Get all log groups from CloudWatch state."""
    try:
        raw = cw.describe_log_groups()
    except Exception:
        return []
    groups = []
    for g in raw or []:
        name = g.get("log_group") or g.get("logGroupName") or g.get("name", "")
        if name:
            groups.append(name)
    return groups


def _get_events(log_group, start_ms=None, end_ms=None, limit=100):
    """Fetch events for a log group, filtered by time range."""
    try:
        events = cw.get_log_events(log_group, limit=1000)
    except Exception:
        return []

    if not isinstance(events, list):
        return []

    # Filter by timestamp range
    filtered = []
    for ev in events:
        # get_log_events() can return strings (raw lines) OR dicts (structured).
        if isinstance(ev, dict):
            ts_str = ev.get("timestamp", "")
            message = ev.get("message", "")
            stream = ev.get("stream", "default")
        else:
            # Raw string line — split "ISO timestamp  message" if possible
            s = str(ev)
            parts = s.split(None, 1)
            ts_str = parts[0] if parts else ""
            message = parts[1] if len(parts) > 1 else s
            stream = "default"

        try:
            dt = __import__("datetime").datetime.fromisoformat(str(ts_str).replace("Z", ""))
            ts_ms = int(dt.timestamp() * 1000)
        except Exception:
            ts_ms = 0

        if start_ms and ts_ms < int(start_ms):
            continue
        if end_ms and ts_ms > int(end_ms):
            continue

        filtered.append({
            "logStreamName": stream,
            "timestamp": ts_ms,
            "message": message,
            "ingestionTime": ts_ms,
            "eventId": f"ev-{hash(message) & 0xffffffff:08x}",
        })

    return filtered[:limit]


def cmd_describe_log_groups(args):
    groups = _log_groups_list()
    payload = {
        "logGroups": [
            {
                "logGroupName": g,
                "creationTime": int(time.time() * 1000),
                "metricFilterCount": 0,
                "arn": f"arn:aws:logs:local:740762029392:log-group:{g}:*",
                "storedBytes": 0,
            }
            for g in groups
        ]
    }
    print(json.dumps(payload, indent=4))
    return 0


def cmd_filter_log_events(args):
    """Match `aws logs filter-log-events` output."""
    flags = _flags(args)
    log_group = flags.get("log-group-name", "")
    pattern = flags.get("filter-pattern", "")
    start_ms = flags.get("start-time")
    end_ms = flags.get("end-time")
    limit = int(flags.get("limit", "10000"))

    if not log_group:
        print("❌ --log-group-name required", file=sys.stderr)
        return 1

    events = _get_events(log_group, start_ms=start_ms, end_ms=end_ms, limit=limit)

    # Apply --filter-pattern (simple substring match, like CloudWatch's simplest pattern)
    if pattern:
        events = [e for e in events if pattern.lower() in e["message"].lower()]

    payload = {
        "events": events,
        "searchedLogStreams": [],
        "nextToken": "",
    }
    print(json.dumps(payload, indent=4))
    return 0


def cmd_create_log_group(args):
    flags = _flags(args)
    name = flags.get("log-group-name", "")
    if not name:
        print("❌ --log-group-name required", file=sys.stderr)
        return 1
    ok_, msg = cw.create_log_group(name)
    print(f"✅ {msg}" if ok_ else f"❌ {msg}")
    return 0 if ok_ else 1


def main(argv):
    if len(argv) < 2:
        print("usage: aws logs <command>")
        print("  describe-log-groups    List log groups")
        print("  filter-log-events      Query log events")
        print("  create-log-group       Create a log group")
        return 1
    sub = argv[1]
    rest = argv[2:]

    if sub == "describe-log-groups":
        return cmd_describe_log_groups(rest)
    if sub == "filter-log-events":
        return cmd_filter_log_events(rest)
    if sub == "create-log-group":
        return cmd_create_log_group(rest)

    print(f"❌ aws logs: unknown command: {sub}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
