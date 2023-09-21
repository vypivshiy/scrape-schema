# Fields

## Default value handling
This is a demonstration of what happens if the value is not found in field

```python
from typing import Optional, List

from scrape_schema import BaseSchema, Parsel


class DefaultsExamples(BaseSchema):
    # handle error, set None
    failed_1: Optional[str] = Parsel(default=None).xpath("//title").get().sc_replace("0", "1", 1)
    # None
    failed_2: Optional[str] = Parsel().xpath("//title").get()
    # "fail:
    failed_3: str = Parsel(default="fail").xpath("//title").get().sc_replace("0", "1", 1)
    # []
    failed_4: List[str] = Parsel().xpath("//a").getall()
    # None
    failed_5: Optional[List[str]] = Parsel(default=None).xpath("//a").getall()


class RaisesSchema(BaseSchema):
    # no provide default - throw error
    this_raise_err: str = Parsel().xpath("//title").get().sc_replace("0", "1", 1)


if __name__ == '__main__':
    print(DefaultsExamples("").dict())
    # {'failed_1': None, 'failed_2': None,
    # 'failed_3': 'fail', 'failed_4': [], 'failed_5': None}
    RaisesSchema("")
    # AttributeError: 'NoneType' object has no attribute 'replace'
```


## Parsel
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

## Text
This field provide raw text parse methods and provide special methods and useful
for parse text.

!!! note
    lxml (parsel backend) is designed to work with xml/html documents and wraps it in a tag when
    passing raw text to next construction:

    `<html><body><p>%TEXT%</p></body></html>`

    There are several ways to get raw text:

    - `Parsel().css("body > p::text").get()`

    - `Parsel().xpath("//body/p/text()").get()`

    - shortcut `Parsel(raw=True)`

    - shortcut `Parsel().raw_text`

    - usage `Text()` field

    > `re` method belongs to the Selector object, use **re_search** or **re_findall**


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

## JMESPath
This field provide `parsel.Selector().JMESPath` and special methods and auto_type
feature is disabled and useful for parse json


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

## Nested
Splits a html to parts by a given field and creates additional nested schemas.
!!! note
    `Sc` (Annotated) first type argument should be
    `BaseSchema`, `list[BaseSchema]` or `List[BaseSchema]` type

```python
import pprint
from typing import List

from scrape_schema import BaseSchema, Nested, Parsel, Sc, sc_param


class Item(BaseSchema):
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
    # attribute style:
    # first_item: Item = Nested(Parsel().xpath("//ul").xpath("./li")[0])
    first_item: Sc[Item, Nested(Parsel().xpath("//ul").xpath("./li")[0])]
    last_item: Sc[Item, Nested(Parsel().xpath("//ul").xpath("./li")[-1])]
    items: Sc[List[Item], Nested(Parsel().xpath("//body/ul").xpath("./li"))]

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

## Callback
Provide invoke functions. Useful for auto set UUID, counter, etc. Support SpecialMethods.
Callback function should be not accept arguments.
Your best friends for this field:

- [itertools](https://docs.python.org/3.10/library/itertools.html)
- [functools.partial](https://docs.python.org/3.10/library/functools.html?highlight=functools#functools.partial)
- lambda functions or any simple functions

```python
import random

from scrape_schema import BaseSchema, Callback
from uuid import uuid4
from string import ascii_lowercase
from itertools import count
from functools import partial


def _random_word(len_=16) -> str:
    return "".join(random.choices(population=ascii_lowercase, k=len_))


# create a simple counter
counter = count(1)
my_counter = partial(lambda: next(counter))


# also you can set alias for reuse
FieldUUID4 = Callback(lambda: str(uuid4()))


class CallbackSchema(BaseSchema):
    num: int = Callback(my_counter)
    # not need init alias. same as uuid argument
    uuid: str = FieldUUID4
    # same as
    # uuid: str = Callback(lambda: str(uuid4()))

    word: str = Callback(_random_word)
    # also Callback field support SpecialMethod functions
    long_word: str = Callback(partial(_random_word, 32)).concat_l("LONG: ")


