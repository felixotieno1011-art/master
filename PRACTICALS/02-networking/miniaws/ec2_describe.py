#!/usr/bin/env python3
"""aws ec2 describe-* — read-only info commands matching real AWS shapes.

Covers the four commands every EC2 tutorial starts with:
  describe-images
  describe-instance-types
  describe-key-pairs
  describe-availability-zones

Output shape: real AWS JSON. All commands support --output json|text|table,
and default to JSON (matching real AWS CLI v2 behavior).
"""
import json
import sys

import config
from core import account


# ---- Fake-but-realistic AMI catalog ----
AMIS = [
    {
        "ImageId": "ami-0c101f26f147fa7fd",
        "Name": "al2023-ami-2023.3.20231010.0-kernel-6.1-x86_64",
        "Description": "Amazon Linux 2023 AMI 2023.3.20231010.0 x86_64 HVM kernel-6.1",
        "State": "available",
        "OwnerId": "137112412989",
        "CreationDate": "2023-10-10T20:42:31.000Z",
        "PlatformDetails": "Linux/UNIX",
        "Architecture": "x86_64",
        "RootDeviceType": "ebs",
        "RootDeviceName": "/dev/xvda",
        "VirtualizationType": "hvm",
        "Public": True,
    },
    {
        "ImageId": "ami-0d5f4b1a3c9e2a5b6",
        "Name": "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-20231011",
        "Description": "Canonical, Ubuntu, 22.04 LTS, amd64 jammy image build on 2023-10-11",
        "State": "available",
        "OwnerId": "099720109477",
        "CreationDate": "2023-10-11T00:00:00.000Z",
        "PlatformDetails": "Linux/UNIX",
        "Architecture": "x86_64",
        "RootDeviceType": "ebs",
        "RootDeviceName": "/dev/sda1",
        "VirtualizationType": "hvm",
        "Public": True,
    },
    {
        "ImageId": "ami-0a1b2c3d4e5f67890",
        "Name": "Windows_Server-2022-English-Full-Base-2023.10.10",
        "Description": "Microsoft Windows Server 2022 Full Locale English AMI provided by Amazon",
        "State": "available",
        "OwnerId": "801119661308",
        "CreationDate": "2023-10-10T12:00:00.000Z",
        "PlatformDetails": "Windows",
        "Architecture": "x86_64",
        "RootDeviceType": "ebs",
        "RootDeviceName": "/dev/sda1",
        "VirtualizationType": "hvm",
        "Public": True,
    },
]


def _output_mode(args):
    """Parse --output {json,text,table} from args. Default 'json'."""
    for i, a in enumerate(args):
        if a == "--output" and i + 1 < len(args):
            return args[i + 1]
        if a.startswith("--output="):
            return a.split("=", 1)[1]
    return "json"


def _flags(args):
    """Simple --key value parser (skips --output and --query for simplicity)."""
    out = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--") and "=" in a:
            k, v = a[2:].split("=", 1)
            out[k] = v
            i += 1
        elif a.startswith("--") and i + 1 < len(args) and not args[i + 1].startswith("--"):
            out[a[2:]] = args[i + 1]
            i += 2
        else:
            i += 1
    return out


def _emit(payload, mode):
    if mode == "json":
        print(json.dumps(payload, indent=4))
    elif mode == "text":
        # Simple tab-separated for one-resource-per-line
        for k, v in payload.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                for item in v:
                    print("\t".join(str(x) for x in item.values()))
            else:
                print(f"{k}\t{v}")
    else:
        print(json.dumps(payload, indent=4))


# ---------------- describe-images ----------------

def cmd_describe_images(args):
    """Match `aws ec2 describe-images` output. Supports --owners filter."""
    flags = _flags(args)
    owner_filter = (flags.get("owners") or "").strip().lower()
    image_ids = (flags.get("image-ids") or "").split(",") if flags.get("image-ids") else []

    images = AMIS
    if image_ids:
        images = [i for i in images if i["ImageId"] in image_ids]

    if owner_filter and owner_filter != "amazon":
        # Amazon-owned images use OwnerId 137112412989
        images = [i for i in images if i["OwnerId"] == "137112412989"]

    _emit({"Images": images}, _output_mode(args))
    return 0


# ---------------- describe-instance-types ----------------

