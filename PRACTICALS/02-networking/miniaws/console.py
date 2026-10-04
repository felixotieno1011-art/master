#!/usr/bin/env python3
"""Console CLI — generate or serve the dashboard."""
import sys
import utils
from core import console, console_server


def main():
    args = sys.argv[1:]
    if not args or args[0] not in ("generate", "serve"):
        print("usage: python console.py generate|serve")
        print("  generate  — write reports/console.html")
        print("  serve     — serve on http://localhost:7000")
        return 1
    sub = args[0]
    if sub == "generate":
        path = console.write_dashboard("reports/console.html")
        print(utils.ok(f"console written: {path}"))
        print(f"   Open: termux-open {path}")
        return 0
    if sub == "serve":
        console_server.serve()
        return 0


if __name__ == "__main__":
    sys.exit(main())
