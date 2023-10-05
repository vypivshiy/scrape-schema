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

### sc_parse
method stack call for parsing values

```python
from scrape_schema import Parsel, Text


Text().sc_parse("test")  # test
Parsel(raw=True).sc_parse("test")  # test
# lxml automatically wrap raw text to <body><p>%TEXT%</p></body> construction
Parsel().xpath('//body').get().sc_parse("test")  # <body><p>test</p></body>
Parsel().xpath("//a/@href").get().sc_parse('<a href="/example">scrape schema</a>')  # '/example'
```

### Scpecial methods cheat sheet

All methods accept from last chain value (usually, from `.get()` and `.getall()` methods if field is not raw text (`Text()`, `Parsel(raw=True)`, `Parsel().raw_text`)

| method             | description                                                                         | example                                                                                       | output                                                       |
|--------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| fn                 | Universal function handler. Accept only one argument - markup from last chain chain | `Text().fn(lambda v: f'{v} count={len(v)} {v}').sc_parse('scrape')`                           | `'count=5, scrape'`                                          |
| concat_l           | Add new string part to left                                                         | `Text().concat_l('schema ').sc_parse('scrape')`                                               | `'schema scrape'`                                            |
| concat_r           | Add new string part to left right                                                   | `Text().concat_r(' schema').sc_parse('scrape')`                                               | `'scrape schema'`                                            |
| replace            | Simular as build-in str.replace() method                                            | `Text().replace('a').sc_parse('scrape')`                                                      | `'scrpe'`                                                    |
| -                  | With limit replace                                                                  | `Text().replace('s', 1).sc_parse('ssscrape')`                                                 | `'sscrape'`                                                  |
| strip              | Simular as build-in str.strip() method                                              | `Text().strip().sc_parse('  scrape  ')`                                                       | `'scrape'`                                                   |
| rstip              | Simular as build-in str.rstrip() method                                             | `Text().rstrip().sc_parse(' scrape  ')`                                                       | `' scrape'`                                                  |
| lstrip             | Simular as build-in str.lstrip() method                                             | `Text().lstrip().sc_parse('   scrape ')`                                                      | `'scrape '`                                                  |
| split              | Simular as str.split() method                                                       | `Text().split().sc_parse('scrape schema')`                                                    | `['scrape', 'schema']`                                       |
| -                  | If last chain list - throw TypeError                                                | `Text().split().split().sc_parse('scrape schema')`                                            | `TypeError`                                                  |
| join               | Simular as str.join() method. Last chain should be `list[str]`                      | `Text().split().join(', ').sc_parse('scrape schema')`                                         | `'scrape, schema'`                                           |
| lower              | Simular as str.lower(). Works with `list[str]`                                      | `Text().lower().sc_parse('SCRAPE SCHEMA)`                                                     | `'scrape schema'`                                            |
| upper              | Simular as str.upper(). Works with `list[str]`                                      | `Text().upper().sc_parse('scrape schema')`                                                    | `'SCRAPE SCHEMA'`                                            |
| capitalize         | Simular as str.capitalize(). Works with `list[str]`                                 | `Text().capitalize().sc_parse('scrape schema')`                                               | `'Scrape Schema'`                                            |
| count              | Calc count items. if last item is not list - return 1                               | `Text().split().count().sc_parse('scrape schema very cool')`                                  | `4`                                                          |
| -                  |                                                                                     | `Text().count().sc_parse('scrape schema')`                                                    | `1`                                                          |
| re_search          | Simular as re.search(...). **return pattern, don't remember get attribute!**        | `Text().re_search(r'(sc\w+)').sc_parse('scrape schema')[0]`                                   | `'scrape'`                                                   |
| -                  | Allowed named groups                                                                | `Text().re_search(r'(?P<who>sc\w+)', groupdict=True).sc_parse('scrape schema')`               | `{'who': 'scrape'}`                                          |
| -                  | Throw error if not set group                                                        | `Text().re_search(r'(sc\w+)', groupdict=True).sc_parse('scrape schema')`                      | `TypeError: groupdict required named groups`                 |
| re_findall         | Simular as [p for p in re.finditer(...)]                                            | `Text().re_findall(r'(sc\w+)').sc_parse('scrape schema scrappy oooo')`                        | `['scrape', 'schema', 'scrappy']`                            |
| -                  | Allowed named groups                                                                | `Text().re_findall(r'(?P<who>sc\w+)', groupdict=True).sc_parse('scrape schema scrappy oooo')` | `[{'who': 'scrape'}, {'who': 'schema'}, {'who': 'scrappy'}]` |
| -                  | Throw error if not set group                                                        | `Text().re_findall(r'(sc\w+)').sc_parse('scrape schema scrappy oooo')`                        | `TypeError: groupdict required named groups`                 |
| chomp_js_parse     | Simular as [chompjs](https://github.com/Nykakin/chompjs#features)                   | see examples                                                                                  | -                                                            |
| chomp_js_parse_all | Simular as [chompjs](https://github.com/Nykakin/chompjs#features)                   | see examples                                                                                  | -                                                            |
| `__getitem__`      | allow `__getitem__` protocol (index, slice, get key)                                | `Text().sc_parse('scrape')[0]`                                                                | `'s'`                                                        |
| -                  | get by slice example                                                                | `Text().sc_parse('scrape')[:3]`                                                               | `'scr'`                                                      |
| -                  | get by key example                                                                  | `Text().re_search(r'(?P<who>sc\w+)', groupdict=True).sc_parse('scrape schema')['who']`        | `'scrape'`                                                   |


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

## RawDLField
This field provide [Description List element tags (`<dl>`)](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dl) parse logic

!!! note
    this experimental field and in last updates maybe changed

- disabled auto_typing by default
- default value - empty dict
- raise TypeError if `<dl>` element not founded

Example:

```python
from typing import Any

from scrape_schema import BaseSchema
from scrape_schema.field import RawDLField


class DatalinesSchema1(BaseSchema):
    data: dict[str, Any] = RawDLField().css_dl()


class DatalinesSchema2(BaseSchema):
    # customize css queries. exclude .col-12 elements
    data: dict[str, Any] = RawDLField().css_dl(dl_css='div.info > dl.row',
                                               dt_css='dt.col-6',
                                               dd_css='dd.col-6')
    # custom enchants
    data2: dict[str, str] = RawDLField().css_dl(dl_css='div.info > dl.row',
                                                dt_css='dt.col-6',
                                                dd_css='dd.col-6',
                                                strip=True,
                                                str_join=', '
                                                )


if __name__ == '__main__':
    HTML_1 = """
    <dl>
    <dt>PHP</dt>
    <dd>A server side scripting language.</dd>
    <dt>JavaScript</dt>
    <dd>A client side scripting language.</dd>
    </dl>
    """

    HTML_2 = """
    <div class="info"><dl class="row">
        <dt class="col-12">keys</dt>
        <dd class="col-12">values</dd>
        <dd class="col-12"><hr></dd>
        <dt class="col-6">key1</dt>
        <dd class="col-6">value1 value2 FROM KEY1</dd>
        <dt class="col-6">items</dt>
        <dd class="col-6">
            <span>item 1</span>
            <span>item 2</span>
            <span>item 3</span>
            <span>item 4</span>
        </dd>
        <dt class="col-6">key2</dt>
        <dd class="col-6"></dd>
        <dt class="col-6">key3</dt>
        <dd class="col-6">value3</dd>
    """
    print(DatalinesSchema1(HTML_1).dict())
    # {'data': {'PHP': ['A server side scripting language.'], 'JavaScript': ['A client side scripting language.']}}

    print(DatalinesSchema2(HTML_2).dict())
    # {'data': {'key1': ['value1 value2 FROM KEY1'],
    # 'items': ['\n            ', 'item 1', ' \n            ', 'item 2',
    # ' \n            ', 'item 3', ' \n            ', 'item 4', ' \n        '],
    # 'key2': [],
    # 'key3': ['value3']},
    #
    # 'data2': {'key1': 'value1 value2 FROM KEY1',
    # 'items': ', item 1, , item 2, , item 3, , item 4,
    # ', 'key2': '',
    # 'key3': 'value3'}}
```

- new in 0.6.2

## RawTableField

This field provide [`<table>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table) elements parse logic


!!! note
    this experimental field and in last updates maybe changed


- auto_typing disabled
- if parse failed - return python dict `{"columns": [], "cells": [], "table": {}}` with empty values
    - `cells` Two-dimensional lists: for one row - one list with cells values (`<td>`)
    - `columns` - list with `<th>` values
    - `table` - try to accumulate `<th>` and `<td>` values to dict
- raise `TypeError` if element will be not founded.
- for better support typing - annotate by `scrape_schema.field.TableDictView` type

Examples:

```python
from scrape_schema.field import RawTableField


HTML = """
     <table>
      <tr>
        <th>Person 1</th>
        <th>Person 2</th>
        <th>Person 3</th>
      </tr>
      <tr>
        <td>Emil</td>
        <td>Tobias</td>
        <td>Linus</td>
      </tr>
      <tr>
        <td>16</td>
        <td>14</td>
        <td>10</td>
      </tr>
    </table>
    """

print(RawTableField().table().sc_parse(HTML))
# {'item': {'cells': [['Emil', 'Tobias', 'Linus'], ['16', '14', '10']],
#           'columns': ['Person 1', 'Person 2', 'Person 3'],
#           'table': {'Person 1': ['Emil', '16'],
#                     'Person 2': ['Tobias', '14'],
#                     'Person 3': ['Linus', '10']}}}
```

```python
from scrape_schema.field import RawTableField


HTML2 = """
    <table>
  <tr>
    <td>&nbsp;</td>
    <td>Knocky</td>
    <td>Flor</td>
    <td>Ella</td>
    <td>Juan</td>
  </tr>
  <tr>
    <td>Breed</td>
    <td>Jack Russell</td>
    <td>Poodle</td>
    <td>Streetdog</td>
    <td>Cocker Spaniel</td>
  </tr>
  <tr>
    <td>Age</td>
    <td>16</td>
    <td>9</td>
    <td>10</td>
    <td>5</td>
  </tr>
  <tr>
    <td>Owner</td>
    <td>Mother-in-law</td>
    <td>Me</td>
    <td>Me</td>
    <td>Sister-in-law</td>
  </tr>
  <tr>
    <td>Eating Habits</td>
    <td>Eats everyone's leftovers</td>
    <td>Nibbles at food</td>
    <td>Hearty eater</td>
    <td>Will eat till he explodes</td>
  </tr>
</table>
    """
print(RawTableField().table().sc_parse(HTML2))
# this document exclude <th> elements, failed represent "table" key value
# {'item': {'cells': [['', 'Knocky', 'Flor', 'Ella', 'Juan'],
#                     ['Breed', 'Jack Russell', 'Poodle', 'Streetdog',
#                      'Cocker Spaniel'],
#                     ['Age', '16', '9', '10', '5'],
#                     ['Owner', 'Mother-in-law', 'Me', 'Me', 'Sister-in-law'],
#                     ['Eating Habits', "Eats everyone's leftovers",
#                      'Nibbles at food', 'Hearty eater',
#                      'Will eat till he explodes']],
#           'columns': [],
#           'table': {}}}
```

```python
from scrape_schema.field import RawTableField


HTML3 = """
    <table>
  <tr>
    <th>Animals</th>
  </tr>
  <tr>
    <th>Hippopotamus</th>
  </tr>
  <tr>
    <th>Horse</th>
    <td>Mare</td>
  </tr>
  <tr>
    <td>Stallion</td>
  </tr>
  <tr>
    <th>Crocodile</th>
  </tr>
  <tr>
    <th>Chicken</th>
    <td>Hen</td>
  </tr>
  <tr>
    <td>Rooster</td>
  </tr>
</table>
"""


print(RawTableField().table().sc_parse(HTML3))
#  in table field missing values stub by `None` value for save correct list len
# {'item': {'cells': [['Mare'], ['Stallion'], ['Hen'], ['Rooster']],
#           'columns': ['Animals', 'Hippopotamus', 'Horse', 'Crocodile',
#                       'Chicken'],
#           'table': {'Animals': ['Mare', 'Stallion', 'Hen', 'Rooster'],
#                     'Chicken':      [None, None, None, None],
#                     'Crocodile':    [None, None, None, None],
#                     'Hippopotamus': [None, None, None, None],
#                     'Horse':        [None, None, None, None]}
#                     }}
```

```python
# example extract value from https://en.wikipedia.org/wiki/Pythonidae table
from scrape_schema.field import RawTableField


HTML4 = """
    <table cellspacing="0" cellpadding="2" border="1" style="border-collapse: collapse;">

<tbody><tr>
<th style="background:#f0f0f0;">Genus<sup id="cite_ref-ITIS_2-1" class="reference"><a href="#cite_note-ITIS-2">[2]</a></sup>
</th>
<th style="background:#f0f0f0;">Taxon author<sup id="cite_ref-ITIS_2-2" class="reference"><a href="#cite_note-ITIS-2">[2]</a></sup>
</th>
<th style="background:#f0f0f0;">Species<sup id="cite_ref-ITIS_2-3" class="reference"><a href="#cite_note-ITIS-2">[2]</a></sup>
</th>
<th style="background:#f0f0f0;">Subsp.<sup id="cite_ref-13" class="reference"><a href="#cite_note-13">[a]</a></sup><sup id="cite_ref-ITIS_2-4" class="reference"><a href="#cite_note-ITIS-2">[2]</a></sup>
</th>
<th style="background:#f0f0f0;">Common name
</th>
<th style="background:#f0f0f0;">Geographic range<sup id="cite_ref-McD99_1-3" class="reference"><a href="#cite_note-McD99-1">[1]</a></sup>
</th></tr>
<tr>
<td><i><a href="/wiki/Antaresia" title="Antaresia">Antaresia</a></i>
</td>
<td>Wells &amp; Wellington, 1984
</td>
<td style="text-align:center;">4
</td>
<td style="text-align:center;">2
</td>
<td>Children's pythons
</td>
<td style="width:40%">Australia in arid and tropical regions
</td></tr>
<tr>
<td><i><a href="/wiki/Apodora" title="Apodora">Apodora</a></i><sup id="cite_ref-14" class="reference"><a href="#cite_note-14">[13]</a></sup>
</td>
<td>Kluge, 1993
</td>
<td style="text-align:center;">1
</td>
<td style="text-align:center;">0
</td>
<td>Papuan python
</td>
<td>Papua New Guinea
</td></tr>
<tr>
<td><i><a href="/wiki/Aspidites" title="Aspidites">Aspidites</a></i>
</td>
<td><a href="/wiki/Wilhelm_Peters" title="Wilhelm Peters">Peters</a>, 1877
</td>
<td style="text-align:center;">2
</td>
<td style="text-align:center;">0
</td>
<td>pitless pythons
</td>
<td>Australia, except in the southern parts of the country
</td></tr>
<tr>
<td><i>Bothrochilus</i>
</td>
<td><a href="/wiki/Leopold_Fitzinger" title="Leopold Fitzinger">Fitzinger</a>, 1843
</td>
<td style="text-align:center;">1
</td>
<td style="text-align:center;">0
</td>
<td><a href="/wiki/Bismarck_ringed_python" title="Bismarck ringed python">Bismarck ringed python</a>
</td>
<td>the Bismarck Archipelago
</td></tr>
<tr>
<td><i><a href="/wiki/Leiopython" title="Leiopython">Leiopython</a></i>
</td>
<td><a href="/wiki/Ambrosius_Hubrecht" title="Ambrosius Hubrecht">Hubrecht</a>, 1879
</td>
<td style="text-align:center;">3
</td>
<td style="text-align:center;">0
</td>
<td>white-lipped pythons
</td>
<td>Papua New Guinea
</td></tr>
<tr>
<td><i><a href="/wiki/Liasis" title="Liasis">Liasis</a></i>
</td>
<td><a href="/wiki/John_Edward_Gray" title="John Edward Gray">Gray</a>, 1842
</td>
<td style="text-align:center;">3
</td>
<td style="text-align:center;">5
</td>
<td>water pythons
</td>
<td><a href="/wiki/Indonesia" title="Indonesia">Indonesia</a> in the <a href="/wiki/Lesser_Sunda_Islands" title="Lesser Sunda Islands">Lesser Sunda Islands</a>, east through New Guinea and northern and western Australia
</td></tr>
<tr>
<td><i><a href="/wiki/Malayopython" title="Malayopython">Malayopython</a></i>
</td>
<td>Reynolds, 2014
</td>
<td style="text-align:center;">2
</td>
<td style="text-align:center;">3
</td>
<td>reticulated and Timor pythons
</td>
<td>from India to Timor
</td></tr>
<tr>
<td><i><a href="/wiki/Morelia_(snake)" title="Morelia (snake)">Morelia</a></i>
</td>
<td>Gray, 1842
</td>
<td style="text-align:center;">6
</td>
<td style="text-align:center;">7
</td>
<td>tree pythons
</td>
<td>from Indonesia in the <a href="/wiki/Maluku_Islands" title="Maluku Islands">Maluku Islands</a>, east through New Guinea, including the Bismarck Archipelago, and Australia
</td></tr>
<tr>
<td><i>Nyctophilopython</i>
</td>
<td>Gow, 1977
</td>
<td style="text-align:center;">1
</td>
<td style="text-align:center;">0
</td>
<td><a href="/wiki/Oenpelli_python" title="Oenpelli python">Oenpelli python</a>
</td>
<td style="width:40%">the Northern Territory, Australia
</td></tr>
<tr>
<td><i><a href="/wiki/Python_(genus)" title="Python (genus)">Python</a></i><sup id="cite_ref-15" class="reference"><a href="#cite_note-15">[b]</a></sup>
</td>
<td><a href="/wiki/Fran%C3%A7ois_Marie_Daudin" title="François Marie Daudin">Daudin</a>, 1803
</td>
<td style="text-align:center;">10
</td>
<td style="text-align:center;">1
</td>
<td>true pythons
</td>
<td>Africa in the tropics south of the <a href="/wiki/Sahara" title="Sahara">Sahara Desert</a> (not including southern and extreme southwestern <a href="/wiki/Madagascar" title="Madagascar">Madagascar</a>), <a href="/wiki/Bangladesh" title="Bangladesh">Bangladesh</a>, Pakistan, India, <a href="/wiki/Sri_Lanka" title="Sri Lanka">Sri Lanka</a>, the <a href="/wiki/Nicobar_Islands" title="Nicobar Islands">Nicobar Islands</a>, <a href="/wiki/Burma" class="mw-redirect" title="Burma">Burma</a>, <a href="/wiki/Indochina" class="mw-redirect" title="Indochina">Indochina</a>, southern China, <a href="/wiki/Hong_Kong" title="Hong Kong">Hong Kong</a>, <a href="/wiki/Hainan" title="Hainan">Hainan</a>, the Malayan region of <a href="/wiki/Indonesia" title="Indonesia">Indonesia</a> and the <a href="/wiki/Philippines" title="Philippines">Philippines</a>
</td></tr>
<tr>
<td><i><a href="/wiki/Simalia" title="Simalia">Simalia</a></i>
</td>
<td>Gray, 1849
</td>
<td style="text-align:center;">6
</td>
<td style="text-align:center;">0
</td>
<td>amethystine python species complex
</td>
<td>found in Indonesia (Including the islands of <a href="/wiki/Halmahera" title="Halmahera">Halmahera</a>, <a href="/wiki/Ambon_Island" title="Ambon Island">Ambon</a>, <a href="/wiki/Seram_Island" title="Seram Island">Seram</a>, <a href="/wiki/Maluku_Islands" title="Maluku Islands">Maluku</a>), the <a href="/wiki/Northern_Territory" title="Northern Territory">Northern Territory</a>, northeastern <a href="/wiki/Queensland" title="Queensland">Queensland</a> into the <a href="/wiki/Torres_Strait" title="Torres Strait">Torres Strait</a>, and <a href="/wiki/Papua_New_Guinea" title="Papua New Guinea">Papua New Guinea</a>
</td></tr></tbody></table>
    """


print(RawTableField().table().sc_parse(HTML4))
# {'item': {'cells': [['Antaresia ', 'Wells & Wellington, 1984', '4', '2',
#                      "Children's pythons",
#                      'Australia in arid and tropical regions'],
#                     ['Apodora [13] ', 'Kluge, 1993', '1', '0', 'Papuan python',
#                      'Papua New Guinea'],
#                     ['Aspidites ', 'Peters , 1877', '2', '0', 'pitless pythons',
#                      'Australia, except in the southern parts of the country'],
#                     ['Bothrochilus ', 'Fitzinger , 1843', '1', '0',
#                      'Bismarck ringed python ', 'the Bismarck Archipelago'],
#                     ['Leiopython ', 'Hubrecht , 1879', '3', '0',
#                      'white-lipped pythons', 'Papua New Guinea'],
#                     ['Liasis ', 'Gray , 1842', '3', '5', 'water pythons',
#                      'Indonesia in the Lesser Sunda Islands , east through New '
#                      'Guinea and northern and western Australia'],
#                     ['Malayopython ', 'Reynolds, 2014', '2', '3',
#                      'reticulated and Timor pythons', 'from India to Timor'],
#                     ['Morelia ', 'Gray, 1842', '6', '7', 'tree pythons',
#                      'from Indonesia in the Maluku Islands , east through New '
#                      'Guinea, including the Bismarck Archipelago, and '
#                      'Australia'],
#                     ['Nyctophilopython ', 'Gow, 1977', '1', '0',
#                      'Oenpelli python ', 'the Northern Territory, Australia'],
#                     ['Python [b] ', 'Daudin , 1803', '10', '1', 'true pythons',
#                      'Africa in the tropics south of the Sahara Desert (not '
#                      'including southern and extreme southwestern Madagascar '
#                      '), Bangladesh , Pakistan, India, Sri Lanka , the Nicobar '
#                      'Islands , Burma , Indochina , southern China, Hong Kong '
#                      ', Hainan , the Malayan region of Indonesia and the '
#                      'Philippines '],
#                     ['Simalia ', 'Gray, 1849', '6', '0',
#                      'amethystine python species complex',
#                      'found in Indonesia (Including the islands of Halmahera , '
#                      'Ambon , Seram , Maluku ), the Northern Territory , '
#                      'northeastern Queensland into the Torres Strait , and '
#                      'Papua New Guinea ']],
#           'columns': ['Genus [2] ', 'Taxon author [2] ', 'Species [2] ',
#                       'Subsp. [a] [2] ', 'Common name',
#                       'Geographic range [1] '],
#           'table': {'Common name': ["Children's pythons", 'Papuan python',
#                                     'pitless pythons',
#                                     'Bismarck ringed python ',
#                                     'white-lipped pythons', 'water pythons',
#                                     'reticulated and Timor pythons',
#                                     'tree pythons', 'Oenpelli python ',
#                                     'true pythons',
#                                     'amethystine python species complex'],
#                     'Genus [2] ': ['Antaresia ', 'Apodora [13] ', 'Aspidites ',
#                                    'Bothrochilus ', 'Leiopython ', 'Liasis ',
#                                    'Malayopython ', 'Morelia ',
#                                    'Nyctophilopython ', 'Python [b] ',
#                                    'Simalia '],
#                     'Geographic range [1] ': ['Australia in arid and tropical '
#                                               'regions',
#                                               'Papua New Guinea',
#                                               'Australia, except in the '
#                                               'southern parts of the country',
#                                               'the Bismarck Archipelago',
#                                               'Papua New Guinea',
#                                               'Indonesia in the Lesser Sunda '
#                                               'Islands , east through New '
#                                               'Guinea and northern and western '
#                                               'Australia',
#                                               'from India to Timor',
#                                               'from Indonesia in the Maluku '
#                                               'Islands , east through New '
#                                               'Guinea, including the Bismarck '
#                                               'Archipelago, and Australia',
#                                               'the Northern Territory, '
#                                               'Australia',
#                                               'Africa in the tropics south of '
#                                               'the Sahara Desert (not '
#                                               'including southern and extreme '
#                                               'southwestern Madagascar ), '
#                                               'Bangladesh , Pakistan, India, '
#                                               'Sri Lanka , the Nicobar Islands '
#                                               ', Burma , Indochina , southern '
#                                               'China, Hong Kong , Hainan , the '
#                                               'Malayan region of Indonesia and '
#                                               'the Philippines ',
#                                               'found in Indonesia (Including '
#                                               'the islands of Halmahera , '
#                                               'Ambon , Seram , Maluku ), the '
#                                               'Northern Territory , '
#                                               'northeastern Queensland into '
#                                               'the Torres Strait , and Papua '
#                                               'New Guinea '],
#                     'Species [2] ': ['4', '1', '2', '1', '3', '3', '2', '6',
#                                      '1', '10', '6'],
#                     'Subsp. [a] [2] ': ['2', '0', '0', '0', '0', '5', '3', '7',
#                                         '0', '1', '0'],
#                     'Taxon author [2] ': ['Wells & Wellington, 1984',
#                                           'Kluge, 1993', 'Peters , 1877',
#                                           'Fitzinger , 1843', 'Hubrecht , 1879',
#                                           'Gray , 1842', 'Reynolds, 2014',
#                                           'Gray, 1842', 'Gow, 1977',
#                                           'Daudin , 1803', 'Gray, 1849']}}}

```

- new in 0.6.2