def cmd_describe_instance_types(args):
    """Match `aws ec2 describe-instance-types` output — iterate config.INSTANCE_TYPES."""
    flags = _flags(args)
    filter_type = flags.get("instance-types")
    filter_types = filter_type.split(",") if filter_type else None

    out = []
    for name, spec in config.INSTANCE_TYPES.items():
        if filter_types and name not in filter_types:
            continue
        out.append({
            "InstanceType": name,
            "CurrentGeneration": True,
            "FreeTierEligible": name in ("t3.micro", "t2.micro"),
            "SupportedUsageClasses": ["on-demand", "spot"],
            "SupportedRootDeviceTypes": ["ebs"],
            "SupportedVirtualizationTypes": ["hvm"],
            "BareMetal": False,
            "Hypervisor": "nitro",
            "ProcessorInfo": {
                "SupportedArchitectures": ["x86_64"],
                "SustainedClockSpeedInGhz": 3.1,
            },
            "VCpuInfo": {
                "DefaultVCpus": spec["vcpus"],
                "DefaultCores": spec["vcpus"],
                "DefaultThreadsPerCore": 1,
            },
            "MemoryInfo": {
                "SizeInMiB": spec["memory_mb"],
            },
            "InstanceStorageSupported": False,
            "EbsInfo": {
                "EbsOptimizedSupport": "supported" if name == "t3.micro" else "unsupported",
                "EncryptionSupport": "supported",
            },
            "NetworkInfo": {
                "NetworkPerformance": "Up to 5 Gigabit" if spec["vcpus"] <= 2 else "Up to 12 Gigabit",
                "MaximumNetworkInterfaces": 3,
                "Ipv4AddressesPerInterface": 6,
            },
        })

    _emit({"InstanceTypes": out}, _output_mode(args))
    return 0


# ---------------- describe-key-pairs ----------------

def cmd_describe_key_pairs(args):
    """Fresh accounts have no key pairs. Returns empty list matching real AWS."""
    _emit({"KeyPairs": []}, _output_mode(args))
    return 0


# ---------------- describe-availability-zones ----------------

def cmd_describe_availability_zones(args):
    """Return availability zones for the current region."""
    region = account.get_region()
    zones = [
        {"ZoneName": f"{region}{suffix}", "State": "available",
         "RegionName": region, "ZoneId": f"{region}-az{suffix}"}
        for suffix in ("a", "b", "c")
    ]
    _emit({"AvailabilityZones": zones}, _output_mode(args))
    return 0


# ---------------- main ----------------

def cmd_describe_volumes(args):
    """Return EBS volumes for all EC2 instances. Real AWS shape."""
    from core import ec2 as ec2_mod
    from core import account

    try:
        instances = ec2_mod.list_all()
    except Exception:
        instances = []

    region = account.get_region()
    acct = account.get_account_id() or "000000000000"

    volumes = []
    for idx, inst in enumerate(instances):
        iid = inst.get("instance_id", "")
        state = (inst.get("state") or "").lower()
        if state == "terminated":
            continue
        itype = inst.get("instance_type", "t3.micro")
        # Approximate volume size from instance type
        spec = config.INSTANCE_TYPES.get(itype, {})
        size = spec.get("disk_gb", 30)
        volumes.append({
            "VolumeId": f"vol-{iid[-17:]}",
            "Size": size,
            "SnapshotId": "",
            "AvailabilityZone": f"{region}a",
            "State": "in-use" if state == "running" else "available",
            "CreateTime": inst.get("launched") or inst.get("created") or "2026-01-01T00:00:00Z",
            "Attachments": [
                {
                    "AttachTime": inst.get("launched") or "2026-01-01T00:00:00Z",
                    "Device": "/dev/xvda",
                    "InstanceId": iid,
                    "State": "attached" if state == "running" else "detached",
                    "DeleteOnTermination": True,
                }
            ] if state == "running" else [],
            "VolumeType": "gp3",
            "Encrypted": True,
            "Iops": 3000,
            "Throughput": 125,
            "MultiAttachEnabled": False,
            "Tags": [
                {"Key": "Name", "Value": (inst.get("tags") or {}).get("Name", "root-volume")},
            ],
        })

    _emit({"Volumes": volumes}, _output_mode(args))
    return 0


COMMANDS = {
    "describe-images": cmd_describe_images,
    "describe-instance-types": cmd_describe_instance_types,
    "describe-key-pairs": cmd_describe_key_pairs,
    "describe-availability-zones": cmd_describe_availability_zones,
    "describe-volumes": cmd_describe_volumes,
}


def main(argv):
    if len(argv) < 2:
        print("usage: aws ec2 <command>")
        print("  " + "\n  ".join(COMMANDS.keys()))
        return 1
    sub = argv[1]
    args = argv[2:]
    fn = COMMANDS.get(sub)
    if fn is None:
        print(f"❌ aws ec2: unknown: {sub}")
        return 1
    return fn(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
