#!/usr/bin/env python3
"""CloudWatch CLI — standalone."""
import sys
import json
import utils
from core import cloudwatch


def parse(args):
    flags = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--"):
            if "=" in a:
                k, v = a[2:].split("=", 1); flags[k] = v
            else:
                k = a[2:]
                if i + 1 < len(args) and not args[i + 1].startswith("--"):
                    flags[k] = args[i + 1]; i += 1
                else:
                    flags[k] = True
        i += 1
    return flags


USAGE = """
CLOUDWATCH COMMANDS:
  put-metric-data --namespace <ns> --metric <name> --value <n> [--unit <u>]
  list-metrics [--namespace <ns>]
  get-metric-statistics --namespace <ns> --metric <name> [--stat Average|Sum|Min|Max|SampleCount]
  put-metric-alarm --name <n> --namespace <ns> --metric <m> --threshold <t> [--comparison <c>] [--stat <s>]
  list-alarms
  delete-alarm <name>
  evaluate-alarms
  create-log-group <name>
  describe-log-groups
  put-log-event <group> <message>
  get-log-events <group> [--limit N]
  collect
"""


def cmd(args):
    if not args or args[0] in ("-h", "--help", "help"):
        print(USAGE); return 1
    sub, rest = args[0], args[1:]
    flags = parse(rest)

    if sub == "put-metric-data":
        ns = flags.get("namespace"); m = flags.get("metric")
        v = flags.get("value")
        unit = flags.get("unit") or "None"
        if not ns or not m or v is None:
            print(utils.err("--namespace --metric --value required")); return 1
        try:
            v = float(v)
        except ValueError:
            print(utils.err("--value must be a number")); return 1
        ok_, msg = cloudwatch.put_metric_data(ns, m, v, unit=unit)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "list-metrics":
        ns = flags.get("namespace") if isinstance(flags.get("namespace"), str) else None
        metrics = cloudwatch.list_metrics(namespace=ns)
        if not metrics:
            print(utils.warn("no metrics")); return 0
        print(f"{'NAMESPACE':<20} {'METRIC':<25} {'POINTS':<10} {'UNIT':<12}")
        print("-" * 70)
        for m in metrics:
            print(f"{m['namespace']:<20} {m['metricName']:<25} {m['datapoints']:<10} {m['unit']:<12}")
        return 0

    if sub == "get-metric-statistics":
        ns = flags.get("namespace"); m = flags.get("metric")
        stat = flags.get("stat") or "Average"
        if not ns or not m:
            print(utils.err("--namespace --metric required")); return 1
        r = cloudwatch.get_metric_statistics(ns, m, stat=stat)
        if not r:
            print(utils.warn("no datapoints")); return 0
        print(f"Namespace:   {r['namespace']}")
        print(f"Metric:      {r['metricName']}")
        print(f"Statistic:   {r['statistic']} = {r['value']}")
        print(f"SampleCount: {r['sampleCount']}")
        return 0

    if sub == "put-metric-alarm":
        name = flags.get("name"); ns = flags.get("namespace")
        m = flags.get("metric"); th = flags.get("threshold")
        comp = flags.get("comparison") or "GreaterThanThreshold"
        stat = flags.get("stat") or "Average"
        if not name or not ns or not m or th is None:
            print(utils.err("--name --namespace --metric --threshold required")); return 1
        try:
            th = float(th)
        except ValueError:
            print(utils.err("--threshold must be a number")); return 1
        ok_, msg = cloudwatch.put_metric_alarm(name, ns, m, th, comparison=comp, stat=stat)
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "list-alarms":
        alarms = cloudwatch.list_alarms()
        if not alarms:
            print(utils.warn("no alarms")); return 0
        print(f"{'NAME':<20} {'METRIC':<22} {'STATE':<18} {'REASON':<30}")
        print("-" * 95)
        for a in alarms:
            print(f"{a['alarmName']:<20} {a['metricName']:<22} {a['stateValue']:<18} {a.get('stateReason','')[:30]:<30}")
        return 0

    if sub == "delete-alarm":
        if not rest:
            print(utils.err("alarm name required")); return 1
        ok_, msg = cloudwatch.delete_alarm(rest[0])
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "evaluate-alarms":
        changes = cloudwatch.evaluate_alarms()
        if not changes:
            print(utils.ok("no alarm state changes")); return 0
        for name, state, reason in changes:
            print(f"  {name} -> {state}  ({reason})")
        return 0

    if sub == "create-log-group":
        if not rest:
            print(utils.err("group name required")); return 1
        ok_, msg = cloudwatch.create_log_group(rest[0])
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "describe-log-groups":
        groups = cloudwatch.describe_log_groups()
        if not groups:
            print(utils.warn("no log groups")); return 0
        print(f"{'LOG GROUP':<30} {'EVENTS':<10} {'BYTES':<10}")
        print("-" * 55)
        for g in groups:
            print(f"{g['logGroupName']:<30} {g['events']:<10} {g['storedBytes']:<10}")
        return 0

    if sub == "put-log-event":
        if len(rest) < 2:
            print(utils.err("usage: put-log-event <group> <message>")); return 1
        ok_, msg = cloudwatch.put_log_events(rest[0], rest[1])
        print(utils.ok(msg) if ok_ else utils.err(msg))
        return 0 if ok_ else 1

    if sub == "get-log-events":
        if not rest:
            print(utils.err("group required")); return 1
        limit = int(flags.get("limit", 50)) if isinstance(flags.get("limit"), str) else 50
        lines = cloudwatch.get_log_events(rest[0], limit=limit)
        if lines is None:
            print(utils.err(f"log group '{rest[0]}' not found")); return 1
        for l in lines:
            print(l)
        return 0

    if sub == "collect":
        n = cloudwatch.collect_instance_metrics()
        print(utils.ok(f"collected metrics from {n} instances"))
        return 0

    print(utils.err(f"unknown cloudwatch subcommand: {sub}")); return 1


if __name__ == "__main__":
    sys.exit(cmd(sys.argv[1:]))
