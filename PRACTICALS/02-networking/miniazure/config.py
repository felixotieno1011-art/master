"""Settings for MiniAzure."""
import os

# Where we store state (like Azure's control plane database)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")
GROUPS_DIR = os.path.join(STATE_DIR, "groups")

# Default values (mirror Azure defaults)
DEFAULT_REGION = "eastus"
DEFAULT_GROUP = None   # must be specified per command

# Valid regions (subset of Azure's real regions)
VALID_REGIONS = [
    "eastus", "westus", "westeurope", "northeurope",
    "southafricanorth", "eastasia", "southeastasia",
]

# Valid resource sizes (subset of Azure's real sizes)
VALID_VM_SIZES = {
    "small":  {"cpu": 1, "ram_mb": 2048,  "disk_gb": 30},
    "medium": {"cpu": 2, "ram_mb": 4096,  "disk_gb": 60},
    "large":  {"cpu": 4, "ram_mb": 8192,  "disk_gb": 120},
}
