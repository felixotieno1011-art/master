"""All settings for the network monitor live here."""

# ---- Test targets ----
# Near targets: use these for the verdict (they're geographically close)
TARGETS_NEAR = {
    "Google DNS": "8.8.8.8",
    "Cloudflare": "1.1.1.1",
    "Quad9":      "9.9.9.9",
}

# Far targets: informational only, don't affect verdict
TARGETS_FAR = {
    "OpenDNS": "208.67.222.222",
}

# ---- Ping settings ----
PING_COUNT   = 5      # packets per ping test
PING_TIMEOUT = 3      # seconds per packet

# ---- Speed test settings ----
SPEED_DOWNLOAD_URL = "http://speedtest.tele2.net/10MB.zip"
SPEED_UPLOAD_URL   = "http://speedtest.tele2.net/upload.php"
SPEED_TIMEOUT      = 60   # seconds

# ---- Thresholds (ms) ----
LATENCY_GOOD     = 100
LATENCY_MODERATE = 200

LOSS_GOOD     = 1.0    # %
LOSS_MODERATE = 5.0    # %

JITTER_GOOD     = 30   # ms
JITTER_MODERATE = 80   # ms

SPEED_GOOD     = 5.0   # Mbps
SPEED_MODERATE = 2.0   # Mbps

# ---- Paths ----
LOG_TXT  = "logs/network_log.txt"
LOG_CSV  = "logs/network_log.csv"
REPORT   = "reports/report.html"

# ---- Web server ----
WEB_PORT = 5000
