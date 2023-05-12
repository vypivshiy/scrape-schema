# slax
Usage [selectolax](https://selectolax.readthedocs.io/en/latest/parser.html) lib

# Schema config
This fields required `selectolax` configuration

```python
from selectolax.parser import HTMLParser
from scrape_schema import BaseSchema, BaseSchemaConfig


class SlaxSchema(BaseSchema):
    class Meta(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}
    # past slax fields here
```

# Field methods

- `extract(self, markup: HTMLParser | Node, type_: Optional[Type] = None) -> Any`: Extracts data from the 
`HTMLParser` object and any provided callbacks and factories. Returns the extracted data.

## Params
- `markup: HTMLParser | Node` - HTMLParser object or Node
- `type_: Optional[Type] = str`: The type to cast the matched string(s) to. This is only used if `factory` 
is not provided.
# NestedSlax
Alias of Nested with `parser=HTMLParser` param
```python
from selectolax.parser import HTMLParser
from scrape_schema.fields.slax import NestedSlax
from scrape_schema.fields.nested import Nested

NestedSlax(...) 
Nested(..., parser=HTMLParser)  # same
```
# NestedSlaxList
Alias of NestedList with `parser=HTMLParser` param
```python
from selectolax.parser import HTMLParser
from scrape_schema.fields.slax import NestedSlaxList
from scrape_schema.fields.nested import NestedList

NestedSlaxList(...) 
NestedList(..., parser=HTMLParser)  # same
```
# SlaxSelect
This field provide [HTMLParser().css_first](https://selectolax.readthedocs.io/en/latest/parser.html#selectolax.parser.HTMLParser.css_first) method

## Params
* `selector: str` - css selector
* `strict: bool = False` -  Check if there is strictly only one match in the document. Default `False`
* `default: Optional[Any]` - default value, if tag not founded. Default `None`
* `callback: Optional[Callable[[Node], Union[str, Any]]]` - A function that transforms the `parser.Node` object into 
another value. Default `get_text()`
* `factory: Optional[Callable[[Any], Any]]` - A function that processes the value. 
**Disable type-cast feature**. Default `None`

## Usage
```python
from selectolax.parser import HTMLParser
from scrape_schema.fields.slax import SlaxSelect
from scrape_schema.callbacks.slax import get_attr
HTML = """
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
    <img src="/foo.png">foo</img>
  </div>
</div>
"""

PARSER = HTMLParser(HTML)
print(SlaxSelect("div.dict > a.list").extract(PARSER))
# "1"

print(SlaxSelect("div.dict > a.list").extract(PARSER, type_=int))
# 1

print(SlaxSelect("div.dict > div.sub-dict > p.sub-string"
                 ).extract(PARSER))
# spam-1

print(SlaxSelect("div.dict > div.sub-dict > p.sub-string", factory=lambda s: s.upper()
                 ).extract(PARSER))
# SPAM-1
print(SlaxSelect("div.sub-dict > img", callback=get_attr("src")
                 ).extract(PARSER))
# /foo.png

```
# SlaxSelectList
This field provide [HTMLParser(),css](https://selectolax.readthedocs.io/en/latest/parser.html#selectolax.parser.HTMLParser.css) method

## Params
* `selector: str` - css selector
* `default: Optional[Any]` - default value, if tag not founded. Default `None`
* `filter_: Optional[Callable[[Node], bool]]` - A filter matched result. Default `None`
* `callback: Optional[Callable[[Node], Union[str, Any]]]` - A function that transforms the `parser.Node` object into 
another value. Default `get_text()`
* `factory: Optional[Callable[[Any], Any]]` - A function that processes the values. 
**Disable type-cast feature**. Default `None`

## Usage
```python
from selectolax.parser import HTMLParser
from scrape_schema.fields.slax import SlaxSelectList
from scrape_schema.callbacks.slax import get_attr
HTML = """
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
    <img src="/foo.png">foo</img>
  </div>
</div>
"""

PARSER = HTMLParser(HTML)
print(SlaxSelectList("div.dict > a.list").extract(PARSER))
# ["1", "2", "3"]

print(SlaxSelectList("div.dict > a.list").extract(PARSER, type_=list[int]))
# [1, 2, 3]


print(SlaxSelectList("div.sub-dict > img").extract(PARSER))
# ["foo"]

print(SlaxSelectList("div.sub-dict > img", callback=get_attr("src")).extract(PARSER))
# ["/foo.png"]


print(SlaxSelectList("a", filter_=lambda n: n.text().isdigit() and int(n.text().isdigit()) <= 10
                     ).extract(PARSER, type_=list[int])
      )
# [1, 2, 3, 10]
```
# scrape_schema.callbacks.slax
this module contains most useful callbacks and crop rules

## callbacks
### get_text
get text from `Node`. This default callback in `fields.slax` module

```python
from selectolax.parser import HTMLParser
from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList
from scrape_schema.callbacks.soup import get_text

HTML = """
<img src="/foo.png">foo</img>
<p class="body-string">test-string</p>
<p class="body-int">555</p>
<a class="body-list">666</a>
<a class="body-list">777</a>
<a class="body-list">888</a>
<img src="/bar.jpg">bar</img>
<img src="/baz.png">baz</img>
"""


PARSER = HTMLParser(HTML)

print(SlaxSelect("p").extract(PARSER))
# test-string

print(SlaxSelect("p", callback=get_text()).extract(PARSER)) # same
# test-string

print(SlaxSelectList("p").extract(PARSER))
# ["test-string", "555"]
```
### replace_text
get text from Node and invoke `str.replace()` method
```python
from selectolax.parser import HTMLParser
from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList
from scrape_schema.callbacks.soup import replace_text

HTML = "<p>spamm-100</p>\n<p>spamm-200</p>"
PARSER = HTMLParser(HTML)

print(SlaxSelect("p", callback=replace_text("spam", "egg")))
# eggm-100

print(SlaxSelect("p", callback=replace_text("m", "n", 1)))
# spanm-100

print(SlaxSelectList("p", callback=replace_text("spam", "egg")))
# ["eggm-100", "eggm-200"]

print(SlaxSelectList("p", callback=replace_text("m", "n", 1)))
# ["spanm-100", "spanm-200"]
```
### get_attr
get attribute value from Node

```python
from selectolax.parser import HTMLParser
from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList
from scrape_schema.callbacks.slax import get_attr
HTML = '<a href="example.com/1">1</a>\n<a href="example.com/2">2</a>'

SOUP = HTMLParser(HTML)

print(SlaxSelect("a", callback=get_attr("href")))
# example.com/1

print(SlaxSelectList("a", callback=get_attr("href")))
# ["example.com/1", "example.com/2"]
```

## crop_rules
This functions used in `fields.nested` fields

### crop_by_slax
Crop string by css selector to one part. This rule can be used in `Nested` field 

### crop_by_slax_all
Crop string by css selector to parts. This rule can be used in `NestedList` field

```python
from scrape_schema.callbacks.slax import crop_by_slax_all

HTML = """
<div class="a">
<p>spam</p>
</div>
<div class="a">
<p>egg</p>
</div>
"""
print(crop_by_slax_all('div.a')(HTML))
# ['<div class="a">\n<p>spam</p>\n</div>', <div class="a">\n<p>egg</p>\n</div>]
```

# Schema Usage
```python
import pprint

from selectolax.parser import HTMLParser

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList
from scrape_schema.callbacks.slax import get_attr

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
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}

    title = SlaxSelect("head > title")
    # build-in callback for get attribute
    lang = SlaxSelect("html", callback=get_attr("lang"))

    body_list_content: ScField[list[str], SlaxSelectList("body > p")]
    list_int: ScField[list[int], SlaxSelectList("body > p.body-int")]

    has_spam_tag: ScField[bool, SlaxSelect("body > spam.egg")]
    has_a_tag: ScField[bool, SlaxSelect("body > a")]
    body_list_float: ScField[list[float], SlaxSelectList("a")]
    # filters, factory features
    body_list_int_filter: ScField[list[int], SlaxSelectList("p",
                                                              filter_=lambda node: node.text(deep=False).isdigit(),
                                                              callback=lambda node: int(node.text()))]

    body_spam_list: ScField[list[str], SlaxSelectList("p",
                                                        filter_=lambda node: not node.text(deep=False).startswith(
                                                            "spam"))]
    list_digit_less_100: ScField[list[int], SlaxSelectList("a",
                                                             filter_=lambda node: int(node.text(deep=False)) < 100)]
    list_digit_bigger_100: ScField[list[int], SlaxSelectList("a",
                                                               filter_=lambda node: int(node.text(deep=False)) > 100)]
    max_digit: ScField[int, SlaxSelectList("a",
                                             callback=lambda node: int(node.text()),
                                             factory=max)]
    min_digit: ScField[int, SlaxSelectList("a",
                                             callback=lambda node: int(node.text()),
                                             factory=min)]


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
