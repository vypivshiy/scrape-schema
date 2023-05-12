# parsel
Usage [parsel](https://parsel.readthedocs.io/en/latest/index.html) backend

# Schema config
this fields required parsel configuration:

```python
from parsel import Selector
from scrape_schema import BaseSchema, BaseSchemaConfig


class SoupSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        # can add extra configurations, or usage another parser
        parsers_config = {Selector: {}}

    # past fields.parsel here
    ...
```

# Field methods
- `extract(self, markup: Selector | _SelectorType, type_: Optional[Type] = None) -> Any`: 
Extracts data from the input text using the regular expression pattern and any provided callbacks and factories. 
Returns the extracted data.

## Params
- `markup: Selector | _SelectorType` - Selector object
- `type_: Optional[Type] = str`: The type to cast the matched string(s) to. This is only used if `factory` 
is not provided.

>>> Note: 
> For these fields to work predictably, don't use the `::text` selector, this object should be handled by **callback**

# NestedParsel
Alias of `scrape_schema.fields.Nested with parser=Selector`
```python
from parsel import Selector
from scrape_schema.fields.parsel import NestedParsel
from scrape_schema.fields.nested import Nested

NestedParsel(...) 
Nested(..., parser=Selector)  # same
```
# NestedParselList
Alias of `scrape_schema.fields.NestedList with parser=Selector`
```python
from parsel import Selector
from scrape_schema.fields.parsel import NestedParselList
from scrape_schema.fields.nested import NestedList

NestedParselList(...) 
NestedList(..., parser=Selector)  # same
```
# ParselSelect
This field provided [Selector.css](https://parsel.readthedocs.io/en/latest/usage.html) method and return first value

## Params
- `query: str` - css selector
- `default: Optional[Any] = None` - default value, if tag not founded. Default `None`
- `callback: Optional[Callable[[_SelectorType], str | Any]]` - A function that transforms the `_SelectorType` 
object into another value. Default `get_text()`
- `factory: Optional[Callable[[Union[str, Any]], Any]] = None` - A function that processes the values. 
**Disable type-cast feature**. Default `None`

## Usage
```python

from parsel import Selector
from scrape_schema.fields.parsel import ParselSelect
from scrape_schema.callbacks.parsel import get_attr
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

PARSER = Selector(HTML)
print(ParselSelect("div.dict > a.list").extract(PARSER))
# "1"

print(ParselSelect("div.dict > a.list").extract(PARSER, type_=int))
# 1

print(ParselSelect("div.dict > div.sub-dict > p.sub-string"
                 ).extract(PARSER))
# spam-1

print(ParselSelect("div.dict > div.sub-dict > p.sub-string", factory=lambda s: s.upper()
                 ).extract(PARSER))
# SPAM-1
print(ParselSelect("div.sub-dict > img", callback=get_attr("src")
                 ).extract(PARSER))
# /foo.png
```

# ParselSelectList
This field provided [Selector.css](https://parsel.readthedocs.io/en/latest/usage.html) method and return all values

## Params
- `query: str` - css selector
- `default: Optional[Any] = None` - default value, if tag not founded. Default `None`
- `filter_: Optional[Callable[[_SelectorType], bool]] = None` - A filter matched result. Default `None`
- `callback: Optional[Callable[[_SelectorType], str | Any]] = get_text()` - A function that transforms the `_SelectorType` 
object into another value. Default `get_text()`
- `factory: Optional[Callable[[Union[str, Any]], Any]] = None` - A function that processes the values. 
**Disable type-cast feature**. Default `None`

## Usage
```python
from parsel import Selector
from scrape_schema.fields.parsel import ParselSelectList
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

PARSER = Selector(HTML)
print(ParselSelectList("div.dict > a.list").extract(PARSER))
# ["1", "2", "3"]

print(ParselSelectList("div.dict > a.list").extract(PARSER, type_=list[int]))
# [1, 2, 3]


print(ParselSelectList("div.sub-dict > img").extract(PARSER))
# ["foo"]

print(ParselSelectList("div.sub-dict > img", callback=get_attr("src")).extract(PARSER))
# ["/foo.png"]

print(ParselSelectList("a", filter_=lambda n: n.text().isdigit() and int(n.text().isdigit()) <= 10
                     ).extract(PARSER, type_=list[int])
      )
# [1, 2, 3, 10]
```
# ParselXPath
This field provided [Selector.xpath](https://parsel.readthedocs.io/en/latest/usage.html) method and return first value

## Params
- `query: str` - xpath query
- `namespaces: Optional[Mapping[str, str]]` - xpath namespaces,
- `default: Optional[Any]` - default value, if tag not founded. Default `None`,
- `callback: Optional[Callable[[_SelectorType], Union[str, Any]]]` - - A function that transforms the `_SelectorType` 
object into another value. Default `get_text()`
- `factory: Optional[Callable[[Union[str, Any]], Any]]` - Optional[Callable[[Union[str, Any]], Any]] = None` - A function that processes the values. 
**Disable type-cast feature**. Default `None`
- `**xpath_kwargs: Any` - any keywords arguments for xpath method
## Usage

```python
from parsel import Selector
from scrape_schema.fields.parsel import ParselXPath
from scrape_schema.callbacks.parsel import get_attr

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
PARSER = Selector(HTML)

print(ParselXPath('//div[@class="dict"]/a').extract(PARSER))
# "1"
print(ParselXPath('//div[@class="dict"]/a').extract(PARSER, type_=int))
# 1
print(ParselXPath('//div/div[@class="sub-dict"]/p').extract(PARSER))
# spam-1

print(ParselXPath('//div/div[@class="sub-dict"]/p', factory=lambda s: s.upper()).extract(PARSER))
# SPAM-1
print(ParselXPath('//div[@class="sub-dict"]/img', callback=get_attr("src")).extract(PARSER))
# /foo.png

```
# ParselXPathList
This field provided [Selector.xpath](https://parsel.readthedocs.io/en/latest/usage.html) method and return all values

## Params
- `namespaces: Optional[Mapping[str, str]]` - xpath namespaces,
- `default: Optional[Any]` - default value, if tag not founded. Default `None`
- `filter_: Optional[Callable[[_SelectorType], bool]]` - A filter matched result. Default `None`
- `callback: Optional[Callable[[_SelectorType], Union[str, Any]]]` - - A function that transforms the `_SelectorType` 
object into another value. Default `get_text()`
- `factory: Optional[Callable[[Union[str, Any]], Any]]` - A function that processes the values. 
**Disable type-cast feature**. Default `None`
- `**xpath_kwargs: Any` - any keywords arguments for xpath method

## Usage

```python
from parsel import Selector
from scrape_schema.fields.parsel import ParselXPathList
from scrape_schema.callbacks.parsel import get_attr

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

PARSER = Selector(HTML)
print(ParselXPathList('//div[@class="dict"]/a').extract(PARSER))
# ["1", "2", "3"]

print(ParselXPathList('//div[@class="dict"]/a').extract(PARSER, type_=list[int]))
# [1, 2, 3]


print(ParselXPathList('//div[@class="sub-dict"]/img').extract(PARSER))
# ["foo"]

print(ParselXPathList('//div[@class="sub-dict"]/img', 
                      callback=get_attr("src")).extract(PARSER))
# ["/foo.png"]


print(ParselXPathList("//a", filter_=lambda n: n.text().isdigit() and int(n.text().isdigit()) <= 10
                     ).extract(PARSER, type_=list[int])
      )
# [1, 2, 3, 10]
```
# scrape_schema.callbacks.parsel
this module contains most useful callbacks and crop rules
## callbacks
### get_text
get text from `_SelectorType` object. This default callback in `fields.parsel` module

```python
from parsel import Selector
from scrape_schema.fields.parsel import ParselSelect, ParselSelectList, ParselXPath, ParselXPathList
from scrape_schema.callbacks.parsel import get_text
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

PARSER = Selector(HTML)
print(ParselSelect("p").extract(PARSER))
# test-string

print(ParselSelect("p", callback=get_text()).extract(PARSER)) # same
# test-string

print(ParselXPath("//p").extract(PARSER))
# test-string


print(ParselSelectList("p").extract(PARSER))
# ["test-string", "555"]

print(ParselXPathList("//p").extract(PARSER))
# ["test-string", "555"]
```
### replace_text
get text from `_SelectorType` and invoke `str.replace()` method
```python
from parsel import Selector
from scrape_schema.fields.parsel import ParselSelect, ParselXPath, ParselXPathList, ParselSelectList
from scrape_schema.callbacks.soup import replace_text

HTML = "<p>spamm-100</p>\n<p>spamm-200</p>"
PARSER = Selector(HTML)

print(ParselSelect("p", callback=replace_text("spam", "egg")))
# eggm-100

print(ParselSelect("p", callback=replace_text("m", "n", 1)))
# spanm-100

print(ParselSelectList("p", callback=replace_text("spam", "egg")))
# ["eggm-100", "eggm-200"]

print(ParselSelectList("p", callback=replace_text("m", "n", 1)))
# ["spanm-100", "spanm-200"]


print(ParselXPath("//p", callback=replace_text("spam", "egg")))
# eggm-100

print(ParselXPath("//p", callback=replace_text("m", "n", 1)))
# spanm-100

print(ParselXPathList("//p", callback=replace_text("spam", "egg")))
# ["eggm-100", "eggm-200"]

print(ParselXPathList("//p", callback=replace_text("m", "n", 1)))
# ["spanm-100", "spanm-200"]
```
### get_attr
get attribute value from `_SelectorType`
```python
from parsel import Selector
from scrape_schema.fields.parsel import ParselSelect, ParselXPath, ParselXPathList, ParselSelectList
from scrape_schema.callbacks.parsel import get_attr

HTML = '<a href="example.com/1">1</a>\n<a href="example.com/2">2</a>'

SOUP = Selector(HTML)

print(ParselSelect("a", callback=get_attr("href")))
# example.com/1

print(ParselXPath("//a", callback=get_attr("href")))
# example.com/1


print(ParselSelectList("a", callback=get_attr("href")))
# ["example.com/1", "example.com/2"]

print(ParselXPathList("//a", callback=get_attr("href")))
# ["example.com/1", "example.com/2"]
```

## crop_rules
This functions used in `fields.nested` fields

### crop_by_selector
Crop string by css selector to one part. This rule can be used in `Nested` field 

```python
from scrape_schema.callbacks.parsel import crop_by_selector

HTML = """
<div class="a">
<p>spam</p>
</div>
<div class="a">
<p>egg</p>
</div>
"""
print(crop_by_selector('div.a')(HTML))
# '<div class="a">\n<p>spam</p>\n</div>'
```
### crop_by_selector_all
Crop string by css selector to parts. This rule can be used in `NestedList` field

```python
from scrape_schema.callbacks.parsel import crop_by_selector_all

HTML = """
<div class="a">
<p>spam</p>
</div>
<div class="a">
<p>egg</p>
</div>
"""
print(crop_by_selector_all('div.a')(HTML))
# ['<div class="a">\n<p>spam</p>\n</div>', <div class="a">\n<p>egg</p>\n</div>]
```

### crop_by_xpath
Crop string by xpath selector to one part. This rule can be used in `Nested` field 
```python
from scrape_schema.callbacks.parsel import crop_by_xpath

HTML = """
<div class="a">
<p>spam</p>
</div>
<div class="a">
<p>egg</p>
</div>
"""
print(crop_by_xpath('//div[@class="a"]')(HTML))
# '<div class="a">\n<p>spam</p>\n</div>'
```
### crop_by_xpath_all
Crop string by xpath selector to parts. This rule can be used in `NestedList` field
```python
from scrape_schema.callbacks.parsel import crop_by_xpath_all
HTML = """
<div class="a">
<p>spam</p>
</div>
<div class="a">
<p>egg</p>
</div>
"""
print(crop_by_xpath_all('//div[@class="a"]')(HTML))
# ['<div class="a">\n<p>spam</p>\n</div>', <div class="a">\n<p>egg</p>\n</div>]
```

# Schema Usage

```python
from typing import List
import pprint

from parsel import Selector

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields import Nested, NestedList
from scrape_schema.fields.parsel import ParselSelect, ParselSelectList, ParselXPath, ParselXPathList
from scrape_schema.callbacks.parsel import get_attr, crop_by_xpath_all, crop_by_xpath, crop_by_selector


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


class ParselSchema(BaseSchema):
    """Base schema configurations"""
    class Config(BaseSchemaConfig):
        parsers_config = {Selector: {}}
    pass


class SchemaDivSubDict(ParselSchema):
    p: ScField[str, ParselSelect("p.sub-string")]
    a: ScField[List[float], ParselSelectList("a.sub-list")]


class SchemaDivDict(ParselSchema):
    p: ScField[str, ParselSelect("p.string")]
    a: ScField[List[int], ParselXPathList('//a[@class="list"]')]
    # crop <div class="sub-dict">...</div>
    sub_div: ScField[
        SchemaDivSubDict,
        Nested(SchemaDivSubDict, crop_rule=crop_by_selector("div.sub-dict"))]


class Schema(ParselSchema):
    title: ScField[str, ParselXPath("//title")]
    # build-in callback for extract tag
    lang: ScField[str, ParselSelect("html", callback=get_attr("lang"))]
    # you can be found build-in crop rules in tools directory package or write manual
    # crop <div class="dict">...</div>
    first_div: ScField[
        SchemaDivDict,
        Nested(SchemaDivDict, crop_rule=crop_by_xpath('//div[@class="dict"]'))
    ]
    # crop <div class="dict">...</div>
    all_divs: ScField[
        List[SchemaDivDict],
        NestedList(SchemaDivDict, crop_rule=crop_by_xpath_all('//div[@class="dict"]')),
    ]


if __name__ == '__main__':
    pprint.pprint(Schema(HTML).dict(), width=60, compact=True)
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

# Reference

* https://selectolax.readthedocs.io/en/latest/index.html