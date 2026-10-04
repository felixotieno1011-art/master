"""CloudFormation — AWS's Infrastructure as Code."""
import json
import os
import re

import config
from utils import now_iso, read_json, write_json, ensure_dir


CFN_DIR = os.path.join(config.STATE_DIR, "cfn")


def _parse_yaml(text):
    lines = text.splitlines()
    return _parse_block(lines, 0, 0)[0]


def _indent(line):
    return len(line) - len(line.lstrip())


def _parse_block(lines, start, indent):
    result = {}
    i = start
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.strip().startswith("#"):
            i += 1; continue
        if _indent(raw) < indent: break
        if _indent(raw) > indent:
            i += 1; continue
        stripped = raw.strip()
        if stripped.startswith("- "): break
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip(); value = value.strip()
            if value == "":
                sub, i = _parse_block(lines, i + 1, indent + 1)
                lst, i = _try_list(lines, i, indent + 1)
                result[key] = lst if lst is not None else sub
            else:
                result[key] = _coerce(value); i += 1
        else:
            i += 1
    return result, i


def _try_list(lines, start, indent):
    i = start
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.strip().startswith("#"):
            i += 1; continue
        if _indent(raw) != indent: return None, start
        if raw.strip().startswith("- "):
            items = []
            while i < len(lines):
                r = lines[i]
                if not r.strip() or r.strip().startswith("#"):
                    i += 1; continue
                if _indent(r) != indent or not r.strip().startswith("- "): break
                content = r.strip()[2:].strip()
                if content == "":
                    sub, i = _parse_block(lines, i + 1, indent + 1)
                    items.append(sub)
                elif ":" in content:
                    k, _, v = content.partition(":")
                    item = {k.strip(): _coerce(v.strip())}
                    i += 1
                    sub, i = _parse_block(lines, i, indent + 1)
                    item.update(sub); items.append(item)
                else:
                    items.append(_coerce(content)); i += 1
            return items, i
        return None, start
    return None, start


def _coerce(v):
    v = v.strip()
    if v in ("true", "True"):  return True
    if v in ("false", "False"): return False
    if v in ("null", "~"):      return None
    if re.match(r"^-?\d+$", v):  return int(v)
    if re.match(r"^-?\d+\.\d+$", v): return float(v)
    if v.startswith("'") and v.endswith("'"): return v[1:-1]
    if v.startswith('"') and v.endswith('"'): return v[1:-1]
    return v


REF_RE    = re.compile(r"!Ref\s+(\w+)")
GETATT_RE = re.compile(r"!GetAtt\s+([\w.]+)")


def _resolve_refs(value, refs):
    if isinstance(value, str):
        def sub_ref(m):
            return str(refs.get(m.group(1), m.group(0)))
        def sub_getatt(m):
            path = m.group(1)
            if "." in path:
                name, attr = path.split(".", 1)
                full = f"{name}.{attr}"
                if full in refs:
                    return str(refs[full])
            return m.group(0)
        return GETATT_RE.sub(sub_getatt, REF_RE.sub(sub_ref, value))
    if isinstance(value, dict):
        if "Ref" in value and len(value) == 1:
            name = value["Ref"]
            return refs.get(name, value)
        if "Fn::GetAtt" in value:
            path = value["Fn::GetAtt"]
            if isinstance(path, list) and len(path) == 2:
                full = f"{path[0]}.{path[1]}"
                return refs.get(full, value)
            return value
        return {k: _resolve_refs(v, refs) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_refs(v, refs) for v in value]
    return value


