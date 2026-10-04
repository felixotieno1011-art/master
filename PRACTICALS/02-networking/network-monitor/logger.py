"""All logging — text log and CSV log."""
import csv
import os
from datetime import datetime

import config


def ensure_dirs():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)


def session_start(isp, conn):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(config.LOG_TXT, "a") as f:
        f.write(f"\n{'=' * 60}\n")
        f.write(f"SESSION STARTED: {ts} [{conn}]\n")
        f.write(f"{'=' * 60}\n")
        if "error" in isp:
            f.write(f"ISP detection failed: {isp['error']}\n")
        else:
            f.write(f"ISP:        {isp['isp']}\n")
            f.write(f"Location:   {isp['city']}, {isp['region']}, {isp['country']}\n")
            f.write(f"Public IP:  {isp['ip']}\n")
            f.write(f"Connection: {conn}\n")
        f.write("\n")


def run_txt(conn, isp_name, results):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(config.LOG_TXT, "a") as f:
        f.write(f"----- {ts} [{conn}] [{isp_name}] -----\n")
        for label, stats in results["pings"].items():
            if stats["avg"] is None:
                f.write(f"{label}: FAILED\n")
            else:
                f.write(
                    f"{label}: {stats['avg']:.0f} ms | "
                    f"loss {stats['loss']:.1f}% | "
                    f"jitter {stats['jitter'] or 0:.0f} ms\n"
                )
        dl = results.get("download")
        ul = results.get("upload")
        f.write(f"Download: {'FAILED' if dl is None else f'{dl:.2f} Mbps'}\n")
        f.write(f"Upload:   {'FAILED' if ul is None else f'{ul:.2f} Mbps'}\n")

        dns = results.get("dns")
        if dns:
            f.write(f"DNS system:   {dns['system']} ms\n")
            for k, v in dns["servers"].items():
                f.write(f"DNS {k}: {v} ms\n")

        http = results.get("http")
        if http:
            for site, r in http.items():
                f.write(f"HTTP {site}: status={r.get('status')} ttfb={r.get('ttfb_ms')} ms\n")

        f.write("\n")


def run_csv(conn, isp_name, results):
    file_exists = os.path.exists(config.LOG_CSV)
    with open(config.LOG_CSV, "a", newline="") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow([
                "timestamp", "conn", "isp",
                "google_avg", "google_loss", "google_jitter",
                "cloudflare_avg", "quad9_avg", "opendns_avg",
                "download_mbps", "upload_mbps",
                "dns_default_ms", "dns_google_ms", "dns_cloudflare_ms",
                "http_google_ttfb", "http_cloudflare_ttfb", "http_wikipedia_ttfb",
            ])
        p = results["pings"]

        def g(key, field):
            return p.get(key, {}).get(field)

        dns = results.get("dns") or {}
        dns_srv = dns.get("servers") or {}

        http = results.get("http") or {}

        def http_ttfb(site):
            r = http.get(site) or {}
            return r.get("ttfb_ms")

        w.writerow([
            datetime.now().isoformat(),
            conn, isp_name,
            g("Google DNS", "avg"), g("Google DNS", "loss"), g("Google DNS", "jitter"),
            g("Cloudflare", "avg"),
            g("Quad9", "avg"),
            g("OpenDNS", "avg"),
            results.get("download"), results.get("upload"),
            dns.get("system"),
            dns_srv.get("Google"),
            dns_srv.get("Cloudflare"),
            http_ttfb("Google"),
            http_ttfb("Cloudflare"),
            http_ttfb("Wikipedia"),
        ])
