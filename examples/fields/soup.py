import pprint
import re

from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.callbacks.soup import get_attr
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect, SoupSelectList

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
    class Config(BaseSchemaConfig):
        # BeautifulSoup configuration. You can change parser to lxml. html5.parser, xml, add any kwargs, etc
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    @staticmethod
    def _bigger_100_filter(tag):
        return tag.get_text().isdigit() and int(tag.get_text()) > 100

    @staticmethod
    def _spam_text_factory(lst: list[str]) -> str:
        return " ".join(lst)

    @staticmethod
    def _all_digits_filter(tag) -> bool:
        return tag.get_text().isdigit()

    @staticmethod
    def _bigger_100_max_filter(tag) -> bool:
        return tag.get_text().isdigit() and int(tag.get_text()) > 100

    @staticmethod
    def _bigger_100_max_factory(lst: list[str]) -> int:
        return max(int(i) for i in lst)

    @staticmethod
    def _sum_all_digit_factory(lst: list[str]) -> int:
        return sum(int(i) for i in lst)

    # <title> param auto converts to {"name": "title"} params
    title = SoupFind("<title>")
    title_select = SoupSelect("head > title")
    # usage build-in callback for get attribute
    lang: ScField[str, SoupFind("<html>", callback=get_attr("lang"))]
    lang_select: ScField[str, SoupSelect("html", callback=get_attr("lang"))]
    # you can use both fields: find or css!
    body_list: ScField[list[int], SoupFindList('<a class="body-list">')]
    body_list_selector: ScField[list[int], SoupSelectList("body > a.body-list")]
    all_digits: ScField[list[float], SoupFindList("<a>")]
    # soup find method features accept
    body_list_re: ScField[
        list[int], SoupFindList({"name": "a", "class_": re.compile("^list")})
    ]
    p_and_a_tags: ScField[list[str], SoupFindList({"name": ["p", "a"]})]
    # bool flags
    has_spam_tag: ScField[bool, SoupFind("<spam>")]
    has_spam_tag_select: ScField[bool, SoupSelect("body > spam")]
    has_a_tag: ScField[bool, SoupFind("<a>")]
    has_a_tag_select: ScField[bool, SoupSelect("body > a")]

    # filter, factory features
    #
    bigger_100: ScField[list[int], SoupFindList("<a>")]
    # get all <a> tags, filter if text isdigit, bigger 100, and get max value
    bigger_100_max: ScField[
        int,
        SoupFindList(
            "<a>",
        ),
    ]
    spam_text: ScField[
        str,
        SoupFindList(
            "<p>",
            filter_=lambda s: s.get_text().startswith("spam"),
            # factory=lambda lst: ", ".join(lst),
        ),
    ]
    sum_all_digit: ScField[int, SoupFindList("<a>")]


if __name__ == "__main__":
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
