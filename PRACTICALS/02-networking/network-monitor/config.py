"""All settings for the network monitor live here."""

# ---- Test targets ----
TARGETS_NEAR = {
    "Google DNS": "8.8.8.8",
    "Cloudflare": "1.1.1.1",
    "Quad9":      "9.9.9.9",
}

TARGETS_FAR = {
    "OpenDNS": "208.67.222.222",
}

# ---- Ping settings ----
PING_COUNT   = 5
PING_TIMEOUT = 3

# ---- Speed test settings ----
SPEED_DOWNLOAD_URL = "http://speedtest.tele2.net/10MB.zip"
SPEED_UPLOAD_URL   = "http://speedtest.tele2.net/upload.php"
SPEED_TIMEOUT      = 60

# ---- Thresholds (ms) ----
LATENCY_GOOD     = 100
LATENCY_MODERATE = 200

LOSS_GOOD     = 1.0
LOSS_MODERATE = 5.0

JITTER_GOOD     = 30
JITTER_MODERATE = 80

SPEED_GOOD     = 5.0
SPEED_MODERATE = 2.0

# ---- DNS thresholds (ms) ----
DNS_GOOD     = 50
DNS_MODERATE = 150

# ---- HTTP thresholds (ms) ----
HTTP_TTFB_GOOD     = 500
HTTP_TTFB_MODERATE = 1500

# ---- Feature toggles ----
ENABLE_DNS       = True
ENABLE_PORTS     = True
ENABLE_HTTP      = True
ENABLE_TRACEROUTE = True   # uses traceroute (first 5 hops)

# ---- Paths ----
LOG_TXT  = "logs/network_log.txt"
LOG_CSV  = "logs/network_log.csv"
REPORT   = "reports/report.html"

# ---- Web server ----
WEB_PORT = 5000
