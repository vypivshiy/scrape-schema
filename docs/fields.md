# Fields
This page contains field descriptions with examples.

# A standard build-in fields logic steps
1. match/search value(s)
2. if value(s) None - set to default value(s)
3. filter value: `value = filter(value)`
4. invoke callback function: `value = callback(value)`
5. try cast to type from annotations (if set)*
6. usage factory function for cast result value. **If this param added,
it ignored typing (5)**

>>> Note: type casting better works with the simple types like 
`int, str, bool, float, list[...]`. For more difficult cases, recommend
add factory param for a manual cast result value.

# regex
This module contains fields that work on the standard module `re` 

## ReMatch
ReMatch field. Match the **first** occurrence and transforms 
according to the given parameters.

Params:

- pattern: str regex or compiled Pattern
- group: group. Default 1
- flags: pattern flags. Default None
- default: default value, if regex not found a match. Default None
- callback: a callback function rule. Default doing nothing
- filter_: a filter function rule. Default doing nothing
- factory: a factory function rule. Default doing nothing. If this param added,
it ignored typing

## ReMatchList
A ReMatchList field. Match the **all** occurrence and transforms according to the given parameters

Params:

- pattern: str regex or compiled Pattern
- group:  group. Default 1
- flags: pattern flags. Default None
- default: default value, if regex not found a match. Default None
- callback: a callback function rule. Default doing nothing
- filter_: a filter function rule. Default doing nothing
- factory: a factory function rule. Default doing nothing. If this param added,
it ignored typing
### Example:
```python
import pprint
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch, ReMatchList


TEXT = "1 2 3 4 5 6"


class Schema(BaseSchema):
    first_digit = ReMatch(r'(\d)')  # return string
    first_digit_int: int = ReMatch(r'(\d)')  # return int
    first_digit_float: float = ReMatch(r'(\d)')  # return float
    digit_float_x35: first_digit = ReMatch(r'(\d)', callback=float, factory=lambda s: s+3.5)
    has_word: bool = ReMatch(r"([a-z]+)")  # False
    has_digit: bool = ReMatch(r"(\d)")  # True

    digits: list[int] = ReMatchList(r'(\d)')
    # get all digit, convert to int and get max value
    max_digit: int = ReMatchList(r'(\d)', callback=int, factory=max)
    # get all digit, convert to int and get min value
    min_digit: int = ReMatchList(r'(\d)', callback=int, factory=min)
    # get digits, then less or equal 3
    less_3: list[int] = ReMatchList(r'(\d)', filter_=lambda s: int(s) <= 3)    # get all digit, convert to int and get max value
    # get digits, then less or equal 3 and sum
    sum_less_3: int = ReMatchList(r'(\d)', filter_=lambda s: int(s) <= 3, callback=int, factory=sum)
    # get digits, then bigger than 3, convert to int
    bigger_3: list[int] = ReMatchList(r'(\d)', filter_=lambda s: int(s) > 3, callback=int)
    # get digits, then bigger than 3 and sum
    sum_bigger_3: int = ReMatchList(r'(\d)', filter_=lambda s: int(s) > 3, callback=int, factory=sum)
    # get all digit and sum
    sum_digits: int = ReMatchList(r'(\d)', callback=int, factory=sum)


if __name__ == '__main__':
    schema = Schema(TEXT)
    pprint.pprint(schema.dict(), indent=4, width=48)
    # {   'bigger_3': [4, 5, 6],
    #     'digit_float_x35': 4.5,
    #     'digits': [1, 2, 3, 4, 5, 6],
    #     'first_digit': '1',
    #     'first_digit_float': 1.0,
    #     'first_digit_int': 1,
    #     'has_digit': True,
    #     'has_word': False,
    #     'less_3': [1, 2, 3],
    #     'max_digit': 6,
    #     'min_digit': 1,
    #     'sum_bigger_3': 15,
    #     'sum_digits': 21,
    #     'sum_less_3': 6}
```

# soup
A bs4.BeautifulSoup build-in fields

## SoupFind
get first value by `BeautifulSoup.find` method

Params:

