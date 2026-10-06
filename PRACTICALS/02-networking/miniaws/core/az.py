"""Availability Zones — MiniAWS's list of AZs per region."""

# Each region has 3-6 AZs (lettered a, b, c, ...)
REGION_AZ_COUNT = {
    "us-east-1": 6,
    "us-west-2": 4,
    "eu-west-1": 3,
    "eu-central-1": 3,
    "af-south-1": 3,
    "ap-southeast-1": 3,
    "ap-southeast-2": 3,
    "ap-northeast-1": 4,
}


def list_azs(region):
    """Return a list of AZ names for the given region."""
    count = REGION_AZ_COUNT.get(region, 3)   # default to 3
    return [f"{region}{chr(ord('a') + i)}" for i in range(count)]


def get_az_details(region):
    """Return AZ names with extra fields like real AWS."""
    names = list_azs(region)
    out = []
    for name in names:
        out.append({
            "ZoneName": name,
            "State": "available",
            "RegionName": region,
            "ZoneType": "availability-zone",
        })
    return out
