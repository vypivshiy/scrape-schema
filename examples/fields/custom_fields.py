import pprint
from typing import Any, Callable, Optional

from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.base import BaseField, BaseFieldConfig
from scrape_schema.fields.regex import ReMatch

# example strings
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
    <img src="/baz.jpg">
"""

# Recipe 1. create field instances and use in ScrapeSchema classes
EmailField = ReMatch(r"([\w\-_.]{2,32}@\w{2,12}\.\w{2,8})")
Ipv4 = ReMatch(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")


# Recipe 2: create a custom fields
class RawText(BaseField):
    """retrun raw or reversed markup"""

    def __init__(self, reverse: bool = False, foil_arg: Any = "any useful argument"):
        super().__init__()
        self.reverse = reverse
        self.foil = foil_arg

    def _parse(self, markup: str) -> str:
        return markup[::-1] if self.reverse else markup


class SoupImage(BaseField):
    # markup parser rule config
    class Config(BaseFieldConfig):
        parser = BeautifulSoup

    # base api provide filter_ (for iterable values), callback, factory and default
    def __init__(
        self,
        filter_: Optional[Callable[[str], bool]] = None,
        callback: Optional[Callable[[str], Any]] = None,
        factory: Optional[Callable[[Any], Any]] = None,
        default: Optional[str] = "empty",
    ):
        super().__init__(
            factory=factory, filter_=filter_, callback=callback, default=default
        )

    def _parse(self, markup: BeautifulSoup) -> str | Any:
        return image.get("src") if (image := markup.find("img")) else self.default


class SoupImageList(SoupImage):
    def __init__(
        self,
        filter_: Optional[Callable[[str], bool]] = None,
        callback: Optional[Callable[[str], Any]] = None,
        factory: Optional[Callable[[Any], Any]] = None,
        default: Optional[str] = "empty",
    ):
        super().__init__(
            filter_=filter_, callback=callback, factory=factory, default=default
        )

    def _parse(self, markup: BeautifulSoup) -> str | list[str]:
        if images := markup.find_all("img"):
            return [tag.get("src") for tag in images]
        return []


class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    raw: ScField[str, RawText(foil_arg=object())]
    email: ScField[str, EmailField]
    ipv4: ScField[str, Ipv4]
    image: ScField[str, SoupImage()]
    images: ScField[list[str], SoupImageList()]
    images_png: ScField[list[str], SoupImageList(filter_=lambda s: s.endswith(".png"))]
    images_png_full: ScField[
        list[str],
        SoupImageList(
            filter_=lambda s: s.endswith(".png"),
            callback=lambda s: "https://example.com" + s,
        ),
    ]


if __name__ == "__main__":
    schema_1 = Schema(TEXT)
    schema_2 = Schema(HTML)
    pprint.pprint(schema_1.dict(), width=48, compact=True)
    # {'email': 'spamegg@spam.egg',
    #  'image': 'empty',
    #  'images': None,
    #  'images_png': None,
    #  'images_png_full': None,
    #  'ipv4': '192.168.0.1',
    #  'raw': '\n192.168.0.1\nspamegg@spam.egg\n'}
    pprint.pprint(schema_2.dict(), width=48, compact=True)
    # {'email': 'spamegg@spam.egg',
    #  'image': '/foo.png',
    #  'images': ['/foo.png', '/bar.png', '/baz.jpg'],
    #  'images_png': ['/foo.png', '/bar.png'],
    #  'images_png_full': ['https://example.com/foo.png',
    #                      'https://example.com/bar.png'],
    #  'ipv4': '192.168.0.1',
    #  'raw': '\n'
    #         '<!DOCTYPE html>\n'
    #         '<html lang="en">\n'
    #         '<head>\n'
    #         '    <meta charset="UTF-8">\n'
    #         '    <title>Custom fields</title>\n'
    #         '</head>\n'
    #         '<body>\n'
    #         '    <p>192.168.0.1</p>\n'
    #         '    <p>spamegg@spam.egg</p>\n'
    #         '    <img src="/foo.png">\n'
    #         '    <img src="/bar.png">\n'
    #         '    <img src="/baz.jpg">\n'}
