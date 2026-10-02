"""Compute plain-English verdict from test results."""
import config


def compute(conn, gateway_stats, near_stats, download):
    """
    Return (level, message).
    level is 'ok', 'warn', or 'critical'.
    """
    # 1. Packet loss — highest priority
    for name, s in near_stats.items():
        if s["loss"] and s["loss"] > config.LOSS_MODERATE:
            return ("critical",
                    f"PACKET LOSS on {name} ({s['loss']:.1f}%) — connection unstable")

    # 2. Speed
    if download is not None and download < config.SPEED_MODERATE:
        return ("critical",
                f"SLOW DOWNLOAD ({download:.2f} Mbps) — unusable for streaming")

    # 3. ISP gateway
    if gateway_stats and gateway_stats["avg"] is not None:
        if gateway_stats["avg"] > 100:
            return ("critical",
                    f"ISP GATEWAY SLOW ({gateway_stats['avg']:.0f} ms) — ISP-side problem")
        if gateway_stats["avg"] > 50:
            return ("warn",
                    f"ISP gateway moderate ({gateway_stats['avg']:.0f} ms)")

    # 4. Latency to near targets
    avgs = [s["avg"] for s in near_stats.values() if s["avg"] is not None]
    if not avgs:
        return ("critical", "ALL TARGETS UNREACHABLE — no internet")

    avg = sum(avgs) / len(avgs)
    if avg < config.LATENCY_GOOD:
        return ("ok", f"HEALTHY (avg {avg:.0f} ms to major DNS)")
    if avg < config.LATENCY_MODERATE:
        return ("warn", f"MODERATE (avg {avg:.0f} ms — usable but not great)")
    return ("critical", f"SLOW (avg {avg:.0f} ms — ISP-side degradation)")
