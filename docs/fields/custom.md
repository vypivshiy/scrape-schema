# custom fields

There are several ways to create a field

## Create alias 

To improve readability and field reuse, you can create field aliases

```python
from bs4 import BeautifulSoup
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField

from scrape_schema.fields.regex import ReMatch
from scrape_schema.fields.soup import SoupFind, SoupFindList
from scrape_schema.callbacks.soup import get_attr

ReEmail = ReMatch(r'([\w\-_.]{2,32}@\w{2,12}\.\w{2,8})')
ReIpv4 = ReMatch(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

SoupImage = SoupFind("<img>", callback=get_attr("src"))
SoupImages = SoupFindList("<img>", callback=get_attr("src"))

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


class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    email: ScField[str, ReEmail]
    ip_v4: ScField[str, ReIpv4]
    image: ScField[str, SoupImage]
    images: ScField[list[str], SoupImages]
    p_list: ScField[list[str]: SoupFindList("<p>")]
```

## Create new field
Also, you can create your field based on `BaseField` and `BaseConfigField` 
(MetaField required for configuration parser backend)

Optionally, to use the library features, pass the following parameters to the constructor:

* `filter_ Optional[Callable[..., bool]] = None`
* `callback: Optional[Callable[..., Any]] = None`
* `factory: Optional[Callable[..., Any]] = None`
* `default: Optional[Any] = None`

```python
from typing import Optional, Any, Callable
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseFieldConfig, BaseSchemaConfig, ScField
from scrape_schema.base import BaseField

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


class RawText(BaseField):
    """return raw or reversed markup"""

    def __init__(self,
                 reverse: bool = False,
                 foil_arg: Any = "any useful argument"):
        super().__init__()
        self.reverse = reverse
        self.foil = foil_arg

    def _parse(self, markup: str) -> str:
        return markup[::-1] if self.reverse else markup


class SoupImage(BaseField):
    class Meta(BaseFieldConfig):
        # markup parser rule config
        parser = BeautifulSoup

    # base api provide filter_ (for iterable values), callback, factory and default
    def __init__(self,
                 *,
                 filter_: Optional[Callable[[str], bool]] = None,
                 callback: Optional[Callable[[str], Any]] = None,
                 factory: Optional[Callable[[Any], Any]] = None,
                 default: Optional[str] = "empty"):
        super().__init__(factory=factory, filter_=filter_, callback=callback, default=default)

    def _parse(self, markup: BeautifulSoup) -> str | Any:
        return image.get("src") if (image := markup.find("img")) else self.default


class SoupImageList(SoupImage):
    def __init__(self,
                 filter_: Optional[Callable[[str], bool]] = None,
                 callback: Optional[Callable[[str], Any]] = None,
                 factory: Optional[Callable[[Any], Any]] = None,
                 default: Optional[str] = "empty"):
        super().__init__(filter_=filter_, callback=callback, factory=factory, default=default)

    def _parse(self, markup: BeautifulSoup) -> str | list[str]:
        if images := markup.find_all("img"):
            return [tag.get("src") for tag in images]
        return []


class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    raw: ScField[str, RawText(foil_arg=object())]
    image: ScField[str, SoupImage()]
    images: ScField[list[str], SoupImageList()]
    images_png: ScField[list[str], SoupImageList(filter_=lambda s: s.endswith(".png"))]
    images_png_full: ScField[list[str], SoupImageList(filter_=lambda s: s.endswith(".png"),
                                                        callback=lambda s: "https://example.com" + s)]


if __name__ == '__main__':
    schema = Schema(HTML)
    print(schema.dict())
```