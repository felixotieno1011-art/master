"""Convert MiniAWS data to AWS-style JSON output."""
import json
import sys
from pathlib import Path

proj = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(proj))

from core import vpc as vpc_mod
from core import ec2 as ec2_mod
from core import s3 as s3_mod
from core import iam as iam_mod
from core import cloudwatch as cw_mod
from core import account as account_mod


def describe_vpcs():
    vpcs = vpc_mod.list_vpcs()
    return {
        "Vpcs": [
            {
                "VpcId": v["vpcId"],
                "CidrBlock": v["cidrBlock"],
                "State": v.get("state", "available"),
                "Region": v.get("region"),
                "IsDefault": v.get("isDefault", False),
            }
            for v in vpcs
        ]
    }


def describe_subnets():
    subnets = vpc_mod.list_subnets()
    return {
        "Subnets": [
            {
                "SubnetId": s["subnetId"],
                "VpcId": s["vpcId"],
                "CidrBlock": s["cidrBlock"],
                "AvailabilityZone": s.get("availabilityZone"),
                "State": s.get("state", "available"),
                "Tags": [
                    {"Key": k, "Value": v}
                    for k, v in (s.get("tags") or {}).items()
                ],
            }
            for s in subnets
        ]
    }


def describe_internet_gateways():
    igws = vpc_mod.list_internet_gateways()
    return {
        "InternetGateways": [
            {
                "InternetGatewayId": g["internetGatewayId"],
                "Attachments": [
                    {"VpcId": vpc_id, "State": "available"}
                    for vpc_id in g.get("attachments", [])
                ],
            }
            for g in igws
        ]
    }


def describe_route_tables():
    rts = vpc_mod.list_route_tables()
    return {
        "RouteTables": [
            {
                "RouteTableId": rt["routeTableId"],
                "VpcId": rt["vpcId"],
                "Routes": [
                    {
                        "DestinationCidrBlock": r["destinationCidrBlock"],
                        "GatewayId": r["gatewayId"],
                        "State": r.get("state", "active"),
                    }
                    for r in rt.get("routes", [])
                ],
            }
            for rt in rts
        ]
    }


def describe_instances():
    instances = ec2_mod.list_all()
    return {
        "Reservations": [
            {
                "Instances": [
                    {
                        "InstanceId": i["instance_id"],
                        "InstanceType": i["instance_type"],
                        "State": {"Name": i.get("state")},
                        "Region": i.get("region"),
                        "Tags": [
                            {"Key": k, "Value": v}
                            for k, v in (i.get("tags") or {}).items()
                        ],
                    }
                    for i in instances
                ]
            }
        ]
    }



def describe_availability_zones():
    from core import az, account
    region = account.get_region()
    return {"AvailabilityZones": az.get_az_details(region)}

def list_buckets():
    buckets = s3_mod.ls_buckets()
    return {
        "Buckets": [
            {
                "Name": b["name"],
                "CreationDate": b.get("created"),
                "Region": b.get("region"),
            }
            for b in buckets
        ]
    }


def list_users():
    users = iam_mod.list_users()
    return {
        "Users": [
            {
                "UserName": u["userName"],
                "Arn": u["arn"],
                "CreateDate": u.get("created"),
            }
            for u in users
        ]
    }


def list_alarms():
    alarms = cw_mod.list_alarms()
    return {
        "MetricAlarms": [
            {
                "AlarmName": a["alarmName"],
                "MetricName": a["metricName"],
                "Namespace": a["namespace"],
                "StateValue": a["stateValue"],
                "StateReason": a.get("stateReason", ""),
                "Threshold": a["threshold"],
                "ComparisonOperator": a["comparisonOperator"],
            }
            for a in alarms
        ]
    }


# Dispatch table
HANDLERS = {
    "describe-vpcs": describe_vpcs,
    "describe-availability-zones": describe_availability_zones,
    "describe-subnets": describe_subnets,
    "describe-internet-gateways": describe_internet_gateways,
    "describe-route-tables": describe_route_tables,
    "describe-instances": describe_instances,
    "list-buckets": list_buckets,
    "list-users": list_users,
    "list-alarms": list_alarms,
}


def main():
    if len(sys.argv) < 2:
        print("usage: json_output.py <command>")
        sys.exit(1)
    cmd = sys.argv[1]
    handler = HANDLERS.get(cmd)
    if not handler:
        print(f"❌ no JSON handler for: {cmd}", file=sys.stderr)
        sys.exit(1)
    result = handler()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
