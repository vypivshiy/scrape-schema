import json
import re
import subprocess
import sys

from schema import Device

if sys.platform == "linux":
    STDOUT = subprocess.Popen(["ip", "a"], stdout=subprocess.PIPE, text=True).stdout.read()  # type: ignore
else:
    # `$ ip address show` stdout example
    STDOUT = """1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
        link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
        inet 127.0.0.1/8 scope host lo
           valid_lft forever preferred_lft forever
        inet6 ::1/128 scope host 
           valid_lft forever preferred_lft forever
    2: wlp2s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
        link/ether ab:cd:de:f0:11:55 brd ff:ff:ff:ff:ff:ff
        inet 192.168.1.130/24 brd 192.168.1.255 scope global dynamic noprefixroute wlp2s0
           valid_lft 66988sec preferred_lft 66988sec
        inet6 fefe::abcd:e000:0101:3695/64 scope link noprefixroute 
           valid_lft forever preferred_lft forever
    3: vpn: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1420 qdisc noqueue state UNKNOWN group default qlen 1000
        link/none 
        inet 10.3.2.3/32 scope global noprefixroute vpn
           valid_lft forever preferred_lft forever
        inet6 fd00::3:2:3/128 scope global noprefixroute 
           valid_lft forever preferred_lft forever
        inet6 fe80::b2d:189b:c179:3b10/64 scope link noprefixroute 
           valid_lft forever preferred_lft forever
    """


if __name__ == "__main__":
    # split stdout to parts
    interfaces = re.split(r"^\d+: ", STDOUT, flags=re.MULTILINE)
    interfaces = [f"{i}: {face}" for i, face in enumerate(interfaces, 0) if face]

    devices = Device.init_list(interfaces)
    print(*devices, sep="\n")
    for device in devices:
        print(device.name, device.ipv4, device.ipv6)

    # convert to dict
    print(json.dumps(devices[0].dict(), indent=4))
    # Device(num<int>=1, name<str>=lo, interface<str>=['LOOPBACK', 'UP', 'LOWER_UP'], mtu<int>=65536,
    # qdisc<str>=noqueue, state<str>=UNKNOWN, group<str>=default, qlen<int>=1000, link<str>=loopback,
    # addr<str>=00:00:00:00:00:00, ipv4<list>=['127.0.0.1/8', '192.168.1.130/24', '10.3.2.3/32'],
    # ipv6<list>=['::1/128', 'fefe::abcd:e000:0101:3695/64', 'fd00::3:2:3/128', 'fe80::b2d:189b:c179:3b10/64'])
    # lo ['127.0.0.1/8', '192.168.1.130/24', '10.3.2.3/32'] ['::1/128', 'fefe::abcd:e000:0101:3695/64', 'fd00::3:2:3/128', 'fe80::b2d:189b:c179:3b10/64']
    # {
    #     "num": 1,
    #     "name": "lo",
    #     "interface": "['LOOPBACK', 'UP', 'LOWER_UP']",
    #     "mtu": 65536,
    #     "qdisc": "noqueue",
    #     "state": "UNKNOWN",
    #     "group": "default",
    #     "qlen": 1000,
    #     "link": "loopback",
    #     "addr": "00:00:00:00:00:00",
    #     "ipv4": [
    #         "127.0.0.1/8",
    #         "192.168.1.130/24",
    #         "10.3.2.3/32"
    #     ],
    #     "ipv6": [
    #         "::1/128",
    #         "fefe::abcd:e000:0101:3695/64",
    #         "fd00::3:2:3/128",
    #         "fe80::b2d:189b:c179:3b10/64"
    #     ]
    # }
