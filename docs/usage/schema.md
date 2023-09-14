## BaseSchema

Base schema class provide this parsing magic.
This class accept str, bytes, Selector and SelectorList objects.

```python
from scrape_schema import BaseSchema, Sc, Parsel
import requests


class Schema(BaseSchema):
    title: Sc[str, Parsel().xpath("//title/text()").get()]
    body: Sc[str, Parsel().xpath("//body/text()").get()]
    urls: Sc[list[str], Parsel(default=[]).xpath("//a/@href").getall()]


if __name__ == '__main__':
    response = requests.get("https://example.com")
    # from string
    print(Schema(response.text).dict())

    # from bytes
    print(Schema(response.content).dict())

    # or from parsel.Selector object
    from parsel import Selector
    selector = Selector(response.text)
    print(Schema(selector).dict())
```

For various types like Response object (requests, httpx, aiohttp, etc...) -
convert value to str, bytes or parsel.Selector object or write an adapter or custom constructor:

```python
import requests

from scrape_schema import BaseSchema, Sc, Parsel


class Schema(BaseSchema):
    title: Sc[str, Parsel().xpath("//title/text()").get()]
    body: Sc[str, Parsel().xpath("//body/text()").get()]
    urls: Sc[list[str], Parsel(default=[]).xpath("//a/@href").getall()]

    @classmethod
    def from_request(cls, response: requests.Response):
        return cls(response.text)


if __name__ == '__main__':
    resp = requests.get("https://example.com")
    print(Schema.from_request(resp))
```

## Configuration

if you need to pass additional arguments to the constructor (for parse XML, example),
you can import `SchemaConfig` class and add it to the schema

```python
from scrape_schema import BaseSchema
from scrape_schema.base import SchemaConfig


# auto add kwargs for new parsel.Selector instances
class XMLConfig(SchemaConfig):
    selector_kwargs = {'type':'xml'}


class Schema(BaseSchema):
    class Config(XMLConfig):
        pass
    # do something
```


## sc_param
property descriptor for dict() method.
Useful for additional conversion or reuse of a value from the field


```python
import pprint
from typing import Literal

from parsel import Selector
from scrape_schema import BaseSchema, Sc, Parsel, sc_param


class Schema(BaseSchema):
    url_path: Sc[str, Parsel().xpath("//a/@href").get()]
    _raw_tag: Sc[Selector, Parsel(auto_type=False).xpath("//div")[0]]

    @sc_param
    def div(self) -> dict[str, str]:
        return {"class": self._raw_tag.attrib.get('class'),
                "text": self._raw_tag.xpath(".//text()").get()}

    @sc_param
    def url(self) -> str:
        return f"https://example.com/{self.url_path}"

    @sc_param
    def foo(self) -> Literal["foo"]:
        return "foo"


    # this property will not be returned from the dict() method
    @property
    def bar(self) -> str:
        return "bar"

text = """<a href="/image.png">
<div class="example">hello, scrape schema!</div>
"""
pprint.pprint(Schema(text).dict(), compact=True)
# {'div': {'class': 'example', 'text': 'hello, scrape schema!'},
# 'foo': 'foo',
# 'url': 'https://example.com//image.png',
# 'url_path': '/image.png'}
```
