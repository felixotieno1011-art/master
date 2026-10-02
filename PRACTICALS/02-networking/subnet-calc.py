def ip_to_bin(ip):
    return ''.join(f'{int(x):08b}' for x in ip.split('.'))

def bin_to_ip(b):
    return '.'.join(str(int(b[i:i+8], 2)) for i in range(0, 32, 8))

def subnet_info(ip, cidr):
    ip_bits = ip_to_bin(ip)
    network_bits = ip_bits[:cidr] + '0' * (32 - cidr)
    broadcast_bits = ip_bits[:cidr] + '1' * (32 - cidr)
    total_hosts = 2 ** (32 - cidr) - 2  # minus network & broadcast

    print(f"IP:         {ip}/{cidr}")
    print(f"Network:    {bin_to_ip(network_bits)}")
    print(f"Broadcast:  {bin_to_ip(broadcast_bits)}")
    print(f"Host range: {bin_to_ip(network_bits[:31] + '1')} - {bin_to_ip(broadcast_bits[:31] + '0')}")
    print(f"Hosts:      {total_hosts}")

# Test with YOUR IP
subnet_info("192.168.1.114", 24)
