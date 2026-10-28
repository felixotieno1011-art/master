#!/usr/bin/env python3
"""WebUI launcher — AWS-faithful browser layer. Old console (:7000) untouched."""
import sys
from core.webui import server


def main(argv):
    if len(argv) < 2 or argv[1] not in ("serve",):
        print("usage: python3 webui.py serve")
        print("  serve  — HTTP server on http://localhost:7001")
        return 1
    if argv[1] == "serve":
        server.serve()
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
