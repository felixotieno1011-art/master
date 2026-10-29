"""Global search — matches the top-bar 'Search' box of the real console.

Searches:
  - Service names, IDs, descriptions (as before)
  - Your resources by ID or name (buckets, instances, VPCs, users, tables,
    functions, alarms, log groups) — real AWS does this too.
"""
from core.webui import aws_ref


def find_services(q):
    """Match on service id / name / description. Returns (matches, exact)."""
    if not q:
        return [], None
    needle = q.strip().lower()
    if not needle:
        return [], None

    matches = []
    exact = None
    for sid, name, desc, href in aws_ref.SERVICES:
        hay = f"{sid} {name} {desc}".lower()
        if name.lower() == needle or sid.lower() == needle:
            exact = (sid, name, desc, href)
        if needle in hay:
            matches.append((sid, name, desc, href))

    if exact and matches and matches[0] != exact:
        matches = [exact] + [m for m in matches if m != exact]
    return matches, exact


def find_resources(q):
    """Return a list of (resource_type, label, href, sublabel) tuples.

    Each tuple:
      resource_type: 'S3 bucket', 'EC2 instance', 'VPC', 'IAM user',
                     'DynamoDB table', 'Lambda function', 'CloudWatch alarm',
                     'Log group'
      label: the matched value (name, ID, etc.)
      href: link to open the resource
      sublabel: extra context (region, state, etc.) or ''
    """
    if not q:
        return []
    needle = q.strip().lower()
    if not needle:
        return []

    results = []

    # S3 buckets
    try:
        from core import s3 as s3_mod
        for b in s3_mod.ls_buckets() or []:
            name = b.get("name", "")
            if needle in name.lower():
                results.append((
                    "S3 bucket", name, f"/s3/{name}",
                    b.get("region", ""),
                ))
    except Exception:
        pass

    # EC2 instances
    try:
        from core import ec2 as ec2_mod
        for i in ec2_mod.list_all() or []:
            name = (i.get("tags") or {}).get("Name") or ""
            iid = i.get("instance_id") or ""
            if needle in name.lower() or needle in iid.lower():
                results.append((
                    "EC2 instance", name or iid, f"/ec2/instances/{iid}",
                    i.get("state", "") + " · " + i.get("region", ""),
                ))
    except Exception:
        pass

    # VPCs
    try:
        from core import vpc as vpc_mod
        for v in vpc_mod.list_vpcs() or []:
            vid = v.get("vpcId", "")
            vname = (v.get("tags") or {}).get("Name", "")
            if needle in vid.lower() or needle in vname.lower():
                results.append((
                    "VPC", vid, f"/vpc/{vid}",
                    v.get("cidrBlock", "") + " · " + v.get("region", ""),
                ))
    except Exception:
        pass

    # IAM users
    try:
        from core import iam as iam_mod
        for u in iam_mod.list_users() or []:
            uname = u.get("userName", "")
            if needle in uname.lower():
                results.append((
                    "IAM user", uname, f"/iam/users/{uname}", "identity",
                ))
    except Exception:
        pass

    # DynamoDB tables
    try:
        from core import dynamodb as ddb
        for t in ddb.list_tables() or []:
            tn = t.get("TableName", "")
            if needle in tn.lower():
                results.append((
                    "DynamoDB table", tn, f"/dynamodb/tables/{tn}",
                    f"{t.get('ItemCount', 0)} items",
                ))
    except Exception:
        pass

    # Lambda functions
    try:
        from core import lambda_svc as lam
        for f in lam.list_functions() or []:
            fn = f.get("FunctionName", "")
            if needle in fn.lower():
                results.append((
                    "Lambda function", fn, f"/lambda/functions/{fn}",
                    f.get("Runtime", ""),
                ))
    except Exception:
        pass

    # CloudWatch alarms
    try:
        from core import cloudwatch as cw
        for a in cw.list_alarms() or []:
            an = a.get("alarmName", "")
            if needle in an.lower():
                results.append((
                    "CloudWatch alarm", an, f"/cloudwatch/alarms/{an}",
                    a.get("stateValue", ""),
                ))
    except Exception:
        pass

    # Log groups
    try:
        from core import cloudwatch as cw
        for g in cw.describe_log_groups() or []:
            gn = g.get("log_group") or g.get("logGroupName") or g.get("name", "")
            if gn and needle in gn.lower():
                results.append((
                    "Log group", gn, f"/cloudwatch/log-groups/{gn}",
                    "logs",
                ))
    except Exception:
        pass

    return results


def find(q):
    """Legacy API — returns (matches, exact) for services only."""
    return find_services(q)
