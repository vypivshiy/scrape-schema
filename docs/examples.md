# Quotes parser
This example required requests or any http library
```python
# required requests or any http lib
from collections import Counter
import json

import requests
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect
from scrape_schema.fields.nested import NestedList
from scrape_schema.tools.soup import crop_by_tag_all, get_tag


def top_10(lst: list[str]) -> list[str]:
    """get 10 most common tags"""
    return [v[0] for v in Counter(lst).most_common(10)]


class Quote(BaseSchema):
    # <div class="quote">
    __MARKUP_PARSERS__ = {BeautifulSoup: {"features": "html.parser"}}

    text: str = SoupFind('<span class="text">')
    author: str = SoupFind('<small class="author">')
    about: str = SoupFind(
        {"name": "a", "string": "(about)"}, callback=get_tag("href")
    )
    tags: list[str] = SoupFindList('<a class="tag">')


class QuotePage(BaseSchema):
    # https://quotes.toscrape.com/page/{} document
    # set usage parsers backends
    __MARKUP_PARSERS__ = {BeautifulSoup: {"features": "html.parser"}}
    title: str = SoupSelect('head > title')
    # wrote just example, recommended write properties or methods in this class
    title_len: int = SoupSelect("head > title", factory=len)
    title_upper: str = SoupFind("<title>", factory=lambda t: t.upper())

    quotes: list[Quote] = NestedList(Quote, crop_rule=crop_by_tag_all({"name": "div", "class_": "quote"},
                                                                      features="html.parser"))
    top_10_tags: list[str] = SoupFindList('<a class="tag">',
                                          factory=top_10)
    top_tags_5_len: list[str] = SoupFindList('<a class="tag">',
                                             filter_=lambda el: len(el.get_text()) <= 5,
                                             factory=top_10)
if __name__ == '__main__':
    resp = requests.get("https://quotes.toscrape.com/page/1/").text
    schema = QuotePage(resp)
    print(json.dumps(schema.dict(), indent=4))
    # parse many pages
    resps = [requests.get(f"https://quotes.toscrape.com/page/{i}/").text
             for i in range(1,3)]
    schemas = QuotePage.parse_many(resps)
    print(*schemas, sep="\n\n")
```
# Wikipedia main page parser
This example works only English version wiki
```python
import requests
import json
from selectolax.parser import HTMLParser

from scrape_schema import BaseSchema
from scrape_schema.fields.slax import SLaxSelect, SLaxSelectList
from scrape_schema.tools.slax import get_tag, get_text


class MainEnPage(BaseSchema):
    # Note: this parser works only English version (en.wikipedia.org)!
    __MARKUP_PARSERS__ = {HTMLParser: {}}
    articles_count: int = SLaxSelect("#articlecount > a:nth-child(1)",
                                     callback=lambda el: el.text().replace(",", ""))
    language: str = SLaxSelect('#articlecount > a:nth-child(2)')
    featured_article: str = SLaxSelect('#mp-tfa > p')
    did_your_know: list[str] = SLaxSelectList('#mp-dyk > ul > li')
    in_the_news: list[str] = SLaxSelectList('#mp-itn > ul > li')
    on_this_day_date: str = SLaxSelect('#mp-otd > p')
    on_this_day: list[str] = SLaxSelectList('#mp-otd > ul > li')
    today_feature_picture: str = SLaxSelect('#mp-tfp > table > tbody > tr:nth-child(1) > td > a',
                                            callback=get_tag('href'))
    today_feature_picture_description: str = SLaxSelect(
        '#mp-tfp > table > tbody > tr:nth-child(2) > td > p:nth-child(1)')
    footer_info: str = SLaxSelect('#footer', callback=get_text(strip=True))


if __name__ == '__main__':
    resp = requests.get("https://en.wikipedia.org").text
    main_page_en = MainEnPage(resp)
    print(json.dumps(main_page_en.dict(), indent=4))

```
# Stdout parser
An `$ ip a` stdout parser.

If you don't have a Unix system, then the stdout stub will be used as an example.

```python
import re

import sys
import subprocess

from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch, ReMatchList


if sys.platform == "linux":
    STDOUT = subprocess.Popen(["ip", "a"], stdout=subprocess.PIPE, text=True).stdout.read()
else:
    # `$ ip addr` stdout stub
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


class Device(BaseSchema):
    num: int = ReMatch(r"^(\d+):")
    name: str = ReMatch(r"^\d+: (\w+):")
    interface: list[str] = ReMatch(r"<([\w,_]+)>", factory=lambda s: s.split(","))
    mtu: int = ReMatch(r"mtu (\d+)")
    qdisc: str = ReMatch(r"qdisc (\w+)")
    state: str = ReMatch(r"state ([A-Z]+)")
    group: str = ReMatch(r"group (\w+)", default="unknown")
    qlen: int = ReMatch(r"qlen (\d+)")
    link: str = ReMatch(r"link/(\w+)")
    addr: str = ReMatch(r"link/\w+ ([\d:a-z]+)")
    ipv4: list[str] = ReMatchList(r"inet ([\d./]+)")
    ipv6: list[str] = ReMatchList(r"inet6 ([a-z\d./:]+)")

    
if __name__ == '__main__':
    # split stdout to parts
    interfaces = re.split(r"^\d+: ", STDOUT, flags=re.MULTILINE)
    interfaces = [f"{i}: {face}" for i, face in enumerate(interfaces, 0) if face]

    devices: list[Device] = Device.parse_many(interfaces)
    print(*devices, sep="\n")
    for device in devices:
        print(device.name, device.ipv4, device.ipv6)
```