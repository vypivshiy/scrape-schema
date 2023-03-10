import pprint
from typing import Optional, Any
import re
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema
from scrape_schema.base import BaseField
from scrape_schema.fields.regex import ReMatch

EmailField = ReMatch(re.compile(r'([\w\-_.]{2,32}@\w{2,12}\.\w{2,8})'))
Ipv4 = ReMatch(re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'))

TEXT = """
192.168.0.1
spamegg@spam.egg
"""


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Custom fields</title>
</head>
<body>
    <p>192.168.0.1</p>
    <p>spamegg@spam.egg</p>
    <img src="/foo.png">
    <img src="/bar.png">
    <img src="/baz.png">
"""


class RawText(BaseField):
    def __init__(self, reverse: bool = False):
        super().__init__()
        self.reverse = reverse

    def parse(self, instance: BaseSchema, name: str, markup: str):
        return markup[::-1] if self.reverse else markup


class SoupImage(BaseField):
    # markup parser rule config
    __MARKUP_PARSER__ = BeautifulSoup

    def __init__(self, default: Optional[Any] = "empty"):
        super().__init__()
        self.default = default

    def parse(self, instance: BaseSchema, name: str, markup: BeautifulSoup):
        return image.get("src") if (image := markup.find("img")) else self.default


class SoupImageList(SoupImage):
    def parse(self, instance: BaseSchema, name: str, markup: BeautifulSoup):
        if images := markup.find_all("img"):
            return [tag.get("src") for tag in images]
        return self.default


class Schema(BaseSchema):
    __MARKUP_PARSERS__ = {BeautifulSoup: {"features": "html.parser"}}
    email: str = EmailField
    ipv4: str = Ipv4
    image: str = SoupImage()
    images: list[str] | str = SoupImageList()


if __name__ == '__main__':
    schema_1 = Schema(TEXT)
    schema_2 = Schema(HTML)
    pprint.pprint(schema_1.dict(), width=48, compact=True)
    # {'email': 'spamegg@spam.egg',
    #  'image': 'empty',
    #  'images': 'empty',
    #  'ipv4': '192.168.0.1'}
    pprint.pprint(schema_2.dict(), width=48, compact=True)
    # {'email': 'spamegg@spam.egg',
    #  'image': '/foo.png',
    #  'images': ['/foo.png', '/bar.png', '/baz.png'],
    #  'ipv4': '192.168.0.1'}
