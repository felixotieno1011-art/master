# ============================================
# NETKIT — core/logger.py
# Timestamped report files. Both UIs write here.
# ============================================

import os
import json
from datetime import datetime
from . import config


class Report:
    """One report per NETKIT session. Writes .txt and .json."""

    def __init__(self):
        os.makedirs(config.REPORTS_DIR, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.txt_path = os.path.join(config.REPORTS_DIR, f"netkit_{stamp}.txt")
        self.json_path = os.path.join(config.REPORTS_DIR, f"netkit_{stamp}.json")
        self.entries = []
        self.started = datetime.now()

        with open(self.txt_path, "w") as f:
            f.write(f"{config.APP_NAME} REPORT — {self.started.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

    def log(self, tag, message, data=None):
        """Write one line to txt, and a structured entry to json."""
        line = f"[{tag}] {message}"
        with open(self.txt_path, "a") as f:
            f.write(line + "\n")

        self.entries.append({
            "time": datetime.now().isoformat(timespec="seconds"),
            "tag": tag,
            "message": message,
            "data": data or {},
        })
        self._flush_json()

    def _flush_json(self):
        payload = {
            "app": config.APP_NAME,
            "version": config.VERSION,
            "started": self.started.isoformat(timespec="seconds"),
            "entries": self.entries,
        }
        with open(self.json_path, "w") as f:
            json.dump(payload, f, indent=2)

    def path(self):
        return self.txt_path

    def json(self):
        return self.json_path

    def read(self):
        if os.path.exists(self.txt_path):
            with open(self.txt_path) as f:
                return f.read()
        return ""


# Single shared instance — both UIs use this
_report = None


def get_report():
    global _report
    if _report is None:
        _report = Report()
    return _report