print(CallbackSchema("").dict())
print(CallbackSchema("").dict())
print(CallbackSchema("").dict())
# {'num': 1, 'uuid': 'a6b5be7a-1f6e-4f37-bfc3-9cfba36ed9f0', 'word': 'lftxzhxsfktwxrzs',
# 'long_word': 'LONG: begxplujskfeeriivqqbdbqakcfnlvtm'}
# {'num': 2, 'uuid': 'b41de697-4c73-4f08-9d53-4c62adc3e506', 'word': 'ylkdunpqxvyevzzf',
# 'long_word': 'LONG: uvtllkxetatsrsqwauiovqpbwiqvswoh'}
# {'num': 3, 'uuid': '457c7ecc-adbe-447e-b914-9a5e3c22af7a', 'word': 'zjrtgxtaraihhngw',
# 'long_word': 'LONG: wzsjvqcvwyydqgiichhohtwagzlajter'}
```

- new in 0.5.5

## Special methods
All fields contain special methods - shortcut functions for convert values in field objects.

### fn
- function: Callable[[Any], Any]
Execute function for prev method chain and return result

```python
# parse only png images
from scrape_schema import BaseSchema, Sc, Parsel


class Schema(BaseSchema):
    # extract only '.png' images
    png_images: Sc[list[str], (
        Parsel().xpath("//img/@src").getall().fn(
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
concat new string to left. Last chain method result should be a string"""

```python
from scrape_schema import BaseSchema, Sc, Parsel


class Schema(BaseSchema):
    # add https://example.com string to result
    png_images: Sc[list[str], (
        Parsel().xpath("//img/@src").getall()
        .concat_l("https://example.com")
    )]
    url: Sc[str, (
        Parsel().xpath("//a/@href").get()
        .concat_l("https://example.com")
    )]

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
concat new string to right. **Last chain method result should be a string**

```python
from scrape_schema import BaseSchema, Sc, Parsel


class Schema(BaseSchema):
    item: Sc[str, Parsel().xpath("//div[@class='item']/text()").get()]
    # add $ char to result
    price_str: Sc[str, (
        Parsel().xpath("//div[@class='price']/text()").get()
        .concat_r(" $"))]
    # convert str float directly to int raise ValueError:
    # invalid literal for int() with base 10: '500.0'
    price_int: Sc[int, (
        Parsel().xpath("//div[@class='price']/text()").get()
        .fn(float))]

text = """<div class="item">low orbit ion cannon</p>
<div class="price">500.0</div>"""
print(Schema(text).dict())
# {'item': 'low orbit ion cannon\n', 'price_str': '500.0 $', 'price_int': 500}
```

### sc_replace
Replace string method. **Last chain method result should be a string**
- old: str,
- new: str,
- count: int = -1

```python
from scrape_schema import BaseSchema, Sc, Parsel


class Schema(BaseSchema):
    item: Sc[str, Parsel().xpath("//div[@class='item']/text()").get()]
    # remove $ char from result
    price: Sc[int, (
        Parsel().xpath("//div[@class='price']/text()").get()
        .sc_replace("$", ""))]

text = """<div class="item">low orbit ion cannon</p>
<div class="price">500$</div>"""
print(Schema(text).dict())
# {'item': 'low orbit ion cannon\n', 'price': 500}
```

### re_search
simular `re.search` function. Last chain method result should be return string.

!!! note
    This method is for use on string values.
    If last method value returns `Selector` object - usage `re` method

### re_findall
Simular `[match for match in re.finditer()]` method. Last chain method result should be return string.

!!! note
    This method is for use on string values.
    If last method value returns `Selector` object - usage `re` method

### chompjs_parse
Simular [chompjs.parse_js_object()](https://github.com/Nykakin/chompjs) method.

!!! note
    Last chain method result should be return string.

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

    # works with chompjs output example

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

!!! note
    Last chain method result should be return string

    **Cast typing feature will work unpredictably with chompjs output, disable is recommended
    set `Parsel(auto_type=False)`**