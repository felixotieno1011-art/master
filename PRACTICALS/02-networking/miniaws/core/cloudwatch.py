"""CloudWatch — AWS's metrics, alarms, and logs.

Storage:
  state/cloudwatch/metrics/<namespace>/<metric>.json
  state/cloudwatch/alarms/<name>.json
  state/cloudwatch/logs/<log-group-with-slashes-encoded>.log
"""
import json
import os
import statistics
from datetime import datetime, timedelta

import config
from utils import now_iso, read_json, write_json, delete_file, ensure_dir
from core import account


CW_DIR       = os.path.join(config.STATE_DIR, "cloudwatch")
METRICS_DIR  = os.path.join(CW_DIR, "metrics")
ALARMS_DIR   = os.path.join(CW_DIR, "alarms")
LOGS_DIR     = os.path.join(CW_DIR, "logs")


def _metric_path(namespace, metric_name):
    ns_safe = namespace.replace("/", "_")
    return os.path.join(METRICS_DIR, ns_safe, f"{metric_name}.json")


def _alarm_path(name):
    return os.path.join(ALARMS_DIR, f"{name}.json")


def _log_path(log_group):
    """Encode slashes in the log group name so it's a single filename."""
    safe = log_group.replace("/", "__")
    return os.path.join(LOGS_DIR, f"{safe}.log")


def _decode_log_group(filename):
    """Reverse the encoding for listing."""
    base = filename[:-4] if filename.endswith(".log") else filename
    return base.replace("__", "/")


# ---------- Metrics ----------

def put_metric_data(namespace, metric_name, value, unit="None", dimensions=None):
    if not isinstance(value, (int, float)):
        return False, "value must be a number"

    dims = dimensions or {}
    path = _metric_path(namespace, metric_name)
    existing = read_json(path) or {
        "namespace": namespace,
        "metricName": metric_name,
        "unit": unit,
        "datapoints": [],
    }
    existing["unit"] = unit

    existing["datapoints"].append({
        "timestamp": now_iso(),
        "value": float(value),
        "dimensions": dims,
    })
    existing["datapoints"] = existing["datapoints"][-500:]

    write_json(path, existing)
    return True, f"put metric {namespace}/{metric_name} = {value}"


def list_metrics(namespace=None):
    ensure_dir(METRICS_DIR)
    out = []
    for ns_dir in sorted(os.listdir(METRICS_DIR)):
        full_ns = os.path.join(METRICS_DIR, ns_dir)
        if not os.path.isdir(full_ns):
            continue
        real_ns = ns_dir.replace("_", "/")
        if namespace and real_ns != namespace:
            continue
        for f in sorted(os.listdir(full_ns)):
            if f.endswith(".json"):
                d = read_json(os.path.join(full_ns, f))
                if d:
                    out.append({
                        "namespace": d["namespace"],
                        "metricName": d["metricName"],
                        "datapoints": len(d["datapoints"]),
                        "unit": d.get("unit", "None"),
                    })
    return out


def _get_datapoints(namespace, metric_name):
    d = read_json(_metric_path(namespace, metric_name))
    return d["datapoints"] if d else []


def get_metric_statistics(namespace, metric_name, period_sec=300, stat="Average"):
    dps = _get_datapoints(namespace, metric_name)
    if not dps:
        return None
    values = [d["value"] for d in dps]

    if stat == "Sum":         agg = sum(values)
    elif stat == "Average":   agg = statistics.mean(values)
    elif stat == "Min":       agg = min(values)
    elif stat == "Max":       agg = max(values)
    elif stat == "SampleCount": agg = len(values)
    else:
        return None

    return {
        "namespace": namespace,
        "metricName": metric_name,
        "statistic": stat,
        "sampleCount": len(values),
        "value": round(agg, 3),
        "datapoints": dps,
    }


# ---------- Alarms ----------

def put_metric_alarm(alarm_name, namespace, metric_name,
                     threshold, comparison="GreaterThanThreshold",
                     evaluation_periods=1, stat="Average"):
    if comparison not in ("GreaterThanThreshold", "LessThanThreshold",
                          "GreaterThanOrEqualToThreshold",
                          "LessThanOrEqualToThreshold"):
        return False, f"invalid comparison '{comparison}'"

    data = {
        "alarmName": alarm_name,
        "namespace": namespace,
        "metricName": metric_name,
        "statistic": stat,
        "threshold": float(threshold),
        "comparisonOperator": comparison,
        "evaluationPeriods": int(evaluation_periods),
        "stateValue": "INSUFFICIENT_DATA",
        "stateReason": "Not yet evaluated",
        "created": now_iso(),
    }
    ensure_dir(ALARMS_DIR)
    write_json(_alarm_path(alarm_name), data)
    return True, f"created alarm '{alarm_name}'"


