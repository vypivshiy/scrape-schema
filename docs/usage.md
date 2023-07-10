# Quickstart
The fields interface is similar to the [original parsel](https://parsel.readthedocs.io/en/latest/)

> Example from parsel documentation
```
>>> from parsel import Selector
>>> text = """
        <html>
            <body>
                <h1>Hello, Parsel!</h1>
                <ul>
                    <li><a href="http://example.com">Link 1</a></li>
                    <li><a href="http://scrapy.org">Link 2</a></li>
                </ul>
                <script type="application/json">{"a": ["b", "c"]}</script>
            </body>
        </html>"""
>>> selector = Selector(text=text)
>>> selector.css('h1::text').get()
'Hello, Parsel!'
>>> selector.xpath('//h1/text()').re(r'\w+')
['Hello', 'Parsel']
>>> for li in selector.css('ul > li'):
...     print(li.xpath('.//@href').get())
http://example.com
http://scrapy.org
>>> selector.css('script::text').jmespath("a").get()
'b'
>>> selector.css('script::text').jmespath("a").getall()
['b', 'c']
```


> Same solution, but in scrape-schema
```python
from scrape_schema import BaseSchema, Parsel, Sc


class Schema(BaseSchema):
    h1: Sc[str, Parsel().css('h1::text').get()]
    words: Sc[list[str], Parsel().xpath('//h1/text()').re(r'\w+')]
    urls: Sc[list[str], Parsel().css('ul > li').xpath('.//@href').getall()]
    sample_jmespath_1: Sc[str, Parsel().css('script::text').jmespath("a").get()]
    sample_jmespath_2: Sc[list[str], Parsel().css('script::text').jmespath("a").getall()]


text = """
        <html>
            <body>
                <h1>Hello, Parsel!</h1>
                <ul>
                    <li><a href="http://example.com">Link 1</a></li>
                    <li><a href="http://scrapy.org">Link 2</a></li>
                </ul>
                <script type="application/json">{"a": ["b", "c"]}</script>
            </body>
        </html>"""

print(Schema(text).dict())
# {'h1': 'Hello, Parsel!',
# 'words': ['Hello', 'Parsel'],
# 'urls': ['http://example.com', 'http://scrapy.org'],
# 'sample_jmespath_1': 'b',
# 'sample_jmespath_2': ['b', 'c']}
```


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

> typing.Annotated does not guarantee type correctness at runtime, it is intended to indicate to 
> the static type checker and IDE the intended type.

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
    d: Annotated[list[dict[str, int]], spam(float("inf"))]  # mypy OK
```

## Features

### logging
for config or disable logging get logger by `scrape_schema` name
```python
import logging
logger = logging.getLogger("scrape_schema")
logger.setLevel(logging.DEBUG)
...
```
### BaseSchema
base schema-like class 

Params:

- text - bytes, str or Selector object

### Parsel
Field for pulling values from html. Methods have a similar interface to `parsel.Selector`.
params:

- raw - if you works with raw text (not HTML), automatically accept xpath(//p/text()).get() methods
- auto_type automatically type-cast from first annotated argument. Default True.
- default - default value. If during operation it throws an error or does not find a value, 
it will set it (without type conversion). If it is not specified, it will throw exception. 

### Nested
Splits a html by a given field and creates additional nested schemas. `Sc` (Annotated) first argument should be
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
## Extra Field buildin methods
### fn
- function: Callable[..., Any] 
execute function for prev method chain and return result

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

> Recommended usage this method with string values. if you works with Selector type, usage `re` method

- pattern: Union[str, Pattern[str]]
- flags: Union[int, RegexFlag] = 0, 
- groupdict: bool = False - accept groupdict method. if pattern not contain `named groups` - raise TypeError
    ) -> Self:
re.search method for text result.

### re_findall
Simular `[match for match in re.finditer()]` method. Last chain method result should be return string.
- pattern: Union[str, Pattern[str]],
- flags: Union[int, RegexFlag] = 0,
- groupdict: bool = False - accept `groupdict` method. pattern required named groups. default False
- 
> Recommended usage this method with string values. if you works with Selector type, usage `re` method

### chompjs_parse
Simular [chompjs.parse_js_object()](https://github.com/Nykakin/chompjs) method. 
Last chain method result should be return string

> **Cast typing feature will work unpredictably with chompjs output, disable is recommended
> set `Parsel(auto_type=False)`**
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

## Cases
### html

```python
from scrape_schema import BaseSchema, Parsel, Sc
```

### raw text parse (regex)
parsel.Selector is designed to work with xml/html documents and wraps it in a tag when passing raw text:

`<html><body><p>%TEXT%</p></body></html>`

There are several ways to get text:
- `Parsel().css("body > p::text")`
- `Parsel().xpath("//p/text()")`
- shortcut `Parsel(raw=True)` 
- shortcut `Parsel().raw_text`

> `re` method belongs to the Selector object, use **re_search** or **re_findall**

```python
from typing import List
import pprint

from scrape_schema import BaseSchema, Parsel, Sc, sc_param


class MySchema(BaseSchema):
    ipv4: Sc[str, (Parsel(raw=True)
                    .re_search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")[1])]
    failed_value: Sc[bool, (Parsel(default=False, raw=True)
                            .re_search(r"(ora)")[1])]
    # digits: Sc[List[int], Parsel(raw=True).re(r"(\d+)")  # throw error
    digits: Sc[List[int], Parsel(raw=True).re_findall(r"(\d+)")]
    digits_float: Sc[List[float], (Parsel(raw=True)
                                   .re_findall(r"(\d+)")
                                   .fn(lambda lst: [f"{s}.5" for s in lst]))]
    words_lower: Sc[List[str], (Parsel(raw=True)
                                .re_findall("([a-z]+)"))]
    words_upper: Sc[List[str], (Parsel(raw=True)
                                .re_findall(r"([A-Z]+)"))]

    @sc_param
    def sum(self):
        return sum(self.digits)

    @sc_param
    def all_words(self):
        return self.words_lower + self.words_upper


TEXT = """
banana potato BANANA POTATO
-foo:10
-bar:20
lorem upsum dolor
192.168.0.1
"""

pprint.pprint(MySchema(TEXT).dict(), compact=True)
# {'all_words': ['banana', 'potato', 'foo', 'bar', 'lorem', 'upsum', 'dolor',
#                'BANANA', 'POTATO'],
#  'digits': [10, 20, 192, 168, 0, 1],
#  'digits_float': [10.5, 20.5, 192.5, 168.5, 0.5, 1.5],
#  'failed_value': False,
#  'ipv4': '192.168.0.1',
#  'sum': 391,
#  'words_lower': ['banana', 'potato', 'foo', 'bar', 'lorem', 'upsum', 'dolor'],
#  'words_upper': ['BANANA', 'POTATO']}
```
