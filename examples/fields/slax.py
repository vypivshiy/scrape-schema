import pprint
from typing import Annotated

from selectolax.parser import HTMLParser
from scrape_schema import BaseSchema, MetaSchema

from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList
from scrape_schema.callbacks.slax import get_attr, get_text

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
    class Meta(MetaSchema):
        parsers_config = {HTMLParser: {}}

    title = SlaxSelect("head > title")
    # build-in callback for get attribute
    lang = SlaxSelect("html", callback=get_attr("lang"))

    body_list_content: Annotated[list[str], SlaxSelectList("body > p")]
    list_int: Annotated[list[int], SlaxSelectList("body > p.body-int")]

    has_spam_tag: Annotated[bool, SlaxSelect("body > spam.egg")]
    has_a_tag: Annotated[bool, SlaxSelect("body > a")]
    body_list_float: Annotated[list[float], SlaxSelectList("a")]
    # filters, factory features
    body_list_int_filter: Annotated[list[int], SlaxSelectList("p",
                                                              filter_=lambda node: node.text(deep=False).isdigit(),
                                                              callback=lambda node: int(node.text()))]

    body_spam_list: Annotated[list[str], SlaxSelectList("p",
                                                        filter_=lambda node: not node.text(deep=False).startswith("spam"))]
    list_digit_less_100: Annotated[list[int], SlaxSelectList("a",
                                                             filter_=lambda node: int(node.text(deep=False)) < 100)]
    list_digit_bigger_100: Annotated[list[int], SlaxSelectList("a",
                                                               filter_=lambda node: int(node.text(deep=False)) > 100)]
    max_digit: Annotated[int, SlaxSelectList("a",
                                             callback=lambda node: int(node.text()),
                                             factory=max)]
    min_digit: Annotated[int, SlaxSelectList("a",
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
