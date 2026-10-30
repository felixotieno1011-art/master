"""Fidelity constants — copied to match the real AWS Console.

Tweak here to stay aligned with console.aws.amazon.com. No logic in this file.
"""

# Palette (from real AWS Console, 2024-2025 theme)
COLORS = {
    "header_bg":      "#232f3e",   # Squid Ink
    "header_hover":   "#31465f",
    "header_text":    "#ffffff",
    "accent":         "#ff9900",   # Amazon Orange
    "accent_hover":   "#e88b00",
    "link":           "#0073bb",   # AWS blue
    "link_hover":     "#005a94",
    "bg":             "#ffffff",
    "bg_subtle":      "#fafafa",
    "border":         "#e9ebed",
    "border_strong":  "#d5dbdb",
    "text":           "#16191f",
    "text_muted":     "#687078",
    "success_bg":     "#f2f8f0",  "success_text": "#037f0c",  "success_border": "#7ad17e",
    "error_bg":       "#fdf3f1",  "error_text":   "#d13212",  "error_border":   "#f5b7ab",
    "warn_bg":        "#fff8e6",  "warn_text":    "#b7791f",  "warn_border":    "#f2cd5c",
    "info_bg":        "#f1f8ff",  "info_text":    "#0073bb",
    "pill_running":   "#037f0c",  "pill_running_bg": "#e6f4e7",
    "pill_stopped":   "#b7791f",  "pill_stopped_bg": "#fff4e0",
    "pill_error":     "#d13212",  "pill_error_bg":   "#fbeae7",
}

# Regions in the order the real console's dropdown lists them.
# (region-code, human label) — labels match AWS exactly.
REGIONS = [
    ("us-east-1",      "US East (N. Virginia)"),
    ("us-east-2",      "US East (Ohio)"),
    ("us-west-1",      "US West (N. California)"),
    ("us-west-2",      "US West (Oregon)"),
    ("af-south-1",     "Africa (Cape Town)"),
    ("ap-east-1",      "Asia Pacific (Hong Kong)"),
    ("ap-south-1",     "Asia Pacific (Mumbai)"),
    ("ap-south-2",     "Asia Pacific (Hyderabad)"),
    ("ap-northeast-1", "Asia Pacific (Tokyo)"),
    ("ap-northeast-2", "Asia Pacific (Seoul)"),
    ("ap-northeast-3", "Asia Pacific (Osaka)"),
    ("ap-southeast-1", "Asia Pacific (Singapore)"),
    ("ap-southeast-2", "Asia Pacific (Sydney)"),
    ("ap-southeast-3", "Asia Pacific (Jakarta)"),
    ("ap-southeast-4", "Asia Pacific (Melbourne)"),
    ("ca-central-1",   "Canada (Central)"),
    ("ca-west-1",      "Canada West (Calgary)"),
    ("eu-central-1",   "Europe (Frankfurt)"),
    ("eu-central-2",   "Europe (Zurich)"),
    ("eu-west-1",      "Europe (Ireland)"),
    ("eu-west-2",      "Europe (London)"),
    ("eu-west-3",      "Europe (Paris)"),
    ("eu-north-1",     "Europe (Stockholm)"),
    ("eu-south-1",     "Europe (Milan)"),
    ("eu-south-2",     "Europe (Spain)"),
    ("il-central-1",   "Israel (Tel Aviv)"),
    ("me-south-1",     "Middle East (Bahrain)"),
    ("me-central-1",   "Middle East (UAE)"),
    ("sa-east-1",      "South America (São Paulo)"),
    ("us-gov-west-1",  "AWS GovCloud (US-West)"),
]

