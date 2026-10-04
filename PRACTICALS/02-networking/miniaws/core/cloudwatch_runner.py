"""Standalone CloudWatch monitor loop.

Usage:
  python -m core.cloudwatch_runner [interval_seconds] [max_iterations]
"""
import sys
import time

from utils import now_iso
from core import cloudwatch


def loop(interval_sec=15, max_iterations=None):
    print(f"▶️  CloudWatch agent starting (interval {interval_sec}s)")
    iteration = 0
    try:
        while True:
            n = cloudwatch.collect_instance_metrics()
            cloudwatch.put_log_events("miniaws/agent",
                                      f"collected {n} instance metric sets")
            # Evaluate alarms
            changes = cloudwatch.evaluate_alarms()
            for name, state, reason in changes:
                cloudwatch.put_log_events(
                    "miniaws/alarms",
                    f"alarm {name} -> {state} ({reason})"
                )
            iteration += 1
            print(f"[{now_iso()}] check #{iteration}: {n} instances, "
                  f"{len(changes)} alarm change(s)")

            if max_iterations and iteration >= max_iterations:
                break
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("\n🛑 CloudWatch agent stopped.")


def main():
    interval = 15
    max_iter = None
    if len(sys.argv) > 1:
        interval = int(sys.argv[1])
    if len(sys.argv) > 2:
        max_iter = int(sys.argv[2])
    loop(interval_sec=interval, max_iterations=max_iter)


if __name__ == "__main__":
    main()
