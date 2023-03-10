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
