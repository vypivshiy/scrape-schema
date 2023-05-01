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