def _create_resource(logical_name, rtype, props, refs):
    """Create a resource and CAPTURE its ID correctly (diff before/after)."""
    props = _resolve_refs(props, refs)

    from core import ec2, s3, vpc
    from core import iam as iam_mod

    # --- VPC ---
    if rtype == "AWS::EC2::VPC":
        cidr = props.get("CidrBlock")
        if not cidr:
            return False, "missing CidrBlock", None, {}
        before = {v["vpcId"] for v in vpc.list_vpcs()}
        ok_, msg = vpc.create_vpc(cidr)
        if not ok_:
            return False, msg, None, {}
        after = vpc.list_vpcs()
        new = next((v for v in after if v["vpcId"] not in before), None)
        vpc_id = new["vpcId"] if new else None
        return True, msg, vpc_id, {"VpcId": vpc_id}

    # --- Subnet ---
    if rtype == "AWS::EC2::Subnet":
        vpc_id = props.get("VpcId")
        cidr = props.get("CidrBlock")
        if not vpc_id or not cidr:
            return False, "missing VpcId or CidrBlock", None, {}
        before = {s["subnetId"] for s in vpc.list_subnets()}
        ok_, msg = vpc.create_subnet(vpc_id, cidr)
        if not ok_:
            return False, msg, None, {}
        after = vpc.list_subnets()
        new = next((s for s in after if s["subnetId"] not in before), None)
        sid = new["subnetId"] if new else None
        az = new.get("availabilityZone") if new else None
        return True, msg, sid, {"SubnetId": sid, "AvailabilityZone": az}

    # --- Internet Gateway ---
    if rtype == "AWS::EC2::InternetGateway":
        before = {g["internetGatewayId"] for g in vpc.list_internet_gateways()}
        ok_, msg = vpc.create_internet_gateway()
        if not ok_:
            return False, msg, None, {}
        after = vpc.list_internet_gateways()
        new = next((g for g in after if g["internetGatewayId"] not in before), None)
        igw_id = new["internetGatewayId"] if new else None
        return True, msg, igw_id, {"InternetGatewayId": igw_id}

    # --- EC2 Instance ---
    if rtype == "AWS::EC2::Instance":
        name = props.get("Name") or logical_name
        itype = props.get("InstanceType", "t3.micro")
        ok_, msg, iid = ec2.create(name, instance_type=itype)
        if not ok_:
            return False, msg, None, {}
        return True, msg, iid, {"InstanceId": iid}

    # --- S3 Bucket ---
    if rtype == "AWS::S3::Bucket":
        name = props.get("BucketName")
        if not name:
            return False, "missing BucketName", None, {}
        ok_, msg = s3.mb_bucket(name)
        if not ok_:
            return False, msg, None, {}
        return True, msg, name, {"BucketName": name, "Arn": f"arn:aws:s3:::{name}"}

    # --- IAM User ---
    if rtype == "AWS::IAM::User":
        name = props.get("UserName")
        if not name:
            return False, "missing UserName", None, {}
        ok_, msg = iam_mod.create_user(name)
        if not ok_:
            return False, msg, None, {}
        return True, msg, name, {"UserName": name}

    return False, f"unsupported resource type: {rtype}", None, {}


def _stack_path(stack_name):
    return os.path.join(CFN_DIR, "stacks", f"{stack_name}.json")


def _load_template(path):
    with open(path) as f:
        text = f.read()
    if text.lstrip().startswith("{"):
        return json.loads(text)
    return _parse_yaml(text)


def deploy(stack_name, template_path):
    if not os.path.exists(template_path):
        return False, {"error": f"template not found: {template_path}"}
    try:
        template = _load_template(template_path)
    except Exception as e:
        return False, {"error": f"failed to parse template: {e}"}

    resources = template.get("Resources") or {}
    if not resources:
        return False, {"error": "template has no Resources"}

    ensure_dir(os.path.join(CFN_DIR, "stacks"))

    refs = {}
    details = []
    created = 0; failed = 0

    for logical, spec in resources.items():
        rtype = spec.get("Type")
        props = spec.get("Properties") or {}
        ok_, msg, phys_id, outputs = _create_resource(logical, rtype, props, refs)
        if ok_:
            refs[logical] = phys_id
            for k, v in outputs.items():
                refs[f"{logical}.{k}"] = v
            created += 1
            details.append((logical, rtype, "CREATE_COMPLETE", phys_id, msg))
        else:
            failed += 1
            details.append((logical, rtype, "CREATE_FAILED", None, msg))

    stack = {
        "StackName": stack_name,
        "StackId": f"arn:aws:cloudformation:local:stack/{stack_name}",
        "CreatedTime": now_iso(),
        "StackStatus": "CREATE_COMPLETE" if failed == 0 else "CREATE_FAILED",
        "TemplateFile": template_path,
        "Resources": {
            logical: {"Type": spec.get("Type"), "PhysicalId": refs.get(logical)}
            for logical, spec in resources.items()
        },
        "Outputs": {k: str(refs.get(k, "")) for k in refs if "." not in k},
    }
    write_json(_stack_path(stack_name), stack)
    return (failed == 0), {
        "stack": stack_name, "status": stack["StackStatus"],
        "created": created, "failed": failed, "details": details,
    }


def list_stacks():
    ensure_dir(os.path.join(CFN_DIR, "stacks"))
    out = []
    d = os.path.join(CFN_DIR, "stacks")
    for f in sorted(os.listdir(d)):
        if f.endswith(".json"):
            s = read_json(os.path.join(d, f))
            if s: out.append(s)
    return out


def get_stack(name):
    return read_json(_stack_path(name))


def delete_stack(name):
    s = get_stack(name)
    if not s:
        return False, f"stack '{name}' not found"
    os.remove(_stack_path(name))
    return True, f"deleted stack '{name}'"
