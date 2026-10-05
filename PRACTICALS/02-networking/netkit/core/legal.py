# ============================================
# NETKIT — core/legal.py
# First-run consent. Protects you and your customers.
# ============================================

import os
from . import config

DISCLAIMER = """
============================================================
  NETKIT — LEGAL NOTICE
============================================================

NETKIT performs active network probing (ping, port scan,
traceroute, firewall checks). Running these against networks
you do NOT own or have WRITTEN PERMISSION to test is illegal
in most countries and may violate computer-misuse laws.

By continuing, you confirm that:
  - You own the network, OR
  - You have explicit written permission from the owner.

Type  I AGREE  to continue, or press Ctrl+C to exit.
============================================================
"""


def has_consent():
    return os.path.exists(config.CONSENT_FILE)


def ask_consent():
    if has_consent():
        return True
    print(DISCLAIMER)
    answer = input("> ").strip()
    if answer == "I AGREE":
        with open(config.CONSENT_FILE, "w") as f:
            f.write("consent given\n")
        print("✅ Consent recorded. This message won't show again.\n")
        return True
    print("❌ Consent not given. Exiting.")
    return False
