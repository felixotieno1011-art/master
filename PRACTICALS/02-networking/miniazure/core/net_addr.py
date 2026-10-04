"""CIDR math — parse, validate, and check overlaps."""
import ipaddress


def parse_cidr(cidr):
    """Return ipaddress.IPv4Network or None if invalid."""
    try:
        return ipaddress.ip_network(cidr, strict=False)
    except Exception:
        return None


def is_valid_cidr(cidr):
    return parse_cidr(cidr) is not None


def networks_overlap(net1, net2):
    """Return True if two networks share any IP."""
    return net1.overlaps(net2)


def subnet_is_inside(vnet_cidr, subnet_cidr):
    """Check subnet is fully inside the vnet range."""
    v = parse_cidr(vnet_cidr)
    s = parse_cidr(subnet_cidr)
    if not v or not s:
        return False
    return s.subnet_of(v)


def first_usable_ip(subnet_cidr, offset=4):
    """
    Return the Nth usable IP in the subnet.
    Azure reserves the first 4 IPs in each subnet, so we do too.
    """
    s = parse_cidr(subnet_cidr)
    if not s:
        return None
    hosts = list(s.hosts())
    if offset >= len(hosts):
        return None
    return str(hosts[offset])
