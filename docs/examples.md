# quotes.toscrape
A [quotes.toscrape](https://quotes.toscrape.com) parser example

```python
from typing import Annotated
from collections import Counter
import json

import requests
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect
from scrape_schema.fields.nested import NestedList
from scrape_schema.callbacks.soup import crop_by_tag_all, get_attr


def top_10(lst: list[str]) -> list[str]:
    """get 10 most common tags"""
    return [v[0] for v in Counter(lst).most_common(10)]


class Quote(BaseSchema):
    # <div class="quote">
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    text: Annotated[str, SoupFind('<span class="text">')]
    author: Annotated[str, SoupFind('<small class="author">')]
    about: Annotated[str, SoupFind(
        {"name": "a", "string": "(about)"}, callback=get_attr("href"))]
    tags: Annotated[list[str], SoupFindList('<a class="tag">')]


class QuotePage(BaseSchema):
    # https://quotes.toscrape.com/page/{} document
    # set usage parsers backends
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    title: Annotated[str, SoupSelect('head > title')]
    # wrote just example, recommended write properties or methods in this class
    title_len: Annotated[int, SoupFind("<title>", factory=len)]
    title_upper: Annotated[str, SoupFind("<title>", factory=lambda t: t.upper())]

    quotes: Annotated[list[Quote], NestedList(Quote, crop_rule=crop_by_tag_all({"name": "div", "class_": "quote"},
                                                                               features="html.parser"))]
    top_10_tags: Annotated[list[str], SoupFindList('<a class="tag">',
                                                   factory=top_10)]
    top_tags_5_len: Annotated[list[str], SoupFindList('<a class="tag">',
                                                      filter_=lambda el: len(el.get_text()) <= 5,
                                                      factory=top_10)]


if __name__ == '__main__':
    resp = requests.get("https://quotes.toscrape.com/page/1/").text
    schema = QuotePage(resp)
    print(schema.title)
    print(schema.title_upper)
    print(schema.title_len)
    print(schema.top_10_tags)
    print(schema.top_tags_5_len)
    print(schema.quotes[0].text, schema.quotes[0].about)
    print(json.dumps(schema.dict(), indent=4))  # pretty print
    # parse many responses
    # NOTE: recommend usage selectolax backend for increase speed
    responses = [requests.get(f"https://quotes.toscrape.com/page/{i}/").text
                 for i in range(1, 3)]
    schemas = QuotePage.init_list(responses)
    print(*schemas, sep="\n---\n")
```

# Wikipedia parser

>>> Note: this parser works only English version (en.wikipedia.org)!

```python
from typing import Annotated
import json

import requests
from selectolax.parser import HTMLParser

from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList
from scrape_schema.callbacks.slax import get_attr, get_text


class MainEnPage(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}

    articles_count: Annotated[int, SlaxSelect("#articlecount > a:nth-child(1)",
                                              callback=lambda el: el.text().replace(",", ""))]
    language: Annotated[str, SlaxSelect('#articlecount > a:nth-child(2)')]
    featured_article: Annotated[str, SlaxSelect('#mp-tfa > p')]
    did_your_know: Annotated[list[str], SlaxSelectList('#mp-dyk > ul > li')]
    in_the_news: Annotated[list[str], SlaxSelectList('#mp-itn > ul > li')]
    on_this_day_date: Annotated[str, SlaxSelect('#mp-otd > p')]
    on_this_day: Annotated[list[str], SlaxSelectList('#mp-otd > ul > li')]
    today_feature_picture: Annotated[str, SlaxSelect('#mp-tfp > table > tbody > tr:nth-child(1) > td > a',
                                                     callback=get_attr('href'))]
    today_feature_picture_description: Annotated[str, SlaxSelect(
        '#mp-tfp > table > tbody > tr:nth-child(2) > td > p:nth-child(1)')]
    footer_info: Annotated[str, SlaxSelect('#footer', callback=get_text(strip=True))]


if __name__ == '__main__':
    resp = requests.get("https://en.wikipedia.org").text
    main_page_en = MainEnPage(resp)
    print(json.dumps(main_page_en.dict(), indent=4))
```

# stdout parser
>>> Note: this example has mock value if you don't have linux

```python
# schema.py
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch, ReMatchList
from typing import Annotated


class Device(BaseSchema):
    num: Annotated[int, ReMatch(r"^(\d+):")]
    name: Annotated[str, ReMatch(r"^\d+: (\w+):")]
    interface: Annotated[list[str], ReMatch(r"<([\w,_]+)>", factory=lambda s: s.split(","))]
    mtu: Annotated[int, ReMatch(r"mtu (\d+)")]
    qdisc: Annotated[str, ReMatch(r"qdisc (\w+)")]
    state: Annotated[str, ReMatch(r"state ([A-Z]+)")]
    group: Annotated[str, ReMatch(r"group (\w+)", default="unknown")]
    qlen: Annotated[int, ReMatch(r"qlen (\d+)")]
    link: Annotated[str, ReMatch(r"link/(\w+)")]
    addr: Annotated[str, ReMatch(r"link/\w+ ([\d:a-z]+)")]
    ipv4: Annotated[list[str], ReMatchList(r"inet ([\d./]+)")]
    ipv6: Annotated[list[str], ReMatchList(r"inet6 ([a-z\d./:]+)")]
```

```python
# main.py
import re
import json

import sys
import subprocess

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

    # convert to json
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
```

# hackernews
A [hackernews](https://news.ycombinator.com) parser example
```python
# callbacks.py
from bs4 import BeautifulSoup


def crop_posts(markup: str) -> list[str]:
    """a crop rule for hackenews schema"""
    soup = BeautifulSoup(markup, 'html.parser')
    # get main news table
    table = soup.find('tr', class_='athing').parent
    elements: list[str] = []
    first_tag: str = ''
    # get two 'tr' tags and concatenate, skip <tr class='spacer'>

    for tr in table.find_all('tr'):
        # <tr class="athing">
        if tr.attrs.get('class') and 'athing' in tr.attrs.get('class'):
            first_tag = str(tr)
        # <tr>
        elif not tr.attrs:
            elements.append(first_tag + '\n' + str(tr))
            first_tag = ''
        # <tr class="morespace"> END page, stop iteration
        elif tr.attrs.get('class') and 'morespace' in tr.attrs.get('class'):
            break
    return elements


def concat_href(path: str) -> str:
    """custom factory for concatenate path url with netloc"""
    return f"https://news.ycombinator.com{path}"
```

```python
# schema.py
# A hackernews schema parser https://news.ycombinator.com
from typing import Annotated
import re

from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.fields.soup import SoupFind, SoupSelect
from scrape_schema.fields.nested import NestedList
from scrape_schema.fields.regex import ReMatch
from scrape_schema.callbacks.soup import get_attr, replace_text

from callbacks import crop_posts, concat_href


class Post(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    id: Annotated[int, SoupFind('<tr class="athing">', callback=get_attr('id'))]
    rank: Annotated[int, SoupFind('<span class="rank">', callback=replace_text('.', ''))]
    vote_up: Annotated[str, SoupFind({'name': 'a', 'id': re.compile(r'^up_\d+')},
                                     callback=get_attr('href'), factory=concat_href)]
    source: Annotated[str, SoupSelect('td.title > span.titleline > a', callback=get_attr('href'))]
    title: Annotated[str, SoupSelect('td.title > span.titleline > a')]
    source_netloc: Annotated[str, SoupFind('<span class="sitebit comhead">')]
    score: Annotated[int, SoupFind('<span class="score">', callback=replace_text(' points', ''), default=0)]
    author: Annotated[str, SoupFind('<a class="hnuser">')]
    author_url: Annotated[str, SoupFind('<a class="hnuser">', callback=get_attr('href'), factory=concat_href)]
    date: Annotated[str, SoupFind('<span class="age">', callback=get_attr('title'))]
    time_ago: Annotated[str, SoupSelect('span.age > a')]
    comments: Annotated[int, ReMatch(r'(\d+)\s+comments', default=0)]
    post_url: Annotated[str, SoupFind({'name': 'a', 'href': re.compile(r'^item\?id=\d+')}, callback=get_attr('href'),
                                      factory=concat_href)]


class HackerNewsSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    posts: Annotated[list[Post], NestedList(Post, crop_rule=crop_posts)]
```

```python
# main.py
import pprint
import requests

from schema import HackerNewsSchema

if __name__ == '__main__':
    resp = requests.get('https://news.ycombinator.com').text
    schema = HackerNewsSchema(resp)
    # # or you can get Post objects list:
    # from schema import Post
    # from callbacks import crop_posts
    # posts = Post.init_list(crop_posts(resp))
    # ...
    pprint.pprint(schema.dict(), width=60, compact=True)
    most_comment_posts = list(filter(lambda p: p.comments > 50, schema.posts))
    shorten_nicknames = list(filter(lambda p: len(p.author) <= 8, schema.posts))
    print(*most_comment_posts, sep="\n")
    print()
    print(*[p.author for p in shorten_nicknames], sep="\n")
```