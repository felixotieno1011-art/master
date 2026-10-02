"""Small helpers: colors, formatting, timing."""
import time

# ANSI colors (work in Termux and Linux terminals)
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
GRAY   = "\033[90m"

def color_for_latency(ms):
    """Return ANSI color code based on latency."""
    if ms is None:
        return RED
    if ms < 100:
        return GREEN
    if ms < 200:
        return YELLOW
    return RED

def color_for_loss(pct):
    if pct is None or pct > 5:
        return RED
    if pct > 1:
        return YELLOW
    return GREEN

def color_for_speed(mbps):
    if mbps is None:
        return RED
    if mbps >= 5:
        return GREEN
    if mbps >= 2:
        return YELLOW
    return RED

def fmt_ms(ms):
    """Format milliseconds or 'FAIL'."""
    if ms is None:
        return f"{RED}FAIL{RESET}"
    color = color_for_latency(ms)
    return f"{color}{ms:.0f} ms{RESET}"

def fmt_loss(pct):
    if pct is None:
        return f"{RED}FAIL{RESET}"
    color = color_for_loss(pct)
    return f"{color}{pct:.1f}%{RESET}"

def fmt_mbps(mbps):
    if mbps is None:
        return f"{RED}FAIL{RESET}"
    color = color_for_speed(mbps)
    return f"{color}{mbps:.2f} Mbps{RESET}"

def hr(char="─", width=60):
    return char * width

def section(title):
    print()
    print(f"{BOLD}{BLUE}{title}{RESET}")
    print(hr())

def timer_start():
    return time.time()

def timer_elapsed(start):
    return time.time() - start