- element: string html element or dict of kwargs for `BeautifulSoup.find` method
- callback: a callback function. Default extract text
- default: default value if Tag not founded. Default None
- validator: a validator function. default None
- filter_: a filter function. default None
- factory: a factory function. default None. If this param added, it ignored typing

## SoupFindList
get all values by `BeautifulSoup.find_all` method

Params:

- element: string html element or dict of kwargs for `BeautifulSoup.find` method
- callback: a callback function. Default extract text
- default: default value if Tag not founded. Default None
- validator: a validator function. default None
- filter_: a filter function. default None
- factory: a factory function. default None. If this param added, it ignored typing

## SoupFindSelect
get first value by `BeautifulSoup.select_one` method

Params:

- selector: css selector
- namespaces:  A dictionary mapping namespace prefixes used in the CSS selector to namespace URIs.
By default, Beautiful Soup will use the prefixes it encountered while parsing the document.
- callback: a callback function. Default extract text
- default: default value if Tag not founded. Default None
- validator: a validator function. default None
- filter_: a filter function. default None
- factory: a factory function. default None. If this param added, it ignored typing

## SoupFindSelectList
get first value by `BeautifulSoup.select_one` method

Params:

- selector: css selector
- namespaces:  A dictionary mapping namespace prefixes used in the CSS selector to namespace URIs.
By default, Beautiful Soup will use the prefixes it encountered while parsing the document.
- callback: a callback function. Default extract text
- default: default value if Tag not founded. Default None
- validator: a validator function. default None
- filter_: a filter function. default None
- factory: a factory function. default None. If this param added, it ignored typing