def list_alarms():
    ensure_dir(ALARMS_DIR)
    out = []
    for f in sorted(os.listdir(ALARMS_DIR)):
        if f.endswith(".json"):
            d = read_json(os.path.join(ALARMS_DIR, f))
            if d:
                out.append(d)
    return out


def delete_alarm(alarm_name):
    if not os.path.exists(_alarm_path(alarm_name)):
        return False, f"alarm '{alarm_name}' not found"
    delete_file(_alarm_path(alarm_name))
    return True, f"deleted alarm '{alarm_name}'"


def _eval_comparison(value, threshold, op):
    if op == "GreaterThanThreshold":           return value > threshold
    if op == "LessThanThreshold":              return value < threshold
    if op == "GreaterThanOrEqualToThreshold":  return value >= threshold
    if op == "LessThanOrEqualToThreshold":     return value <= threshold
    return False


def evaluate_alarms():
    results = []
    for alarm in list_alarms():
        stats = get_metric_statistics(alarm["namespace"], alarm["metricName"],
                                      stat=alarm["statistic"])
        if not stats:
            new_state = "INSUFFICIENT_DATA"
            reason = "No datapoints"
        else:
            value = stats["value"]
            breached = _eval_comparison(value, alarm["threshold"],
                                        alarm["comparisonOperator"])
            new_state = "ALARM" if breached else "OK"
            reason = (f"{alarm['statistic']}={value} "
                      f"{alarm['comparisonOperator']} {alarm['threshold']}")

        changed = new_state != alarm.get("stateValue")
        alarm["stateValue"] = new_state
        alarm["stateReason"] = reason
        alarm["stateUpdated"] = now_iso()
        write_json(_alarm_path(alarm["alarmName"]), alarm)

        if changed:
            results.append((alarm["alarmName"], new_state, reason))
    return results


# ---------- Logs (FIXED to handle / in group names) ----------

def create_log_group(name):
    ensure_dir(LOGS_DIR)
    path = _log_path(name)
    if os.path.exists(path):
        return False, f"log group '{name}' already exists"
    with open(path, "w"):
        pass
    return True, f"created log group '{name}'"


def put_log_events(log_group, message):
    ensure_dir(LOGS_DIR)
    path = _log_path(log_group)
    # If the group doesn't exist yet, create it silently
    if not os.path.exists(path):
        with open(path, "w"):
            pass
    with open(path, "a") as f:
        f.write(f"{now_iso()}  {message}\n")
    return True, "logged"


def describe_log_groups():
    ensure_dir(LOGS_DIR)
    out = []
    for f in sorted(os.listdir(LOGS_DIR)):
        if f.endswith(".log"):
            path = os.path.join(LOGS_DIR, f)
            with open(path) as fh:
                lines = fh.readlines()
            out.append({
                "logGroupName": _decode_log_group(f),
                "storedBytes": os.path.getsize(path),
                "events": len(lines),
            })
    return out


def get_log_events(log_group, limit=50):
    path = _log_path(log_group)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        lines = f.readlines()
    return [l.rstrip() for l in lines[-limit:]]


# ---------- Built-in metric collector ----------

def collect_instance_metrics():
    from core import ec2
    from core import ec2_runtime

    recorded = 0
    for inst in ec2.list_all():
        iid = inst["instance_id"]
        if inst.get("state") != "running":
            continue
        pid = ec2_runtime.get_pid(iid)
        if not pid:
            continue
        proc = ec2.read_proc_stats(pid)
        if not proc:
            continue

        mem_mb = proc.get("memory_kb", 0) / 1024
        mem_pct = round((mem_mb / inst["hardware"]["memory_mb"]) * 100, 2)

        put_metric_data("AWS/EC2", "MemoryUtilization", mem_pct,
                        unit="Percent", dimensions={"InstanceId": iid})
        put_metric_data("AWS/EC2", "MemoryUsedMB", round(mem_mb, 2),
                        unit="Megabytes", dimensions={"InstanceId": iid})

        cpu = 2.0 if proc.get("proc_state") == "S" else 12.0
        put_metric_data("AWS/EC2", "CPUUtilization", cpu,
                        unit="Percent", dimensions={"InstanceId": iid})

        recorded += 1
    return recorded
