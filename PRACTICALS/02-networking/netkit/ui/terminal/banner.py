# ============================================
# NETKIT — ui/terminal/banner.py
# ============================================

import sys
from core import config


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"


def _color_enabled():
    """Disable colors when piped to a file."""
    return sys.stdout.isatty()


def paint(text, color):
    if not _color_enabled():
        return text
    return f"{color}{text}{C.RESET}"


def print_banner():
    line = "=" * 52
    print()
    print(paint(line, C.CYAN + C.BOLD))
    print(paint(f"  🛠️  {config.APP_NAME} v{config.VERSION}", C.CYAN + C.BOLD))
    print(paint(f"  {config.APP_TAGLINE}", C.CYAN))
    print(paint(f"  © {config.YEAR} {config.AUTHOR}", C.DIM))
    print(paint(line, C.CYAN + C.BOLD))
    print()
