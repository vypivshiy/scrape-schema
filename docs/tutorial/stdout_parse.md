# stdout parser
>>> Note: in this tutorial there will be no theory of writing regular expressions. 
> It assumes that you know how to write them.
> For the initial writing of expressions, use [regex101](https://regex101.com/) service and official documentation 
[regex how-to](https://docs.python.org/3.11/howto/regex.html#regex-howto)

Welcome to scrape_schema tutorial!

This tutorial will walk through the case of getting data from terminal stdout using `scrape_schema.fields.regex` module.

You can embed any projects this way
with a terminal interface when parsing a stdout string using regular expressions (as in bash, bat scripts)

The algorithm for this task is as follows:

1. run terminal command using `subprocess` module (or `asyncio.subprocess` if your project is async)
2. get stdout
3. parse it
4. serialise them


# ip a
For example, let's write a parser for the unix command `ip a`
>>> If you do not have a linux system, then you can use the `Stub` in the example, install a wsl (windows) 
> or docker container ([docker ubuntu](https://hub.docker.com/_/ubuntu)) and run this code 

`ip a` execute command and Stub:
```python
import sys
import subprocess


if sys.platform == "linux":
    # if OS linux
    STDOUT = subprocess.Popen(["ip", "a"], stdout=subprocess.PIPE, text=True).stdout.read()  # type: ignore
else:
    # `$ ip a` stub if not unix system
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
```
To simplify the writing of the parser, we will write a function for separating interfaces into parts
```python
import pprint
from typing import List
import re


def crop_stdout(stdout: str) -> List[str]:
    interfaces = re.split(r"^\d+: ", stdout, flags=re.MULTILINE)  # crop by interface num
    # add interface num
    return [f"{i}: {interface}" for i, interface in enumerate(interfaces, 0) if interface] 


pprint.pprint(crop_stdout(STDOUT), compact=True)
# ['1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group '
#  'default qlen 1000\n'
#  '    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00\n'
#  '    inet 127.0.0.1/8 scope host lo\n'
#  '       valid_lft forever preferred_lft forever\n'
#  '    inet6 ::1/128 scope host \n'
#  '       valid_lft forever preferred_lft forever\n',
#  '2: wlp2s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP '
#  'group default qlen 1000\n'
#  '    link/ether ab:cd:de:f0:11:55 brd ff:ff:ff:ff:ff:ff\n'
#  '    inet 192.168.1.130/24 brd 192.168.1.255 scope global dynamic '
#  'noprefixroute wlp2s0\n'
#  '       valid_lft 66988sec preferred_lft 66988sec\n'
#  '    inet6 fefe::abcd:e000:0101:3695/64 scope link noprefixroute \n'
#  '       valid_lft forever preferred_lft forever\n',
#  '3: vpn: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1420 qdisc noqueue state UNKNOWN '
#  'group default qlen 1000\n'
#  '    link/none \n'
#  '    inet 10.3.2.3/32 scope global noprefixroute vpn\n'
#  '       valid_lft forever preferred_lft forever\n'
#  '    inet6 fd00::3:2:3/128 scope global noprefixroute \n'
#  '       valid_lft forever preferred_lft forever\n'
#  '    inet6 fe80::b2d:189b:c179:3b10/64 scope link noprefixroute \n'
#  '       valid_lft forever preferred_lft forever\n']
```
# about regex fields
* `ReMatch` - Scan through a string, and return first match (`re.search(...)` function analog)

* `ReMatchList` - Scan through a string, and return all matches (`[match for match in re.finditer(...)]` code analog)

`ScField` is a `typing.Annotated` alias, specially allocated in the module for 
backwards compatibility, as this type is added in 3.9 version. 


ScField typing syntax in BaseSchema class:

`ScField[<type>, Field1, Field2, ... FieldN]`

Loops until it finds a field value (not an empty list, dictionary, or None). If not found -
sets default value of last field:

```python
from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch

class Schema(BaseSchema):
    digit: ScField[int, 
                   ReMatch(r"(\d\d\d)"), # None
                   ReMatch(r"(\d\d)"),  # None
                   ReMatch(r"([a-z])", default=100)  # 100
    ]

print(Schema("1"))
# Schema(digit:int=100)
```

Fields usage example:

```python
from typing import Optional
from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchList

class Schema(BaseSchema):
    num: ScField[int, ReMatch(r"(\d+)")]
    nums: ScField[list[int], ReMatchList(r"(\d+)")]
    word: ScField[str, ReMatch(r"([a-zA-Z]+)")]
    words: ScField[list[str], ReMatchList(r"([a-zA-Z]+)")]
    words_reverse: ScField[list[str], ReMatchList(r"([a-zA-Z]+)", callback=lambda s: s[::-1])]
    has_spam: ScField[bool, ReMatch(r"(spam)")]
    has_spam_2: ScField[Optional[bool], ReMatch(r"(spam)")]
    has_egg: ScField[bool, ReMatch(r"(egg)")]
    has_egg_2: ScField[Optional[bool], ReMatch(r"(egg)")]

schema = Schema("5 Lorem upSum 10 doLor spam 8")
print(schema)
# Schema(num:int=5, 
# nums:list=[5, 10, 8], 
# word:str='Lorem', 
# words:list=['Lorem', 'upSum', 'doLor', 'spam'], 
# words_reverse:list=['meroL', 'muSpu', 'roLod', 'maps'], 
# has_spam:bool=True, 
# has_spam_2:bool=True, 
# has_egg:bool=False, 
# has_egg_2:NoneType=None)
```

>>> Note: `ScField (typing.Annotated)` specifies type at runtime and **is not 100% guaranteed to be correct**

```python
from scrape_schema import ScField, BaseSchema
from scrape_schema.fields.regex import ReMatch

class Schema(BaseSchema):
    # factory disable type-cast feature, you should be manually convert to int
    digit: ScField[int, ReMatch(r"(\d+)", factory=str)]

    
print(Schema("1"))
# Schema(digit:str='1')
schema = Schema("digit?")
print(schema)
# Schema(digit:str='None')

schema.digit = ["I", "NEED", "DIGIT", "NOT", "STR"]
print(schema)
# Schema(digit:list=['I', 'NEED', 'DIGIT', 'NOT', 'STR'])
```

# write `ip a` parser
```python
from typing import List, Optional
import re

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchList


class Device(BaseSchema):
    num: ScField[int, ReMatch(r"^(\d+):")]
    name: ScField[str, ReMatch(r"^\d+: (\w+):")]
    interface: ScField[
        List[str], 
        ReMatch(r"<([\w,_]+)>", factory=lambda s: s.split(",") if s else [])
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
        # you can write custom constructor for create `BaseSchema` objects
        interfaces = re.split(r"^\d+: ", stdout, flags=re.MULTILINE) # crop by interface num
        # add interface num
        return cls.from_list(
            [f"{i}: {interface}" for i, interface in enumerate(interfaces, 0) if interface]
        ) 

print(*Device.from_stdout(STDOUT), sep="\n")
# Device(num:int=1, name:str='lo', interface:list=['LOOPBACK', 'UP', 'LOWER_UP'], mtu:int=65536, qdisc:str='noqueue', state:str='UNKNOWN', group:str='default', qlen:int=1000, link:str='loopback', addr:str='00:00:00:00:00:00', ipv4:list=['127.0.0.1/8'], ipv6:list=['::1/128'])
# Device(num:int=2, name:str='wlp2s0', interface:list=['BROADCAST', 'MULTICAST', 'UP', 'LOWER_UP'], mtu:int=1500, qdisc:str='noqueue', state:str='UP', group:str='default', qlen:int=1000, link:str='ether', addr:str='ab:cd:de:f0:11:55', ipv4:list=['192.168.1.130/24'], ipv6:list=['fefe::abcd:e000:0101:3695/64'])
# Device(num:int=3, name:str='vpn', interface:list=['POINTOPOINT', 'NOARP', 'UP', 'LOWER_UP'], mtu:int=1420, qdisc:str='noqueue', state:str='UNKNOWN', group:str='default', qlen:int=1000, link:str='none', addr:NoneType=None, ipv4:list=['10.3.2.3/32'], ipv6:list=['fd00::3:2:3/128', 'fe80::b2d:189b:c179:3b10/64'])

# same, without custom constructor
print(*Device.from_crop_rule_list(STDOUT, crop_rule=crop_stdout), sep="\n")
# Device(num:int=1, name:str='lo', interface:list=['LOOPBACK', 'UP', 'LOWER_UP'], mtu:int=65536, qdisc:str='noqueue', state:str='UNKNOWN', group:str='default', qlen:int=1000, link:str='loopback', addr:str='00:00:00:00:00:00', ipv4:list=['127.0.0.1/8'], ipv6:list=['::1/128'])
# Device(num:int=2, name:str='wlp2s0', interface:list=['BROADCAST', 'MULTICAST', 'UP', 'LOWER_UP'], mtu:int=1500, qdisc:str='noqueue', state:str='UP', group:str='default', qlen:int=1000, link:str='ether', addr:str='ab:cd:de:f0:11:55', ipv4:list=['192.168.1.130/24'], ipv6:list=['fefe::abcd:e000:0101:3695/64'])
# Device(num:int=3, name:str='vpn', interface:list=['POINTOPOINT', 'NOARP', 'UP', 'LOWER_UP'], mtu:int=1420, qdisc:str='noqueue', state:str='UNKNOWN', group:str='default', qlen:int=1000, link:str='none', addr:NoneType=None, ipv4:list=['10.3.2.3/32'], ipv6:list=['fd00::3:2:3/128', 'fe80::b2d:189b:c179:3b10/64'])
```

### Full code project:
```python
from typing import List, Optional
import re
import sys
import subprocess

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
    interfaces = re.split(r"^\d+: ", stdout, flags=re.MULTILINE) # crop by interface num
    #add interface num
    return [f"{i}: {interface}" for i, interface in enumerate(interfaces, 0) if interface] 


class Device(BaseSchema):
    """An `ip a` python object"""
    num: ScField[int, ReMatch(r"^(\d+):")]
    name: ScField[str, ReMatch(r"^\d+: (\w+):")]
    interface: ScField[
        List[str], 
        ReMatch(r"<([\w,_]+)>", factory=lambda s: s.split(",") if s else [])
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
        interfaces = re.split(r"^\d+: ", stdout, flags=re.MULTILINE) # crop by interface num
        #add interface num
        return cls.from_list(
            [f"{i}: {interface}" for i, interface in enumerate(interfaces, 0) if interface]
        ) 

    
print(*Device.from_stdout(STDOUT), sep="\n")
# Device(num:int=1, name:str='lo', interface:list=['LOOPBACK', 'UP', 'LOWER_UP'], mtu:int=65536, qdisc:str='noqueue', state:str='UNKNOWN', group:str='default', qlen:int=1000, link:str='loopback', addr:str='00:00:00:00:00:00', ipv4:list=['127.0.0.1/8'], ipv6:list=['::1/128'])
# Device(num:int=2, name:str='wlp2s0', interface:list=['BROADCAST', 'MULTICAST', 'UP', 'LOWER_UP'], mtu:int=1500, qdisc:str='noqueue', state:str='UP', group:str='default', qlen:int=1000, link:str='ether', addr:str='ab:cd:de:f0:11:55', ipv4:list=['192.168.1.130/24'], ipv6:list=['fefe::abcd:e000:0101:3695/64'])
# Device(num:int=3, name:str='vpn', interface:list=['POINTOPOINT', 'NOARP', 'UP', 'LOWER_UP'], mtu:int=1420, qdisc:str='noqueue', state:str='UNKNOWN', group:str='default', qlen:int=1000, link:str='none', addr:NoneType=None, ipv4:list=['10.3.2.3/32'], ipv6:list=['fd00::3:2:3/128', 'fe80::b2d:189b:c179:3b10/64'])

# same, without custom constructor
print(*Device.from_crop_rule_list(STDOUT, crop_rule=crop_stdout), sep="\n")
# Device(num:int=1, name:str='lo', interface:list=['LOOPBACK', 'UP', 'LOWER_UP'], mtu:int=65536, qdisc:str='noqueue', state:str='UNKNOWN', group:str='default', qlen:int=1000, link:str='loopback', addr:str='00:00:00:00:00:00', ipv4:list=['127.0.0.1/8'], ipv6:list=['::1/128'])
# Device(num:int=2, name:str='wlp2s0', interface:list=['BROADCAST', 'MULTICAST', 'UP', 'LOWER_UP'], mtu:int=1500, qdisc:str='noqueue', state:str='UP', group:str='default', qlen:int=1000, link:str='ether', addr:str='ab:cd:de:f0:11:55', ipv4:list=['192.168.1.130/24'], ipv6:list=['fefe::abcd:e000:0101:3695/64'])
# Device(num:int=3, name:str='vpn', interface:list=['POINTOPOINT', 'NOARP', 'UP', 'LOWER_UP'], mtu:int=1420, qdisc:str='noqueue', state:str='UNKNOWN', group:str='default', qlen:int=1000, link:str='none', addr:NoneType=None, ipv4:list=['10.3.2.3/32'], ipv6:list=['fd00::3:2:3/128', 'fe80::b2d:189b:c179:3b10/64'])
```