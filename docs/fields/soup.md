# soup
Usage [beautifulsoup4](https://beautiful-soup-4.readthedocs.io/en/latest/#searching-the-tree) lib

# Schema config
This fields required bs4 configuration

```python
from bs4 import BeautifulSoup
from scrape_schema import BaseSchema, BaseSchemaConfig


class SoupSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        # can add extra configurations, or usage another parser
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    # past fields.soup here
    ...
```

# Field methods

- `extract(self, markup: bs4.BeautifulSoup | Tag, type_: Optional[Type] = None) -> Any`: 
Extracts data from the `bs4.BeautifulSoup` object and any provided callbacks and factories. Returns the extracted data.

## Params
- `markup: bs4.BeautifulSoup | Tag` - Soup object or Tag
- `type_: Optional[Type] = str`: The type to cast the matched string(s) to. This is only used if `factory` 
is not provided.

# SoupFind
Field provided [find()](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find) method

## Params
- `element: str | Dict[str, Any]]` -  html tag or keywords arguments for find method
- `default: Optional[Any]` - default value, if tag not founded. Default `None`
- `callback: Optional[Callable[[Tag], Union[str, Any]]]` - A function that transforms the `bs4.Tag` object into 
another value. Default `get_text()`
- `factory: Optional[Callable[[Union[str, Any]], Any]]` - A function that processes the value. 
**Disable type-cast feature**. Default `None`
## Usage

```python
from bs4 import BeautifulSoup
from scrape_schema.fields.soup import SoupFind

# convert html tag to soup keyword arguments feature
SoupFind("<a>")
# equivalent SoupFind({"name": "a"})
SoupFind('<div class="spam" id="0">')
# equivalent SoupFind({"name": "div", "attrs": {"class":"spam", "id": "0"}})
SoupFind("foobar") # TypeError: "Element `foobar` is not valid HTML tag


HTML = """
<img src="/foo.png">foo</img>
<p class="body-string">test-string</p>
<p class="body-int">555</p>
<a class="body-list">666</a>
<a class="body-list">777</a>
<a class="body-list">888</a>
"""
SOUP = BeautifulSoup(HTML, "html.parser")
print(SoupFind("<img>").extract(SOUP)) # foo
# same
print(SoupFind({"name": "img"}).extract(SOUP)) # foo

from scrape_schema.callbacks.soup import get_attr
print(SoupFind("<img>", 
               callback=get_attr("src")).extract(SOUP)) # "/foo.png"

print(SoupFind('<p class="body-int">').extract(SOUP)) # "555"
print(SoupFind('<p class="body-int">').extract(SOUP, type_=int)) # 555
print(SoupFind('<p class="body-int">', factory=lambda v: int(v) * 2).extract(SOUP)) # 1110

# find() method features (functions, regex) accepted
import re
print(SoupFind(
    {"name": "p", 
     "attrs": 
         {"class": re.compile(r"int")}
     }).extract(HTML)) # "555"
```

# SoupFindList
Field provided [find_all()](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all) method

## Params:
- `element: str | Dict[str, Any]]` -  html tag or keywords arguments for find method
- `default: Optional[Any]` - default value, if tags not founded. Default `None`
- `filter_: Optional[Callable[[Tag], bool]]` - A filter matched result. Default `None`
- `callback: Optional[Callable[[Tag], Union[str, Any]]]` - A function that transforms the `bs4.Tag` object into 
another value. Default `get_text()`
- `factory: Optional[Callable[[Any], Any]]` - A function that processes the value. 
**Disable type-cast feature**. Default `None`

## Usage
```python
from bs4 import BeautifulSoup
from scrape_schema.fields.soup import SoupFindList
from scrape_schema.callbacks.soup import get_attr
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


SOUP = BeautifulSoup(HTML, "html.parser")
# SoupFindList have same feature: convert html tag to attrs
SoupFindList("<a>")
# equivalent SoupFind({"name": "a"})
SoupFindList('<div class="spam" id="0">')
# equivalent SoupFindList({"name": "div", "attrs": {"class":"spam", "id": "0"}})
SoupFindList("foobar") # raise TypeError

print(SoupFindList("<img>").extract(SOUP)) 
# ["foo", "bar", "baz"]

print(SoupFindList("<img>", callback=get_attr("src")).extract(SOUP)) 
# ["/foo.png", "/bar.jpg", "/baz.png"]

print(SoupFindList("<img>", 
                   filter_=lambda t: not t.get("src").endswith(".jpg"),
                   callback=get_attr("src")).extract(SOUP)) 
# ["/foo.png", "/baz.png"]

print(SoupFindList("<img>", 
                   callback=get_attr("src"), 
                   factory=lambda lst: [f"example.com{p}" for p in lst]
                   ).extract(SOUP))
# ["example.com/foo.png", "example.com/bar.jpg", "example.com/baz.png"]

print(SoupFindList({"name": ["p", "a"]}, 
                   filter_=lambda t: t.get_text().isdigit(),
                   ).extract(SOUP, type_=list[int])
      )
# [555, 666, 777, 888]
```


# SoupSelect
This field provided by [select_one()](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors-through-the-css-property) method

## Params:
- `selector: str` - css selector
- `default: Optional[Any]` - default value, if tag not founded. Default `None`
- `callback: Optional[Callable[[Tag], Any]]` - A function that transforms the `bs4.Tag` object into 
another value. Default `get_text()`
- `factory: Optional[Callable[[Any], Any]]` - A function that processes the value. 
**Disable type-cast feature**. Default `None`

## Usage
```python
from bs4 import BeautifulSoup

from scrape_schema.fields.soup import SoupSelect
from scrape_schema.callbacks.soup import get_attr


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

SOUP = BeautifulSoup(HTML, "html.parser")
print(SoupSelect("div.dict > a.list").extract(SOUP))
# "1"

print(SoupSelect("div.dict > a.list").extract(SOUP, type_=int))
# 1

print(SoupSelect("div.sub-dict > p.sub-string").extract(SOUP))
# "spam-1"

print(SoupSelect("div.sub-dict > p.sub-string",
                 factory=lambda s: s.upper()).extract(SOUP))
# "SPAM-1"

print(SoupSelect("div.dict > div.sub-dict > img", callback=get_attr("src")))
# /foo.png

```
# SoupSelectList
This field provided by [select()](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors-through-the-css-property) method

## Params:
- `selector: str` - css selector
- `default: Optional[Any]` - default value, if tag not founded. Default `None`
- `filter_: Optional[Callable[[Tag], bool]]` - A filter matched result function. Default `None`
- `callback: Optional[Callable[[Tag], Any]]` - A function that transforms the `bs4.Tag` object into 
another value. Default `get_text()`
- `factory: Optional[Callable[[List[Any]]], Any]` - A function that processes the value. 
**Disable type-cast feature**. Default `None`

## Usage
```python
from bs4 import BeautifulSoup

from scrape_schema.fields.soup import SoupSelectList

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

SOUP = BeautifulSoup(HTML, "html.parser")

print(SoupSelectList("div.dict > a.list").extract(SOUP))
# ["1", "2", "3"]

print(SoupSelectList("div.dict > div.sub-dict > a.list").extract(SOUP))
# ["10", "20", "30"]

print(SoupSelectList("div.dict > div.sub-dict > a.list"
                     ).extract(SOUP, type_=list[int]))
# [10, 20, 30]

print(SoupSelectList("a", 
                     filter_=lambda t: t.get_text().isdigit() and int(t.get_text()) <= 10,
                     ).extract(SOUP, type_=list[int]))
# [1, 2, 3, 10]

```
# scrape_schema.callbacks.soup
this module contains most useful callbacks and crop rules

## callbacks

### get_text()
get text from tag. This default callback in `fields.soup` module
```python
from bs4 import BeautifulSoup
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect,SoupSelectList
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


SOUP = BeautifulSoup(HTML, "html.parser")

print(SoupFind("<p>").extract(SOUP))
# test-string

print(SoupFind("<p>", callback=get_text()).extract(SOUP)) # same
# test-string

print(SoupFindList("<p>").extract(SOUP))
# ["test-string", "555"] 

print(SoupSelect("p").extract(SOUP))
# test-string

print(SoupSelectList("p").extract(SOUP))
# ["test-string", "555"]
```
### replace_text()
get text from tag and invoke `str.replace()` method
```python
from bs4 import BeautifulSoup
from scrape_schema.fields.soup import SoupSelect, SoupSelectList
from scrape_schema.callbacks.soup import replace_text

HTML = "<p>spamm-100</p>\n<p>spamm-200</p>"
SOUP = BeautifulSoup(HTML, "html.parser")

print(SoupSelect("p", callback=replace_text("spam", "egg")))
# eggm-100

print(SoupSelect("p", callback=replace_text("m", "n", 1)))
# spanm-100

print(SoupSelectList("p", callback=replace_text("spam", "egg")))
# ["eggm-100", "eggm-200"]

print(SoupSelectList("p", callback=replace_text("m", "n", 1)))
# ["spanm-100", "spanm-200"] 

```
### element_to_dict()
Convert html tag to soup keyword arguments. 
Automatically init in `SoupFind`, `SoupFindList` constructors if argument **is string**.

```python
from scrape_schema.fields.soup import SoupFind
from scrape_schema.callbacks.soup import element_to_dict
SoupFind("<a>")  # same SoupFind({"name": "a"})
SoupFind('<div class="spam"> id="100">')  # same SoupFind({"name": "div", "attrs": {"class": "spam", "id": "100"})

print(element_to_dict("<a>"))
# {"name": "a"}
print(element_to_dict('<div class="spam"> id="100">'))
# {"name": "div", "attrs": {"class": "spam", "id": "100"}

print(element_to_dict("div > a"))
# TypeError
```

### get_attr()
get attribute value from Tag

```python
from bs4 import BeautifulSoup
from scrape_schema.fields.soup import SoupSelect, SoupFindList
from scrape_schema.callbacks.soup import get_attr
HTML = '<a href="example.com/1">1</a>\n<a href="example.com/2">2</a>'

SOUP = BeautifulSoup(HTML, "html.parser")

print(SoupSelect("a", callback=get_attr("href")))
# example.com/1

print(SoupFindList("<a>", callback=get_attr("href")))
# ["example.com/1", "example.com/2"]
```

## crop_rules
this functions used in `fields.nested` fields

### crop_by_tag
crop string by tag to one part. This rule can be used in `Nested` field 

```python
from scrape_schema.callbacks.soup import crop_by_tag

HTML = """
<div class="a">
<p>spam</p>
</div>
<div class="a">
<p>egg</p>
</div>
"""
print(crop_by_tag('<div class="a">')(HTML))
# <div class="a">
# <p>spam</p>
# </div>
```
### crop_by_tag_all
crop string by tag to parts. This rule can be used in `NestedList` field 

```python
from scrape_schema.callbacks.soup import crop_by_tag_all

HTML = """
<div class="a">
<p>spam</p>
</div>
<div class="a">
<p>egg</p>
</div>
"""
print(crop_by_tag_all('<div class="a">')(HTML))
# ['<div class="a">\n<p>spam</p>\n</div>', <div class="a">\n<p>egg</p>\n</div>]
```

### crop_by_selector
crop string by css selector to one part. This rule can be used in `Nested` field 

```python
from scrape_schema.callbacks.soup import crop_by_selector
HTML = """
<div class="a">
<p>spam</p>
</div>
<div class="a">
<p>egg</p>
</div>
"""
print(crop_by_selector('div.a')(HTML))
# <div class="a">
# <p>spam</p>
# </div>
```
### crop_by_selector_all
crop string by css selector to parts. This rule can be used in `NestedList` field
```python
from scrape_schema.callbacks.soup import crop_by_selector_all

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

## Schema Usage
```python
import pprint
import re

from bs4 import BeautifulSoup

from scrape_schema.fields.nested import NestedList
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect, SoupSelectList
from scrape_schema.callbacks.soup import get_attr, crop_by_selector_all

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


class DivDict(BaseSchema):
    # <div class="dict">
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    string: ScField[str, SoupFind('<p class="string">')]
    a_list: ScField[list[int], SoupFindList('<a class="list">')]


class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        # BeautifulSoup configuration. You can change parser to lxml. html5.parser, xml, add any kwargs
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    # <title> param auto converts to {"name": "title"} params
    title: ScField[str, SoupFind("<title>")]
    title_select: ScField[str, SoupSelect("head > title")]
    # usage build-in callback for get attribute
    lang: ScField[str, SoupFind("<html>", callback=get_attr("lang"))]
    lang_select: ScField[str, SoupSelect("html", callback=get_attr("lang"))]
    # you can use both fields: find or css!
    body_list: ScField[list[int], 
                         SoupFindList('<a class="body-list">')]
    body_list_selector: ScField[list[int], 
                                  SoupSelectList("body > a.body-list")]
    all_digits: ScField[list[float], 
                          SoupFindList("<a>", 
                                       filter_=lambda tag: tag.get_text().isdigit())]
    # soup find method features accept
    body_list_re: ScField[list[int], 
                            SoupFindList({"name": "a", "class_": re.compile("^list")})]
    p_and_a_tags: ScField[list[str], SoupFindList({"name": ["p", "a"]})]
    # bool flags
    has_spam_tag: ScField[bool, SoupFind("<spam>")]
    has_spam_tag_select: ScField[bool, SoupSelect("body > spam")]
    has_a_tag: ScField[bool, SoupFind("<a>")]
    has_a_tag_select: ScField[bool, SoupSelect("body > a")]

    # filter, factory features
    bigger_100: ScField[list[int], 
                          SoupFindList("<a>",
                                       filter_=lambda s: s.get_text().isdigit() and int(s.get_text()) > 100)]
    # get all <a> tags, filter if text isdigit, bigger 100, and get max value
    bigger_100_max: ScField[int,
                              SoupFindList("<a>",
                                           filter_=lambda s: s.get_text().isdigit() and int(s.get_text()) > 100,
                                           callback=lambda tag: int(tag.get_text(strip=True)),
                                           factory=max)]

    spam_text: ScField[str,
                         SoupFindList("<p>",
                                      filter_=lambda s: s.get_text().startswith("spam"),
                                      factory=lambda lst: ", ".join(lst))]
    sum_all_digit: ScField[int,
                             SoupFindList("<a>",
                                          filter_=lambda tag: tag.get_text().isdigit(),
                                          callback=lambda tag: int(tag.get_text()),
                                          factory=sum)]
    div_dicts: ScField[list[DivDict],
                         NestedList(DivDict, 
                                    crop_rule=crop_by_selector_all("body > div.dict"))]


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
    #  'div_dicts': [{'a_list': [1, 2, 3],
    #                 'string': 'test-1'},
    #                {'a_list': [4, 5, 6],
    #                 'string': 'test-2'},
    #                {'a_list': [7, 8, 9],
    #                 'string': 'test-3'}],
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
# Reference:

* https://beautiful-soup-4.readthedocs.io/en/latest/

* https://beautiful-soup-4.readthedocs.io/en/latest/#find

* https://beautiful-soup-4.readthedocs.io/en/latest/#find-all

* https://beautiful-soup-4.readthedocs.io/en/latest/#a-regular-expression

* https://beautiful-soup-4.readthedocs.io/en/latest/#a-list

* https://beautiful-soup-4.readthedocs.io/en/latest/#a-function

* https://beautiful-soup-4.readthedocs.io/en/latest/#css-selectors
