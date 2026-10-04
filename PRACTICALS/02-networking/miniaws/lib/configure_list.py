import sys
import os
from pathlib import Path

proj = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(proj))

from core import account

cfg = account._read_aws_config()

# Build rows
rows = []
for k in ("region", "output"):
    v = cfg.get(k, "(not set)")
    rows.append((k, v, "config"))

creds_path = os.path.expanduser("~/.aws/credentials")
if os.path.isfile(creds_path):
    with open(creds_path) as f:
        for line in f:
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip()
            if k in ("aws_access_key_id", "aws_secret_access_key"):
                if "secret" in k and len(v) > 8:
                    v = v[:4] + "****" + v[-4:]
                rows.append((k, v, "credentials"))

# Print with fixed columns
print("      {:<24}{:<24}{:<12}".format("Name", "Value", "Type"))
print("      {:<24}{:<24}{:<12}".format("-"*23, "-"*23, "-"*11))
for name, value, source in rows:
    print("      {:<24}{:<24}{:<12}".format(name, value, source))
