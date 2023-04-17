from typing import Annotated
import pprint
import re

from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect, SoupSelectList
from scrape_schema.callbacks.soup import get_attr

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

    # <title> param auto converts to {"name": "title"} params
    title = SoupFind("<title>")
    title_select = SoupSelect("head > title")
    # usage build-in callback for get attribute
    lang: Annotated[str, SoupFind("<html>", callback=get_attr("lang"))]
    lang_select: Annotated[str, SoupSelect("html", callback=get_attr("lang"))]
    # you can use both fields: find or css!
    body_list: Annotated[list[int], SoupFindList('<a class="body-list">')]
    body_list_selector: Annotated[list[int], SoupSelectList("body > a.body-list")]
    all_digits: Annotated[list[float], SoupFindList("<a>", filter_=lambda tag: tag.get_text().isdigit())]
    # soup find method features accept
    body_list_re: Annotated[list[int], SoupFindList({"name": "a", "class_": re.compile("^list")})]
    p_and_a_tags: Annotated[list[str], SoupFindList({"name": ["p", "a"]})]
    # bool flags
    has_spam_tag: Annotated[bool, SoupFind("<spam>")]
    has_spam_tag_select: Annotated[bool, SoupSelect("body > spam")]
    has_a_tag: Annotated[bool, SoupFind("<a>")]
    has_a_tag_select: Annotated[bool, SoupSelect("body > a")]

    # filter, factory features
    bigger_100: Annotated[list[int], SoupFindList("<a>",
                                                  filter_=lambda s: s.get_text().isdigit() and int(s.get_text()) > 100)]
    # get all <a> tags, filter if text isdigit, bigger 100, and get max value
    bigger_100_max: Annotated[int, SoupFindList("<a>",
                                                filter_=lambda s: s.get_text().isdigit() and int(s.get_text()) > 100,
                                                callback=lambda tag: int(tag.get_text(strip=True)),
                                                factory=max)]

    spam_text: Annotated[str, SoupFindList("<p>",
                                           filter_=lambda s: s.get_text().startswith("spam"),
                                           factory=lambda lst: ", ".join(lst))]
    sum_all_digit: Annotated[int, SoupFindList("<a>",
                                               filter_=lambda tag: tag.get_text().isdigit(),
                                               callback=lambda tag: int(tag.get_text()),
                                               factory=sum)]


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
