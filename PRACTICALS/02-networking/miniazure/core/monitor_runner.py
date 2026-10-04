"""Standalone monitor process.

Run with:  python -m core.monitor_runner [interval_seconds] [max_iterations]
"""
import sys
from core import monitor


def main():
    interval = 15
    max_iter = None

    if len(sys.argv) > 1:
        interval = int(sys.argv[1])
    if len(sys.argv) > 2:
        max_iter = int(sys.argv[2])

    monitor.start_loop(interval_sec=interval, max_iterations=max_iter)


if __name__ == "__main__":
    main()
