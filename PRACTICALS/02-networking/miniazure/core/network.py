"""VNets, subnets, and VM-to-subnet attachment.

A VNet is a private network (CIDR range).
A subnet is a slice of that range.
A VM attaches to a subnet and gets an IP.
"""
import os

import config
from utils import now_iso, read_json, write_json, delete_file, ensure_dir
from core import resource_group as rg
from core import net_addr
from core import vm as vmm


VNETS_DIR = os.path.join(config.STATE_DIR, "network", "vnets")


# ---- paths ----

def _vnet_path(name):
    return os.path.join(VNETS_DIR, f"{name}.json")


# ---- validation ----

def validate_vnet_name(name):
    if not name:
        return "vnet name required"
    if len(name) < 2 or len(name) > 64:
        return "vnet name must be 2-64 chars"
    return None


def validate_subnet_name(name):
    if not name:
        return "subnet name required"
    if len(name) < 2 or len(name) > 80:
        return "subnet name must be 2-80 chars"
    return None


# ---- VNet ----

def create_vnet(name, group, cidr):
    e = validate_vnet_name(name)
    if e:
        return False, e

    if os.path.exists(_vnet_path(name)):
        return False, f"vnet '{name}' already exists"

    if not rg.get(group):
        return False, f"resource group '{group}' not found"

    net = net_addr.parse_cidr(cidr)
    if not net:
        return False, f"invalid CIDR '{cidr}'. Example: 10.0.0.0/16"

    if net.prefixlen > 24:
        return False, f"vnet CIDR too small ({cidr}). Use /16 to /24"

    # Check this CIDR doesn't overlap with any existing vnet
    for existing in list_vnets():
        existing_net = net_addr.parse_cidr(existing.get("cidr", ""))
        if existing_net and net_addr.networks_overlap(net, existing_net):
            return False, (f"CIDR {cidr} overlaps with vnet "
                           f"'{existing['name']}' ({existing['cidr']})")

    data = {
        "id": f"/subscriptions/local/resourceGroups/{group}/providers/Microsoft.Network/virtualNetworks/{name}",
        "name": name,
        "type": "Microsoft.Network/virtualNetworks",
        "resourceGroup": group,
        "location": rg.get(group).get("location", config.DEFAULT_REGION),
        "cidr": str(net),
        "subnets": {},
        "created": now_iso(),
    }

    ensure_dir(VNETS_DIR)
    write_json(_vnet_path(name), data)
    return True, f"created vnet '{name}' with CIDR {net}"


def get_vnet(name):
    return read_json(_vnet_path(name))


def list_vnets():
    ensure_dir(VNETS_DIR)
    out = []
    for f in sorted(os.listdir(VNETS_DIR)):
        if f.endswith(".json"):
            data = read_json(os.path.join(VNETS_DIR, f))
            if data:
                out.append(data)
    return out


def delete_vnet(name):
    data = get_vnet(name)
    if not data:
        return False, f"vnet '{name}' not found"
    if data.get("subnets"):
        return False, f"vnet '{name}' has subnets. Delete them first."
    delete_file(_vnet_path(name))
    return True, f"deleted vnet '{name}'"


# ---- Subnet ----

def create_subnet(vnet_name, subnet_name, cidr):
    e = validate_subnet_name(subnet_name)
    if e:
        return False, e

    vnet = get_vnet(vnet_name)
    if not vnet:
        return False, f"vnet '{vnet_name}' not found"

    if subnet_name in vnet.get("subnets", {}):
        return False, f"subnet '{subnet_name}' already exists in '{vnet_name}'"

    subnet_net = net_addr.parse_cidr(cidr)
    if not subnet_net:
        return False, f"invalid CIDR '{cidr}'"

    # Must be inside the vnet
    if not net_addr.subnet_is_inside(vnet["cidr"], cidr):
        return False, f"subnet {cidr} is not inside vnet range {vnet['cidr']}"

    # Must not overlap with other subnets in this vnet
    for existing_name, existing in vnet["subnets"].items():
        existing_net = net_addr.parse_cidr(existing["cidr"])
        if existing_net and net_addr.networks_overlap(subnet_net, existing_net):
            return False, (f"subnet {cidr} overlaps with "
                           f"'{existing_name}' ({existing['cidr']})")

    vnet["subnets"][subnet_name] = {
        "name": subnet_name,
        "cidr": str(subnet_net),
        "ips_used": {},   # vm_name -> ip
        "created": now_iso(),
    }
    write_json(_vnet_path(vnet_name), vnet)
    return True, f"created subnet '{subnet_name}' ({subnet_net}) in vnet '{vnet_name}'"


