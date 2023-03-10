from typing import Optional

import pytest
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema
from scrape_schema.fields.soup import SoupFind, SoupSelect, SoupFindList, SoupSelectList
from scrape_schema.tools.soup import get_tag

from tests.fixtures import HTML


class SoupSchema(BaseSchema):
    __MARKUP_PARSERS__ = {BeautifulSoup: {"features": "html.parser"}}
    # Soup
    lang: str = SoupFind("<html>", callback=get_tag("lang"))
    charset: str = SoupFind("<meta>", callback=get_tag("charset"), factory=lambda s: s.replace("-", ""))
    title: str = SoupFind({"name": "title"})
    title_lower: str = SoupSelect("head > title", factory=lambda text: text.lower())
    body_string: str = SoupFind('<p class="body-string>')
    body_string_chars: list[str] = SoupFind('<p class="body-string>', factory=list)
    body_string_flag: bool = SoupSelect('body > p.body-string')
    body_int: int = SoupFind('<p class="body-int">')
    body_float: float = SoupSelect("body > p.body-int")
    body_int_x10: int = SoupSelect("body > p.body-int", factory=lambda el: int(el) * 10)

    fail_value_1: Optional[str] = SoupFind({"name": "spam"})
    fail_value_2: bool = SoupFind("<spam>")
    fail_value_3: str = SoupSelect('body > spam.egg', default="spam")

    # SoupList
    body_int_list: list[int] = SoupFindList('<a class="body-list">')
    body_float_list: list[float] = SoupSelectList('body > a.body-list')
    max_body_list: int = SoupFindList({"name": "a", "class_": "body-list"}, factory=lambda els: max(int(i) for i in els))
    body_float_flag: bool = SoupFindList({"name": "a", "class_": "body-list"}, factory=bool)

    fail_list_1: Optional[list[int]] = SoupFindList({"name": "spam"})
    fail_list_2: bool = SoupSelectList('body > spam.egg')
    fail_list_3: list[str] = SoupFindList('<spam class="egg">', default=["spam", "egg"])


SOUP_SCHEMA = SoupSchema(HTML)


@pytest.mark.parametrize(
    "attr,result",
    [
        ("lang", "en"),
        ("charset", "UTF8"),
        ("title", "TEST PAGE"),
        ("title_lower", "test page"),
        ("body_string", "test-string"),
        ("body_string_chars", ["t", "e", "s", "t", "-", "s", "t", "r", "i", "n", "g"]),
        ("body_string_flag", True),
        ("body_int", 555),
        ("body_float", 555.0),
        ("body_int_x10", 5550),
        ("fail_value_1", None),
        ("fail_value_2", False),
        ("fail_value_3", "spam"),
        ("body_int_list", [666, 777, 888]),
        ("body_float_list", [666.0, 777.0, 888.0]),
        ("max_body_list", 888),
        ("body_float_flag", True),
        ("fail_list_1", None),
        ("fail_list_2", False),
        ("fail_list_3", ["spam", "egg"]),
    ]
)
def test_soup_parse(attr, result):
    value = getattr(SOUP_SCHEMA, attr)
    assert value == result
