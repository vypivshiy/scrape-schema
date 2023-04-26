# soup
Usage [beautifulsoup4](https://beautiful-soup-4.readthedocs.io/en/latest/#searching-the-tree) backend

# Schema config
this fields required bs4 configuration

```python
from bs4 import BeautifulSoup
from scrape_schema import BaseSchema, BaseSchemaConfig


class SoupSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        # can add extra configurations, or usage another parser
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    # pass fields.soup here
    ...
```

# SoupFind, SoupFindList
* element - html tag or kwargs for find/find_all methods

## features
this field can automatically convert sting html tag string to kwargs for this methods

```python
from scrape_schema.callbacks.soup import element_to_dict


print(element_to_dict("<a>"))
# {"name": "a"}
print(element_to_dict('<div class="spam" id="100">'))
# {"name": "div", "attrs": {"class": "spam", "id": "100"}}
print(element_to_dict('<div class="spam egg foo">'))
# {"name": "div", "attrs": {"class": ["spam", "egg", "foo"]}}
print(element_to_dict('div class="spam"'))
# TypeError: Element `div class="spam` is not valid HTML tag
print(element_to_dict('scrape_schema'))
# TypeError: Element `scrape_schema` is not valid HTML tag
```

```python
from scrape_schema.fields.soup import SoupFind, SoupFindList


SoupFind("<a>")  # {"name": "a"}
SoupFindList('<div class="spam" id="0">')  # {"name": "div", "attrs": {"class":"spam", "id": "0"}}
SoupFind("foobar") # raise TypeError
```
Also, you can simplify tag for search elements:

```python
from scrape_schema.fields.soup import SoupFind


# find div tag with class="spam" tag like <div class="spam" foo="bar", href="/foo">
# <div class="spam egg">
# <div class="spam foo bar baz">
# ...
SoupFind('<div class="spam">')  # {"name": "div", "attrs": {"class":"spam"}}
```

If you need advanced features of `soup.find, soup.find_all` - pass the first parameter as a dictionary,
```python
import re
from scrape_schema.fields.soup import SoupFind, SoupFindList


ExampleField_1 = SoupFind({"name": "div", "class_": re.compile(r'^spam*')})
ExampleField_2 = SoupFindList({"name": ["a", "p", "h1"]})
...
```

# SoupSelect, SoupSelectList
* selector - css selector

```python
from scrape_schema.fields.soup import SoupSelect, SoupSelectList

SelectorExample = SoupSelect("body > div.spam > div.egg")
SelectorExample_2 = SoupSelectList("div.spam > ul > li")
```

## callbacks
fields.soup in callbacks, filter accept `Tag` object

```python
from scrape_schema.fields.soup import SoupFind, SoupSelect
from scrape_schema.callbacks.soup import get_attr, get_text

# get tag attribute
ExampleCallback_1 = SoupFind("<a>", callback=get_attr("href"))
ExampleCallback_2 = SoupSelect("div > img", callback=get_attr("src", default=''))

# get text. is default callback
ExampleCallback_3 = SoupFind("<div>", callback=get_text(separator=",", strip=True))
```

## crop_rules

```python
from scrape_schema.fields.nested import Nested, NestedList
from scrape_schema.callbacks.soup import crop_by_tag, crop_by_tag_all, crop_by_selector, crop_by_selector_all

# crop rules (Nested)
Nested_1 = Nested(..., crop_rule=crop_by_tag('ul'))
Nested_2 = Nested(..., crop_rule=crop_by_selector('body > div', features='lxml'))

# crop selectors (NestedList)
Nested_3 = NestedList(..., crop_rule=crop_by_tag_all('div'))
Nested_4 = NestedList(..., crop_rule=crop_by_selector_all('body > div'))
```

## Example
Without usage schema:
```python
from bs4 import BeautifulSoup
from scrape_schema.callbacks.soup import get_attr, get_text
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect, SoupSelectList

HTML = """
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
"""
Image = SoupFind("<img>", callback=get_attr("src"))
AllPText = SoupFindList("<p>", filter_=lambda t: not(get_text()(t).isdigit()))
SubList = SoupFindList('<a class="sub-list">')
SelectSubDictA = SoupSelectList("div.sub-dict > a")
SelectSubString = SoupSelect("div.sub-dict > p.sub-string")

soup = BeautifulSoup(HTML, "html.parser")

img: str = Image.extract(soup)
p_lst: list[str] = AllPText.extract(soup)
sub_list: list[int] = SubList.extract(soup, type_=list[int])
sub_list_2: list[float] = SelectSubDictA.extract(soup, type_=list[float])
sub_str: str = SelectSubString.extract(soup)

print(img, p_lst, sub_list, sub_list_2, sub_str, sep="\n__\n")
# /foo.png
# __
# ['test-string', 'test-1', 'spam-1']
# __
# [10, 20, 30]
# __
# [10.0, 20.0, 30.0]
# __
# spam-1
```
With schema:
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
    title = SoupFind("<title>")
    title_select = SoupSelect("head > title")
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