## tools
This module contains build-in callback and crop rules for [nested](#nested) fields

### Example:
```python
import pprint
from bs4 import BeautifulSoup
import re

from scrape_schema import BaseSchema
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect, SoupSelectList
from scrape_schema.tools.soup import get_tag

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TEST PAGE</title>
</head>
<body>
    <img src="/foo.png">foo</img>
    <p class="body-string">test-string</p>
    <p class="body-int">555</p>
    <a class="body-list">666</a>
    <a class="body-list">777</a>
    <a class="body-list">888</a>
    <div class="dict">
      <p class="string">test-1</p>
      <a class="list">1</a>
      <a class="list">2</a>
      <a class="list">3</a>
      <div class="sub-dict">
        <p class="sub-string">spam-1</p>
        <a class="sub-list">10</a>
        <a class="sub-list">20</a>
        <a class="sub-list">30</a>
      </div>
    </div>
    <div class="dict">
      <p class="string">test-2</p>
      <a class="list">4</a>
      <a class="list">5</a>
      <a class="list">6</a>
      <div class="sub-dict">
        <p class="sub-string">spam-2</p>
        <a class="sub-list">40</a>
        <a class="sub-list">50</a>
        <a class="sub-list">60</a>
      </div>
    </div>
    <img src="/baz.png">baz</img>
    <div class="dict">
      <p class="string">test-3</p>
      <a class="list">7</a>
      <a class="list">8</a>
      <a class="list">9</a>
      <div class="sub-dict">
        <p class="sub-string">spam-3</p>
        <a class="sub-list">70</a>
        <a class="sub-list">80</a>
        <a class="sub-list">90</a>
      </div>
    </div>
    <img src="/bar.png">bar</img>
</body>
</html>
"""


class Schema(BaseSchema):
    # add BeautifulSoup to config
    __MARKUP_PARSERS__ = {BeautifulSoup: {"features": "html.parser"}}
    # equal SoupFind({"name": "title"})
    title = SoupFind("<title>")
    title_select = SoupSelect("head > title")
    # usage build-in callback for get attribute
    lang: str = SoupFind("<html>", callback=get_tag("lang"))
    lang_select: str = SoupSelect("html", callback=get_tag("lang"))
    # you can use both fields: find and css!
    body_list: list[int] = SoupFindList('<a class="body-list">')
    body_list_selector: list[int] = SoupSelectList("body > a.body-list")
    all_digits: list[float] = SoupFindList("<a>", filter_=lambda tag: tag.get_text().isdigit())
    # soup find methods features accept
    body_list_re: list[int] = SoupFindList({"name": "a", "class_": re.compile("^list")})
    p_and_a_tags: list[str] = SoupFindList({"name": ["p", "a"]})
    has_spam_tag: bool = SoupFind("<spam>")
    has_spam_tag_select: bool = SoupSelect("body > spam")
    has_a_tag: bool = SoupFind("<a>")
    has_a_tag_select: bool = SoupSelect("body > a")

    # filter, factory feature
    bigger_100: list[int] = SoupFindList(
        "<a>", filter_=lambda s: s.get_text().isdigit() and int(s.get_text()) > 100)

    bigger_100_max: int = SoupFindList(
        "<a>", filter_=lambda s: s.get_text().isdigit() and int(s.get_text()) > 100,
        callback=lambda tag: int(tag.get_text(strip=True)), factory=max)

    spam_text: str = SoupFindList(
        "<p>", filter_=lambda s: s.get_text().startswith("spam"),
        factory=lambda lst: ", ".join(lst))
    sum_all_digit: int = SoupFindList(
        "<a>", filter_=lambda tag: tag.get_text().isdigit(), callback=lambda tag: int(tag.get_text()),
        factory=sum)


if __name__ == '__main__':
    schema = Schema(HTML)
    pprint.pprint(schema.dict(), width=48, compact=True)
    # {'all_digits': [666.0, 777.0, 888.0, 1.0, 2.0,
    #                 3.0, 10.0, 20.0, 30.0, 4.0, 5.0,
    #                 6.0, 40.0, 50.0, 60.0, 7.0, 8.0,
    #                 9.0, 70.0, 80.0, 90.0],
    #  'bigger_100': [666, 777, 888],
    #  'bigger_100_max': 888,
    #  'body_list': [666, 777, 888],
    #  'body_list_re': [1, 2, 3, 4, 5, 6, 7, 8, 9],
    #  'body_list_selector': [666, 777, 888],
    #  'has_a_tag': True,
    #  'has_a_tag_select': True,
    #  'has_spam_tag': False,
    #  'has_spam_tag_select': False,
    #  'lang': 'en',
    #  'lang_select': 'en',
    #  'p_and_a_tags': ['test-string', '555', '666',
    #                   '777', '888', 'test-1', '1',
    #                   '2', '3', 'spam-1', '10',
    #                   '20', '30', 'test-2', '4',
    #                   '5', '6', 'spam-2', '40',
    #                   '50', '60', 'test-3', '7',
    #                   '8', '9', 'spam-3', '70',
    #                   '80', '90'],
    #  'spam_text': 'spam-1, spam-2, spam-3',
    #  'sum_all_digit': 2826,
    #  'title': 'TEST PAGE',
    #  'title_select': 'TEST PAGE'}
```
# slax
A selectolax.parser.HTMLParser (Modest) build-in fields

## SLaxSelect
Get first value by css selector

- query: css selector
- strict: Set to True if you want to check if there is strictly only one match in the document
- callback: a callback function, default get_text
- default: default value if Node not founded. Default None
- validator: a validator function. default None
- filter_: a filter function. default None
- factory: a factory function. default None. If this param added, it ignored typing

## SLaxSelectList
Get first value by css selector

- query: css selector
- strict: Set to True if you want to check if there is strictly only one match in the document
- callback: a callback function, default get_text
- default: default value if Node not founded. Default None
- validator: a validator function. default None
- filter_: a filter function. default None
- factory: a factory function. default None. If this param added, it ignored typing
## tools
This module contains build-in callback and crop rules for [nested](#nested) fields
### Example:
```python
import pprint

from selectolax.parser import HTMLParser
from scrape_schema import BaseSchema
from scrape_schema.fields.slax import SLaxSelect, SLaxSelectList
from scrape_schema.tools.slax import get_tag, get_text

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TEST PAGE</title>
</head>
<body>
    <img src="/foo.png">foo</img>
    <p class="body-string">test-string</p>
    <p class="body-int">555</p>
    <a class="body-list">666</a>
    <a class="body-list">777</a>
    <a class="body-list">888</a>
    <div class="dict">
      <p class="string">test-1</p>
      <a class="list">1</a>
      <a class="list">2</a>
      <a class="list">3</a>
      <div class="sub-dict">
        <p class="sub-string">spam-1</p>
        <a class="sub-list">10</a>
        <a class="sub-list">20</a>
        <a class="sub-list">30</a>
      </div>
    </div>
    <div class="dict">
      <p class="string">test-2</p>
      <a class="list">4</a>
      <a class="list">5</a>
      <a class="list">6</a>
      <div class="sub-dict">
        <p class="sub-string">spam-2</p>
        <a class="sub-list">40</a>
        <a class="sub-list">50</a>
        <a class="sub-list">60</a>
      </div>
    </div>
    <img src="/baz.png">baz</img>
    <div class="dict">
      <p class="string">test-3</p>
      <a class="list">7</a>
      <a class="list">8</a>
      <a class="list">9</a>
      <div class="sub-dict">
        <p class="sub-string">spam-3</p>
        <a class="sub-list">70</a>
        <a class="sub-list">80</a>
        <a class="sub-list">90</a>
      </div>
    </div>
    <img src="/bar.png">bar</img>
</body>
</html>
"""


class Schema(BaseSchema):
    # add parser to config
    __MARKUP_PARSERS__ = {HTMLParser: {}}

    title = SLaxSelect("head > title")
    # build-in callback for extract tag
    lang = SLaxSelect("html", callback=get_tag("lang"))

    body_list_content: list[str] = SLaxSelectList("body > p")
    list_int: list[int] = SLaxSelectList("body > p.body-int")

    has_spam_tag: bool = SLaxSelect("body > spam.egg")
    has_a_tag: bool = SLaxSelect("body > a")
    body_list_float: list[float] = SLaxSelectList("a")
    # filters, factory features
    body_list_int_filter: list[int] = SLaxSelectList(
        "p", filter_=lambda node: node.text(deep=False).isdigit(), callback=lambda node: int(node.text()))

    body_spam_list: list[str] = SLaxSelectList(
        "p", filter_=lambda node: not node.text(deep=False).startswith("spam"))
    list_digit_less_100: list[int] = SLaxSelectList(
        "a", filter_=lambda node: int(node.text(deep=False)) < 100
    )
    list_digit_bigger_100: list[int] = SLaxSelectList(
        "a", filter_=lambda node: int(node.text(deep=False)) > 100
    )
    max_digit: int = SLaxSelectList("a", callback=lambda node: int(node.text()), factory=max)
    min_digit: int = SLaxSelectList("a", callback=lambda node: int(node.text()), factory=min)


if __name__ == "__main__":
    schema = Schema(HTML)
    pprint.pprint(schema.dict(), width=48, compact=True)
    # {'body_list_content': ['test-string', '555'],
    #  'body_list_float': [666.0, 777.0, 888.0, 1.0,
    #                      2.0, 3.0, 10.0, 20.0, 30.0,
    #                      4.0, 5.0, 6.0, 40.0, 50.0,
    #                      60.0, 7.0, 8.0, 9.0, 70.0,
    #                      80.0, 90.0],
    #  'body_list_int': [555],
    #  'body_list_int_filter': [555],
    #  'body_spam_list': ['test-string', '555',
    #                     'test-1', 'test-2',
    #                     'test-3'],
    #  'has_a_tag': True,
    #  'has_spam_tag': False,
    #  'lang': 'en',
    #  'list_digit_bigger_100': [666, 777, 888],
    #  'list_digit_less_100': [1, 2, 3, 10, 20, 30, 4,
    #                          5, 6, 40, 50, 60, 7, 8,
    #                          9, 70, 80, 90],
    #  'max_digit': 888,
    #  'min_digit': 1,
    #  'title': 'TEST PAGE'}

```
# nested
A "glue" for BaseSchema objects
## How it works
1. add Nested/NestedList field
2. add BaseSchema Type param, add crop_rule. 
3. crop_rule - a function, that cuts text according to a given rule
4. the text part is passed to the ScrapeSchema and the fields are parsed this

## Nested
A "glue" for BaseSchema objects. return one parsed BaseSchema object
Params:

- schema: BaseSchema type
- default: default value if parse is failed. Default NOne
- crop_rule: crop rule
- factory: factory function

## NestedList
A "glue" for BaseSchema objects. return list of parsed BaseSchema objects
Params:

- schema: BaseSchema type
- default: default value if parse is failed. Default NOne
- crop_rule: crop rule
- factory: factory function

### Example
```python
import pprint

from selectolax.parser import HTMLParser

from scrape_schema import BaseSchema
from scrape_schema.fields.slax import SLaxSelect, SLaxSelectList
from scrape_schema.fields.nested import NestedList, Nested
from scrape_schema.tools.slax import crop_by_slax, crop_by_slax_all, get_tag


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TEST PAGE</title>
</head>
<body>
    <img src="/foo.png">foo</img>
    <p class="body-string">test-string</p>
    <p class="body-int">555</p>
    <a class="body-list">666</a>
    <a class="body-list">777</a>
    <a class="body-list">888</a>
    <div class="dict">
      <p class="string">test-1</p>
      <a class="list">1</a>
      <a class="list">2</a>
      <a class="list">3</a>
      <div class="sub-dict">
        <p class="sub-string">spam-1</p>
        <a class="sub-list">10</a>
        <a class="sub-list">20</a>
        <a class="sub-list">30</a>
      </div>
    </div>
    <div class="dict">
      <p class="string">test-2</p>
      <a class="list">4</a>
      <a class="list">5</a>
      <a class="list">6</a>
      <div class="sub-dict">
        <p class="sub-string">spam-2</p>
        <a class="sub-list">40</a>
        <a class="sub-list">50</a>
        <a class="sub-list">60</a>
      </div>
    </div>
    <img src="/baz.png">baz</img>
    <div class="dict">
      <p class="string">test-3</p>
      <a class="list">7</a>
      <a class="list">8</a>
      <a class="list">9</a>
      <div class="sub-dict">
        <p class="sub-string">spam-3</p>
        <a class="sub-list">70</a>
        <a class="sub-list">80</a>
        <a class="sub-list">90</a>
      </div>
    </div>
    <img src="/bar.png">bar</img>
</body>
</html>
"""


class SchemaConfig(BaseSchema):
    # add parser to config
    __MARKUP_PARSERS__ = {HTMLParser: {}}


class SchemaDivSubDict(SchemaConfig):
    p: str = SLaxSelect('p.sub-string')
    a: list[float] = SLaxSelectList("a.sub-list")


class SchemaDivDict(SchemaConfig):
    p: str = SLaxSelect("p.string")
    a: list[int] = SLaxSelectList("a.list")
    sub_div: SchemaDivSubDict = Nested(SchemaDivSubDict, crop_rule=crop_by_slax("div.sub-dict"))


class Schema(SchemaConfig):
    title = SLaxSelect("head > title")
    # build-in callback for extract tag
    lang = SLaxSelect("html", callback=get_tag("lang"))
    # you can be found build-in crop rules in tools directory package or write manual
    first_div: SchemaDivDict = Nested(SchemaDivDict,
                                      crop_rule=crop_by_slax("body > div.dict"))
    all_divs: list[SchemaDivDict] = NestedList(SchemaDivDict, crop_rule=crop_by_slax_all("body > div.dict"))


if __name__ == "__main__":
    schema = Schema(HTML)
    pprint.pprint(schema.dict(), width=60, compact=True)
    # {'all_divs': [{'a': [1, 2, 3],
    #                'p': 'test-1',
    #                'sub_div': {'a': [10.0, 20.0, 30.0],
    #                            'p': 'spam-1'}},
    #               {'a': [4, 5, 6],
    #                'p': 'test-2',
    #                'sub_div': {'a': [40.0, 50.0, 60.0],
    #                            'p': 'spam-2'}},
    #               {'a': [7, 8, 9],
    #                'p': 'test-3',
    #                'sub_div': {'a': [70.0, 80.0, 90.0],
    #                            'p': 'spam-3'}}],
    #  'first_div': {'a': [1, 2, 3],
    #                'p': 'test-1',
    #                'sub_div': {'a': [10.0, 20.0, 30.0],
    #                            'p': 'spam-1'}},
    #  'lang': 'en',
    #  'title': 'TEST PAGE'}
```

# Custom Fields
If you need to write a field with your own logic or make a template for reuse - you can do it!
1. Usage build-in field and configurate
2. write new based on `BaseField` class

### Example

```python
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

```