# Service catalog — names, ids, and short descriptions as they appear
# in the real "Services" menu.
SERVICES = [
    # (service_id, real_name, one_line_desc, href_path)
    ("s3",         "S3",         "Scalable storage in the cloud",           "/s3"),
    ("ec2",        "EC2",        "Virtual servers in the cloud",            "/ec2"),
    ("dynamodb",   "DynamoDB",   "Managed NoSQL database",                  "/dynamodb"),
    ("lambda",     "Lambda",     "Run code without thinking about servers", "/lambda"),
    ("iam",        "IAM",        "Manage access to AWS resources",          "/iam"),
    ("cloudwatch", "CloudWatch", "Monitor resources and applications",      "/cloudwatch"),
    ("vpc",        "VPC",        "Isolated cloud resources",                "/vpc"),
    ("sts",        "STS",        "Temporary security credentials",          "/sts"),
]

# Left-rail items per service — same order as real AWS console.
SERVICE_NAV = {
    "s3": [
        ("Buckets",              "/s3"),
        ("Batch operations",     "/s3/batch-ops"),
        ("Access points",        "/s3/access-points"),
        ("Object Lambda access points", "/s3/olap"),
    ],
    "ec2": [
        ("Dashboard",            "/ec2"),
        ("Instances",            "/ec2/instances"),
        ("Instance Types",       "/ec2/instance-types"),
        ("Launch Templates",     "/ec2/launch-templates"),
        ("Elastic IPs",          "/ec2/elastic-ips"),
        ("Security Groups",      "/ec2/security-groups"),
        ("Key Pairs",            "/ec2/key-pairs"),
    ],
    "dynamodb": [
        ("Dashboard",            "/dynamodb"),
        ("Tables",               "/dynamodb/tables"),
        ("Backups",              "/dynamodb/backups"),
        ("PartiQL editor",       "/dynamodb/partiql"),
    ],
    "lambda": [
        ("Dashboard",            "/lambda"),
        ("Functions",            "/lambda/functions"),
        ("Layers",               "/lambda/layers"),
    ],
    "iam": [
        ("Dashboard",            "/iam"),
        ("Users",                "/iam/users"),
        ("User groups",          "/iam/groups"),
        ("Roles",                "/iam/roles"),
        ("Policies",             "/iam/policies"),
    ],
    "cloudwatch": [
        ("Overview",             "/cloudwatch"),
        ("Alarms",               "/cloudwatch/alarms"),
        ("Metrics",              "/cloudwatch/metrics"),
        ("Log groups",           "/cloudwatch/log-groups"),
    ],
    "vpc": [
        ("Your VPCs",            "/vpc"),
        ("Subnets",              "/vpc/subnets"),
        ("Route tables",         "/vpc/route-tables"),
        ("Internet gateways",    "/vpc/igws"),
        ("NAT gateways",         "/vpc/nats"),
        ("Security groups",      "/vpc/security-groups"),
    ],
    "sts": [
        ("Get caller identity",  "/sts"),
    ],
}


# ------------------------------------------------------------------
# Real AWS service color palette (from AWS brand guidelines).
# Used for the colored tiles + service icons throughout the console.
# ------------------------------------------------------------------
SERVICE_COLORS = {
    "s3":         {"primary": "#3F8624", "accent": "#1B660F", "bg": "#E8F5E4"},  # green
    "ec2":        {"primary": "#FF9900", "accent": "#C77700", "bg": "#FFF4E0"},  # orange
    "lambda":     {"primary": "#FF9900", "accent": "#ED7100", "bg": "#FFF4E0"},  # orange
    "dynamodb":   {"primary": "#2E27AD", "accent": "#1E1A6E", "bg": "#E8E7F5"},  # blue
    "iam":        {"primary": "#DD344C", "accent": "#A32538", "bg": "#FBE8EB"},  # red
    "cloudwatch": {"primary": "#E7157B", "accent": "#B41062", "bg": "#FCE5F0"},  # pink
    "vpc":        {"primary": "#8C4FFF", "accent": "#6636BF", "bg": "#F0E9FF"},  # purple
    "sts":        {"primary": "#DD344C", "accent": "#A32538", "bg": "#FBE8EB"},  # red
}


def service_color(service_id):
    """Return {primary, accent, bg} for a service ID, or a neutral gray fallback."""
    return SERVICE_COLORS.get(
        service_id,
        {"primary": "#545B64", "accent": "#3A3F46", "bg": "#F1F3F3"},
    )