def list_subnets(vnet_name):
    vnet = get_vnet(vnet_name)
    if not vnet:
        return None
    return vnet.get("subnets", {})


def delete_subnet(vnet_name, subnet_name):
    vnet = get_vnet(vnet_name)
    if not vnet:
        return False, f"vnet '{vnet_name}' not found"
    if subnet_name not in vnet.get("subnets", {}):
        return False, f"subnet '{subnet_name}' not found in '{vnet_name}'"
    subnet = vnet["subnets"][subnet_name]
    if subnet.get("ips_used"):
        return False, f"subnet '{subnet_name}' still has VMs attached"
    del vnet["subnets"][subnet_name]
    write_json(_vnet_path(vnet_name), vnet)
    return True, f"deleted subnet '{subnet_name}'"


# ---- Attach VM to subnet ----

def attach_vm(vm_name, vnet_name, subnet_name):
    vnet = get_vnet(vnet_name)
    if not vnet:
        return False, f"vnet '{vnet_name}' not found"

    subnet = vnet.get("subnets", {}).get(subnet_name)
    if not subnet:
        return False, f"subnet '{subnet_name}' not found in '{vnet_name}'"

    vm_data = vmm.get(vm_name)
    if not vm_data:
        return False, f"VM '{vm_name}' not found"

    # Already attached?
    if vm_name in subnet.get("ips_used", {}):
        return False, f"VM '{vm_name}' is already attached to this subnet"

    # Find next free IP (starting after Azure's reserved 4)
    used_ips = set(subnet.get("ips_used", {}).values())
    subnet_net = net_addr.parse_cidr(subnet["cidr"])
    hosts = list(subnet_net.hosts())[4:]   # skip first 4 (reserved)

    free_ip = None
    for h in hosts:
        if str(h) not in used_ips:
            free_ip = str(h)
            break

    if not free_ip:
        return False, f"subnet '{subnet_name}' is full"

    # Record in subnet
    subnet.setdefault("ips_used", {})[vm_name] = free_ip

    # Record on the VM
    vm_data["network"] = {
        "vnet": vnet_name,
        "subnet": subnet_name,
        "ip": free_ip,
        "cidr": subnet["cidr"],
    }
    vmm.write_json(vmm._vm_path(vm_name), vm_data)

    write_json(_vnet_path(vnet_name), vnet)
    return True, f"attached VM '{vm_name}' to {vnet_name}/{subnet_name} with IP {free_ip}"


def detach_vm(vm_name, vnet_name, subnet_name):
    vnet = get_vnet(vnet_name)
    if not vnet:
        return False, f"vnet '{vnet_name}' not found"
    subnet = vnet.get("subnets", {}).get(subnet_name)
    if not subnet:
        return False, f"subnet '{subnet_name}' not found"
    if vm_name not in subnet.get("ips_used", {}):
        return False, f"VM '{vm_name}' is not attached here"
    ip = subnet["ips_used"].pop(vm_name)
    write_json(_vnet_path(vnet_name), vnet)

    vm_data = vmm.get(vm_name)
    if vm_data:
        vm_data.pop("network", None)
        vmm.write_json(vmm._vm_path(vm_name), vm_data)
    return True, f"detached VM '{vm_name}' (freed IP {ip})"


def show_topology():
    """Return a nested view of all vnets, subnets, and attached VMs."""
    out = []
    for vnet in list_vnets():
        node = {
            "name": vnet["name"],
            "cidr": vnet["cidr"],
            "group": vnet["resourceGroup"],
            "subnets": [],
        }
        for sname, sdata in vnet.get("subnets", {}).items():
            s = {
                "name": sname,
                "cidr": sdata["cidr"],
                "vms": [{"name": vm, "ip": ip}
                        for vm, ip in sdata.get("ips_used", {}).items()],
            }
            node["subnets"].append(s)
        out.append(node)
    return out
