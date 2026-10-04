"""Global settings for MiniAWS."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")

# Default region (like AWS CLI's ~/.aws/config)
DEFAULT_REGION = "us-east-1"

# Real AWS regions (a subset)
REGIONS = {
    "us-east-1":      "US East (N. Virginia)",
    "us-west-2":      "US West (Oregon)",
    "eu-west-1":      "Europe (Ireland)",
    "eu-central-1":   "Europe (Frankfurt)",
    "af-south-1":     "Africa (Cape Town)",
    "ap-southeast-1": "Asia Pacific (Singapore)",
    "ap-southeast-2": "Asia Pacific (Sydney)",
    "ap-northeast-1": "Asia Pacific (Tokyo)",
}

# EC2 instance types (like AWS's t3.micro, t3.small, etc.)
INSTANCE_TYPES = {
    "t3.nano":   {"vcpus": 1, "memory_mb": 512,    "disk_gb": 20},
    "t3.micro":  {"vcpus": 2, "memory_mb": 1024,   "disk_gb": 30},
    "t3.small":  {"vcpus": 2, "memory_mb": 2048,   "disk_gb": 50},
    "t3.medium": {"vcpus": 2, "memory_mb": 4096,   "disk_gb": 80},
    "t3.large":  {"vcpus": 2, "memory_mb": 8192,   "disk_gb": 120},
}

# Bucket name rules (AWS-specific: globally unique, no underscores)
BUCKET_NAME_MIN = 3
BUCKET_NAME_MAX = 63

# Paths
CONFIG_FILE = os.path.join(STATE_DIR, "config.json")
