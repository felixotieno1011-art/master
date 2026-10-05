# ============================================
# NETKIT — core/config.py
# Central configuration. No logic here, just values.
# ============================================

VERSION = "2.0.0"
APP_NAME = "NETKIT"
APP_TAGLINE = "Your all-in-one networking toolkit"
AUTHOR = "NETKIT"
YEAR = "2026"

# --- Paths ---
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# --- Network defaults ---
PING_COUNT = 4
PING_TIMEOUT = 2
PING_TOTAL_TIMEOUT = 15

TRACEROUTE_MAX_HOPS = 5
TRACEROUTE_TIMEOUT = 2
TRACEROUTE_TOTAL_TIMEOUT = 30

PORT_TIMEOUT = 2

COMMON_PORTS = [22, 80, 443, 21, 25, 3306, 8080]

FIREWALL_PORTS = {
    22: "SSH",
    80: "HTTP",
    443: "HTTPS",
    3306: "MySQL",
    5432: "PostgreSQL",
}

# --- IDS ---
IDS_SCAN_THRESHOLD = 5

# --- Web UI ---
WEB_HOST = "127.0.0.1"
WEB_PORT = 8000

# --- Legal ---
CONSENT_FILE = os.path.join(BASE_DIR, ".netkit_consent")
