#!/usr/bin/env python3
# ============================================
# NETKIT v2.0 — All-in-one networking toolkit
# Usage:
#   python netkit.py            → terminal UI
#   python netkit.py --web      → browser UI
#   python netkit.py --web --open → browser UI + auto-open
# ============================================

import sys
from core import legal, config


def main():
    args = sys.argv[1:]

    if not legal.ask_consent():
        sys.exit(1)

    if "--web" in args:
        from ui.web import server
        if "--open" in args:
            _open_browser_later()
        server.start()
    else:
        from ui.terminal import menu
        menu.loop()


def _open_browser_later():
    """Open the browser after a short delay so the server is ready."""
    import threading, webbrowser, shutil, subprocess

    url = f"http://{config.WEB_HOST}:{config.WEB_PORT}"

    def opener():
        import time
        time.sleep(1.2)
        # Termux has termux-open-url; fall back to webbrowser module
        if shutil.which("termux-open-url"):
            subprocess.run(["termux-open-url", url], check=False)
        else:
            webbrowser.open(url)

    threading.Thread(target=opener, daemon=True).start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user.")
