# Network Monitor

A cross-platform network diagnostic tool. Runs on Termux (Android) and Linux.
Uses only Python's standard library — no pip installs needed.

## What it measures

- ISP info (name, location, public IP)
- Connection type (WiFi / Mobile)
- ISP gateway reachability
- Latency to public DNS servers
- Packet loss %
- Jitter (latency variation)
- Download speed (Mbps)
- Upload speed (Mbps)

## Outputs

- Terminal (pretty, color-coded)
- `logs/network_log.txt` — human-readable log
- `logs/network_log.csv` — machine-readable data
- `reports/report.html` — browser-viewable report

## Files

| File | Purpose |
|------|---------|
| `config.py`        | All settings (targets, timeouts, thresholds) |
| `utils.py`         | Colors, formatting, small helpers |
| `detect.py`        | ISP, connection type, gateway detection |
| `ping.py`          | Latency, packet loss, jitter |
| `speed.py`         | Download and upload speed |
| `monitor.py`       | Main script — runs the test, logs results |
| `report.py`        | Reads logs, produces terminal + HTML report |
| `web_server.py`    | Serves the HTML report live in browser |
| `run_monitor.sh`   | Runs monitor.py N times with pauses |

## Quick start

    python monitor.py                # run a test
    python report.py                 # view report in terminal
    python report.py --html          # generate HTML report
    python web_server.py             # live browser view
    bash run_monitor.sh 10 5         # 10 runs, 5s pause

## Requirements

- Python 3.7+
- `ping` command (built-in on Termux and Linux)
- `curl` command (built-in on Termux and Linux)

No other dependencies.
