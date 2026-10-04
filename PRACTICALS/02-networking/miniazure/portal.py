#!/usr/bin/env python3
"""Portal CLI — generate or serve the dashboard."""
import sys
import utils
from core import portal, portal_server


def main():
    args = sys.argv[1:]
    if not args or args[0] not in ("generate", "serve"):
        print("usage: python portal.py generate|serve")
        print("  generate  — write reports/portal.html")
        print("  serve     — serve on http://localhost:9090")
        return 1

    sub = args[0]
    if sub == "generate":
        path = portal.write_dashboard("reports/portal.html")
        print(utils.ok(f"dashboard written: {path}"))
        print(f"   Open: termux-open {path}")
        return 0
    if sub == "serve":
        portal_server.serve()
        return 0


if __name__ == "__main__":
    sys.exit(main())
