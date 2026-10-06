#!/usr/bin/env python3
"""Availability Zones CLI."""
import sys
import utils
from core import az
from core import account


def cmd_list(args):
    """List AZs for the current region."""
    region = account.get_region()
    azs = az.get_az_details(region)

    # Check for --output json
    output_json = "--output" in args and "json" in args

    if output_json:
        import json
        print(json.dumps({"AvailabilityZones": azs}, indent=2))
        return 0

    # Table output
    print_row(["ZONE NAME", "STATE", "REGION", "TYPE"],
              [20, 12, 15, 20])
    print("-" * 67)
    for z in azs:
        print_row([z["ZoneName"], z["State"], z["RegionName"], z["ZoneType"]],
                  [20, 12, 15, 20])
    return 0


def print_row(cells, widths):
    print(" ".join(str(c).ljust(w) for c, w in zip(cells, widths)))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(cmd_list([]))
    sub = sys.argv[1]
    args = sys.argv[2:]
    if sub == "list":
        sys.exit(cmd_list(args))
    # Default: no subcommand means list
    sys.exit(cmd_list(sys.argv[1:]))
