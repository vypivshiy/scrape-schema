# Usage
## Quickstart

## About typing.Annotated
This project usage Annotated [(PEP 593)](https://docs.python.org/3/library/typing.html#typing.Annotated)
typehint for annotation fields in runtime and make the static type checker happy 😀
and didn't need write a mypy plugin 🤯.

This project have `Annotated` shortcut `Sc`

```python
from typing import Annotated
from scrape_schema import Sc

assert Annotated == Sc  # OK
```
!!! note
    typing.Annotated does not guarantee type correctness at runtime, it is intended to indicate to
    the static type checker and IDE the intended type.

```python
from typing import Union, Annotated

def spam(a: int) -> Union[int, str]:
    if a < 0:
        return "ooops"
    return a**2

class A:
    a: Annotated[str, spam(-1000)]
    b: Annotated[int, spam(1000)]
    c: Annotated[dict, spam(-1000)]  # mypy OK
    d: Annotated[list[dict[str, int]], spam(float("inf"))]  # also OK
```

## Annotating in attribute-style

There is a way to create a schema using normal field assignment.
But for now there is no mypy plugin to throw an exception and mypy will throw
error with code `assigment`.
!!! warning
    There is currently no plugin for mypy and this method
    will give an `assignment` error.

    to pass mypy check, turn off checking for this type of error by
    `# mypy: disable-error-code="assignment"`

```python
# mypy: disable-error-code="assignment"
from scrape_schema import BaseSchema, Text


class Schema(BaseSchema):
    digit: int = Text().re_search(r"\d+")[0]
    word: str = Text().re_search(r"[a-zA-Z]+")[0]


Schema("test 100").dict()
# {"digit": 100, "word": "test"}

```

- _new 0.5.0_

## logging
For config or disable logging get logger by `scrape_schema` name

```python
import logging
logger = logging.getLogger("scrape_schema")
logger.setLevel(logging.DEBUG)
...
```

For type_caster feature:

```python
import logging
logger = logging.getLogger("type_caster")
logger.setLevel(logging.ERROR)
...
```
- _new 0.5.0_

## BaseSchema

Base schema class provide this parsing magic. Accept str, bytes, Selector and SelectorList objects

for various types like Response object (requests, httpx) - prepare value
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
### Configuration

If your need configuration parse schema rule (example: for xml parse)

```python
from scrape_schema import BaseSchema, Sc, Parsel
from scrape_schema.base import SchemaConfig

class XMLConfig(SchemaConfig):
    # auto add kwargs for new parsel.Selector instances
    selector_kwargs = {'type':'xml'}

class Schema(BaseSchema):
    class Config(XMLConfig):
        pass
    # do something
```

## Fields
For the examples below the following html will be used and will be referred to as HTML

### Parsel
This field simular an original `parsel.Selector` API

```python
from typing import Optional
import pprint

from scrape_schema import BaseSchema, Parsel, Sc


class Schema(BaseSchema):
    # in view `dict` method h1 name swap to `title`
    h1: Sc[str, Parsel(alias="title").css('body > h1').get()]
    # if you don't pass the `default` argument,
    # script raise `TypeError: expected string or bytes-like object`
    real_title: Sc[Optional[str], Parsel(default=None).xpath("//head/title").get().re_search("\w+")[0]]
    # singe xpath query
    urls: Sc[list[str], Parsel().xpath("//ul/li/a/@href").getall()]
    # css + xpath
    urls_css: Sc[list[str], Parsel().css("ul > li > a").xpath("@href").getall()]
    # multiple queries:
    urls_multi: Sc[list[str], Parsel().css("ul").css('li').css('a').xpath("@href").getall()]
    # get urls from parsel.Selector.re methods
    urls_re1: Sc[list[str], Parsel().re(r'href="(https://.*?)"')]
    # get urls from standart regex and disable auto_type feature
    urls_re2: Sc[list[str], Parsel(auto_type=False).xpath("//ul").get().re_findall(r'href="(https://.*?)"')]


if __name__ == '__main__':
    text = """
        <html>
            <body>
                <h1>Hello, Parsel!</h1>
                <ul>
                    <li><a href="https://example.com">Link 1</a></li>
                    <li><a href="https://scrapy.org">Link 2</a></li>
                    <li><a href="https://github.com/vypivshiy/scrape-schema">Link 3</a></li>
                </ul>
                <script type="application/json">{"a": ["b", "c"]}</script>
            </body>
        </html>"""
    pprint.pprint(Schema(text).dict(), compact=True)
# {'real_title': None,
#  'title': '<h1>Hello, Parsel!</h1>',
#  'urls': ['https://example.com', 'https://scrapy.org',
#           'https://github.com/vypivshiy/scrape-schema'],
#  'urls_css': ['https://example.com', 'https://scrapy.org',
#               'https://github.com/vypivshiy/scrape-schema'],
#  'urls_multi': ['https://example.com', 'https://scrapy.org',
#                 'https://github.com/vypivshiy/scrape-schema'],
#  'urls_re1': ['https://example.com', 'https://scrapy.org',
#               'https://github.com/vypivshiy/scrape-schema'],
#  'urls_re2': ['https://example.com', 'https://scrapy.org',
#               'https://github.com/vypivshiy/scrape-schema']}

```

### Text
This field provide raw text parse mode and provide special methods

Have alias `Parsel(raw=True)` and `Parsel().raw_text` and
IDE doesn't show `parsel.Selector` method hints

!!! tip
    This field useful for parse plain text, not json, html, css

```python
import pprint
from typing import List  # if you usage python 3.8. If python 3.9+ - use build-in list

from scrape_schema import BaseSchema, Text, Sc, sc_param


TEXT = """
banana potato BANANA POTATO
-foo:10
-bar:20
lorem upsum dolor
192.168.0.1
"""


class MySchema(BaseSchema):
    ipv4: Sc[
        str, Text().re_search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")[1]
    ]
    failed_value: Sc[bool, Text(default=False).re_search(r"(ora)")[1]]
    digits: Sc[List[int], Text().re_findall(r"(\d+)")]
    digits_float: Sc[
        List[float],
        Text().re_findall(r"(\d+)").fn(lambda lst: [f"{s}.5" for s in lst])
    ]
    words_lower: Sc[List[str], Text().re_findall("([a-z]+)")]
    words_upper: Sc[List[str], Text().re_findall(r"([A-Z]+)")]



pprint.pprint(MySchema(TEXT).dict(), compact=True)
# {'digits': [10, 20, 192, 168, 0, 1],
#  'digits_float': [10.5, 20.5, 192.5, 168.5, 0.5, 1.5],
#  'failed_value': False,
#  'ipv4': '192.168.0.1',
#  'words_lower': ['banana', 'potato', 'foo', 'bar', 'lorem', 'upsum', 'dolor'],
#  'words_upper': ['BANANA', 'POTATO']}
```

### JMESPath
This field provide `parsel.Selector().JMESPath` and special methods and auto_type feature is disabled

!!! tip
    This field useful for parse json

```python
from typing import List, Optional
import pprint

from scrape_schema import BaseSchema, Sc, JMESPath

class JsonSchema(BaseSchema):
    args: Sc[List[str], JMESPath().jmespath("args").getall()]
    headers: Sc[dict, JMESPath().jmespath("headers").get()]
    url: Sc[Optional[str], JMESPath(default=None).jmespath("url").get()]

if __name__ == '__main__':
    text = '{"args": ["spam", "egg"], "headers": {"user-agent": "Mozilla 5.0", "lang": "en-US"}}'
    pprint.pprint(JsonSchema(text).dict(), compact=True)
    # {'args': ['spam', 'egg'],
    #  'headers': {'lang': 'en-US', 'user-agent': 'Mozilla 5.0'},
    #  'url': None}
```

### Nested
Splits a html to parts by a given field and creates additional nested schemas. `Sc` (Annotated) first argument should be
`BaseSchema` or `list[BaseSchema]` type

```python
import pprint

from scrape_schema import BaseSchema, Nested, Parsel, Sc, sc_param


class SubSchema(BaseSchema):
    item: Sc[str, Parsel().xpath("//p/text()").get()]
    price: Sc[int, Parsel().xpath("//div[@class='price']/text()").get()]
    _available: Sc[
        str,
        Parsel().xpath("//div[contains(@class, 'available')]").attrib.get(key="class"),
    ]

    @sc_param
    def available(self) -> bool:
        return "yes" in self._available


class Schema(BaseSchema):
    first_item: Sc[SubSchema, Nested(Parsel().xpath("//ul").xpath("./li")[0])]
    last_item: Sc[SubSchema, Nested(Parsel().xpath("//ul").xpath("./li")[-1])]
    items: Sc[list[SubSchema], Nested(Parsel().xpath("//body/ul").xpath("./li"))]

    @sc_param
    def max_price_item(self):
        return max(self.items, key=lambda obj: obj.price)


text = """
<html>
    <body>
        <ul>
            <li>
                <p>audi</p>
                <div class="price">10000</div>
                <div class="available yes"></div>
            </li>
            <li>
                <p>ferrari</p>
                <div class="price">99999999</div>
                <div class="available no"></div>
            </li>
            <li>
                <p>bentley</p>
                <div class="price">50000</div>
                <div class="available yes"></div>
            </li>
            <li>
                <p>ford</p>
                <div class="price">20000</div>
                <div class="available yes"></div>
            </li>
            <li>
                <p>suzuki</p>
                <div class="price">25000</div>
                <div class="available yes"></div>
            </li>
        </ul>
    </body>
</html>
"""

pprint.pprint(Schema(text).dict(), compact=True)
# {'first_item': {'available': True, 'item': 'audi', 'price': 10000},
#  'items': [{'available': True, 'item': 'audi', 'price': 10000},
#            {'available': False, 'item': 'ferrari', 'price': 99999999},
#            {'available': True, 'item': 'bentley', 'price': 50000},
#            {'available': True, 'item': 'ford', 'price': 20000},
#            {'available': True, 'item': 'suzuki', 'price': 25000}],
#  'last_item': {'available': True, 'item': 'suzuki', 'price': 25000},
#  'max_price_item': {'available': False, 'item': 'ferrari', 'price': 99999999}}
```

### sc_param
property descriptor for dict() view. Useful for additional conversion or reuse of a value from a field

```python
import pprint

from parsel import Selector
from scrape_schema import BaseSchema, Sc, Parsel, sc_param


class Schema(BaseSchema):
    url_path: Sc[str, Parsel().xpath("//a/@href").get()]
    _raw_tag: Sc[Selector, Parsel(auto_type=False).xpath("//div")[0]]

    @sc_param
    def div(self):
        return {"class": self._raw_tag.attrib.get('class'),
                "text": self._raw_tag.xpath(".//text()").get()}

    @sc_param
    def url(self):
        return f"https://example.com/{self.url_path}"

    @sc_param
    def foo(self):
        return "foo"

    @property
    def bar(self):  # this property not return from dict() method
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
## Special methods
All fields contain special methods -> shortcut functions to convert values

### fn
- function: Callable[..., Any]
Execute function for prev method chain and return result

```python
from scrape_schema import BaseSchema, Sc, Parsel


class Schema(BaseSchema):
    png_images: Sc[list[str], (Parsel()
                               .xpath("//img/@src")
                               .getall()
                               .fn(
        lambda lst: [i for i in lst if i.endswith('.png')])
    )]


text = """<img src="/one.png">
<img src="/two.gif">
<img src="/three.jpg">
<img src="/real_png.png">"""
print(Schema(text).dict())
# {'png_images': ['/one.png', '/real_png.png']}
```

### concat_l
- left_string: str
concat new string to left. Last chain method result should be string"""

```python
from scrape_schema import BaseSchema, Sc, Parsel

class Schema(BaseSchema):
    png_images: Sc[list[str], (Parsel()
                               .xpath("//img/@src")
                               .getall()
                               .concat_l("https://example.com"))]
    url: Sc[str, (Parsel()
                  .xpath("//a/@href")
                  .get()
                  .concat_l("https://example.com"))]

text = """<img src="/one.png">
<img src="/two.gif">
<img src="/three.jpg">
<img src="/real_png.png">
<a href="/login">"""
print(Schema(text).dict())
# {'png_images': ['https://example.com/one.png', 'https://example.com/two.gif',
# 'https://example.com/three.jpg', 'https://example.com/real_png.png'],
# 'url': 'https://example.com/login'}

```
### concat_r
- right_string: str
concat new string to right. Last chain method result should be string

```python
from scrape_schema import BaseSchema, Sc, Parsel


class Schema(BaseSchema):
    item: Sc[str, Parsel().xpath("//div[@class='item']/text()").get()]
    price_str: Sc[str, (Parsel()
                        .xpath("//div[@class='price']/text()")
                        .get()
                        .concat_r(" $"))]

    # convert str float directly to int raise ValueError: invalid literal for int() with base 10: '500.0'
    price_int: Sc[int, (Parsel()
                        .xpath("//div[@class='price']/text()")
                        .get()
                        .fn(float))]

text = """<div class="item">low orbit ion cannon</p>
<div class="price">500.0</div>"""
print(Schema(text).dict())
# {'item': 'low orbit ion cannon\n', 'price_str': '500.0 $', 'price_int': 500}

```
### sc_replace
- old: str,
- new: str,
- count: int = -1
replace string method. Last chain method result should be string

```python
from scrape_schema import BaseSchema, Sc, Parsel


class Schema(BaseSchema):
    item: Sc[str, Parsel().xpath("//div[@class='item']/text()").get()]
    price: Sc[int, (Parsel()
                    .xpath("//div[@class='price']/text()")
                    .get()
                    .sc_replace("$", ""))]

text = """<div class="item">low orbit ion cannon</p>
<div class="price">500$</div>"""
print(Schema(text).dict())
# {'item': 'low orbit ion cannon\n', 'price': 500}
```

### re_search
simular `re.search` function. Last chain method result should be return string.

!!! note
    Recommended usage this method with string values. if you works with Selector type, usage `re` method

### re_findall
Simular `[match for match in re.finditer()]` method. Last chain method result should be return string.

!!! note
    Recommended usage this method with string values. if you works with Selector type, usage `re` method

### chompjs_parse
Simular [chompjs.parse_js_object()](https://github.com/Nykakin/chompjs) method.
Last chain method result should be return string

!!! note
    **Cast typing feature will work unpredictably with chompjs output, disable is recommended
    set `Parsel(auto_type=False)`**

```python
from typing import Any, TypedDict
import pprint
from scrape_schema import BaseSchema, Parsel, Sc, sc_param

# optionally, you can write TypedDict type for chomp_js output annotation
# or use `dict[str, Any]`
ResultDict = TypedDict(
    "ResultDict", {"key": str, "values": list[int], "layer1": dict[str, Any]}
)


class ChompJSAddon(BaseSchema):
    # auto_type will work unpredictably with chompjs output, disable is recommended
    result: Sc[
        ResultDict,
        Parsel(auto_type=False).xpath("//script/text()").get().chomp_js_parse(),
    ]

    @sc_param
    def typed_result(self) -> ResultDict:
        return self.result

    @sc_param
    def key(self) -> str:
        return self.result["key"]

    @sc_param
    def values(self) -> list[int]:
        return self.result["values"]


if __name__ == '__main__':
    text = """
     <script>
                var sampleParams = Sandbox.init(
                {"key": "spam", "values": [1,2,3,4,5], "layer1": {"layer2": {"layer3": [null, null, true, false]}}}
                );
    </script>
    """

    pprint.pprint(ChompJSAddon(text).dict(), compact=True)
    # {'key': 'spam',
    #  'result': {'key': 'spam',
    #             'layer1': {'layer2': {'layer3': [None, None, True, False]}},
    #             'values': [1, 2, 3, 4, 5]},
    #  'typed_result': {'key': 'spam',
    #                   'layer1': {'layer2': {'layer3': [None, None, True, False]}},
    #                   'values': [1, 2, 3, 4, 5]},
    #  'values': [1, 2, 3, 4, 5]}
```

### chompjs_parse_all
Simular [chompjs.parse_js_objects()](https://github.com/Nykakin/chompjs) method.
Last chain method result should be return string

## Validation
You can check the markup argument before initialization. And if the check fails, it will throw
`SchemaPreValidationError`
```python
from scrape_schema import BaseSchema, Parsel
from scrape_schema.validator import markup_pre_validator


class Schema(BaseSchema):
    text: str = Parsel().css("h1::text").get()

    @markup_pre_validator()
    def validate(self) -> bool:
        # manual pre-validate rule
        return self.__selector__.xpath("//h1/text()").get() == "Hello, Parsel!"



Schema("<h1>Hello, Parsel!</h1>")  # OK
Schema("<h1>spam egg</h1>")  # raise SchemaPreValidationError
```

Also, you can pass query to decorator:

```python
from scrape_schema import BaseSchema, Parsel
from scrape_schema.validator import markup_pre_validator
from scrape_schema.exceptions import SchemaPreValidationError


class ValidateSchemaXpath(BaseSchema):
    title: str = Parsel().xpath("//title/text()").get()

    @markup_pre_validator(xpath="//title")
    def validate(self):
        return True


class ValidateSchemaCss(BaseSchema):
    title: str = Parsel().xpath("//title/text()").get()

    @markup_pre_validator(css="title")
    def validate(self):
        return True


class ValidateSchemaRe(BaseSchema):
    title: str = Parsel().xpath("//title/text()").get()

    @markup_pre_validator(pattern=r"<title>.*?</title>")
    def validate(self):
        return True


if __name__ == '__main__':
    text = "<title>hello, scrape-schema!</title>"
    text_2 = "<h1>hello, scrape-schema!</h1>"
    # passed validation
    print(ValidateSchemaXpath(text).dict())
    print(ValidateSchemaCss(text).dict())
    print(ValidateSchemaRe(text).dict())
    # failed
    try:
        ValidateSchemaXpath(text_2)
    except SchemaPreValidationError:
        print("failed")
    try:
        ValidateSchemaCss(text_2)
    except SchemaPreValidationError:
        print("failed")
    try:
        ValidateSchemaRe(text_2)
    except SchemaPreValidationError:
        print("failed")
# {'title': 'hello, scrape-schema!'}
# {'title': 'hello, scrape-schema!'}
# {'title': 'hello, scrape-schema!'}
# failed
# failed
# failed
```
- _new 0.5.2_

## Tips

### raw text parse (regex)
parsel.Selector is designed to work with xml/html documents and wraps it in a tag when passing raw text:

`<html><body><p>%TEXT%</p></body></html>`

There are several ways to get text:
- `Parsel().css("body > p::text")`
- `Parsel().xpath("//body/p/text()")`
- shortcut `Parsel(raw=True)`
- shortcut `Parsel().raw_text`
- `Text()` field

> `re` method belongs to the Selector object, use **re_search** or **re_findall**
