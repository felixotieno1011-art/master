#!/usr/bin/env python3
"""aws sts — real AWS CLI shape for get-caller-identity."""
import json
import sys

from core import account
from core import iam as iam_mod


def _identity():
    """Return (UserId, Account, Arn) in the shape real AWS uses."""
    account_id = account.get_account_id() or "000000000000"
    try:
        current = iam_mod.get_current_user()
    except Exception:
        current = None

    if not current or str(current).lower() == "root":
        # Root ARN — no user/ prefix
        user_id = account_id
        arn = f"arn:aws:iam::{account_id}:root"
    else:
        user_id = f"AIDA{account_id}:{current}"
        arn = f"arn:aws:iam::{account_id}:user/{current}"

    return user_id, account_id, arn


def cmd_get_caller_identity(args):
    """Match `aws sts get-caller-identity` output exactly."""
    # Parse --output flag (also accepted as global flag by wrapper, but we
    # handle it here so the command works standalone too)
    output_mode = "json"
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--output" and i + 1 < len(args):
            output_mode = args[i + 1]
            i += 2
        elif a.startswith("--output="):
            output_mode = a.split("=", 1)[1]
            i += 1
        else:
            i += 1

    user_id, account_id, arn = _identity()

    if output_mode == "text":
        # Real AWS: `--output text` prints tab-separated: UserId\tAccount\tArn
        print(f"{user_id}\t{account_id}\t{arn}")
        return 0

    if output_mode == "table":
        print("----------------------------------------------")
        print("|       GetCallerIdentity                    |")
        print("+---------+--------------+-------------------+")
        print("|  Account|  UserId       |  Arn              |")
        print("+---------+--------------+-------------------+")
        print(f"|  {account_id} |  {user_id} |  {arn} |")
        print("+---------+--------------+-------------------+")
        return 0

    # Default: JSON (real AWS shape)
    print(json.dumps({
        "UserId": user_id,
        "Account": account_id,
        "Arn": arn,
    }, indent=4))
    return 0


def main(argv):
    if len(argv) < 2:
        print("usage: aws sts <command>")
        print("  get-caller-identity   Return details about the IAM user or role")
        return 1
    sub = argv[1]
    rest = argv[2:]

    if sub == "get-caller-identity":
        return cmd_get_caller_identity(rest)

    print(f"❌ aws sts: unknown command: {sub}")
    print("Try: get-caller-identity")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
