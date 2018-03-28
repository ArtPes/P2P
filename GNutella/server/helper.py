from ipaddr import *


def controlMandator(address, pktIpv4, pktIpv6):
    addrIpv4 = address.split(":")[-1]
    if len(addrIpv4) > 4:
        fragments = addrIpv4.split(".")
        for idx, i in enumerate(fragments):
            fragments[idx] = str(i).zfill(3)
        mandatorIp = ".".join(fragments)
        if mandatorIp == pktIpv4:
            return True
        else:
            return False
    else:

        if IPv6Address(address).exploded == pktIpv6:
            return True
        else:
            return False
    return False
