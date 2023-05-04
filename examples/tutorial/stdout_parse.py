import re
import subprocess
import sys
from typing import List, Optional

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchList

if sys.platform == "linux":
    # if OS linux
    STDOUT = subprocess.Popen(["ip", "a"], stdout=subprocess.PIPE, text=True).stdout.read()  # type: ignore
else:
    # `$ ip a` mock
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


def crop_stdout(stdout: str) -> List[str]:
    """crop ip a stdout to interfaces parts"""
    interfaces = re.split(
        r"^\d+: ", stdout, flags=re.MULTILINE
    )  # crop by interface num
    # add interface num
    return [
        f"{i}: {interface}" for i, interface in enumerate(interfaces, 0) if interface
    ]


class Device(BaseSchema):
    """An `ip a` python object"""

    num: ScField[int, ReMatch(r"^(\d+):")]
    name: ScField[str, ReMatch(r"^\d+: (\w+):")]
    interface: ScField[
        List[str], ReMatch(r"<([\w,_]+)>", factory=lambda s: s.split(",") if s else [])
    ]
    mtu: ScField[int, ReMatch(r"mtu (\d+)")]
    qdisc: ScField[str, ReMatch(r"qdisc (\w+)")]
    state: ScField[str, ReMatch(r"state ([A-Z]+)")]
    group: ScField[Optional[str], ReMatch(r"group (\w+)")]
    qlen: ScField[int, ReMatch(r"qlen (\d+)")]
    link: ScField[str, ReMatch(r"link/(\w+)")]
    addr: ScField[str, ReMatch(r"link/\w+ ([\d:a-z]+)")]
    ipv4: ScField[List[str], ReMatchList(r"inet ([\d./]+)")]
    ipv6: ScField[List[str], ReMatchList(r"inet6 ([a-z\d./:]+)")]

    @classmethod
    def from_stdout(cls, stdout: str):
        # move crop rule to classmethod constructor
        interfaces = re.split(
            r"^\d+: ", stdout, flags=re.MULTILINE
        )  # crop by interface num
        # add interface num
        return cls.from_list(
            [
                f"{i}: {interface}"
                for i, interface in enumerate(interfaces, 0)
                if interface
            ]
        )


if __name__ == "__main__":
    print(*Device.from_stdout(STDOUT), sep="\n")
    # same, without custom constructor
    print(*Device.from_crop_rule_list(STDOUT, crop_rule=crop_stdout), sep="\n")
