from typing import Optional, Annotated

from bs4 import BeautifulSoup
import pytest

from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.fields.soup import SoupFind, SoupSelect, SoupFindList, SoupSelectList
from scrape_schema.callbacks.soup import get_attr

from tests.fixtures import HTML


class SoupSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    # Soup
    lang: Annotated[str, SoupFind("<html>", callback=get_attr("lang"))]
    charset: Annotated[str, SoupFind("<meta>",
                                     callback=get_attr("charset"),
                                     factory=lambda s: s.replace("-", ""))]
    title: Annotated[str, SoupFind({"name": "title"})]
    title_lower: Annotated[str, SoupSelect("head > title", factory=lambda text: text.lower())]
    body_string: Annotated[str, SoupFind('<p class="body-string>')]
    body_string_chars: Annotated[list[str], SoupFind('<p class="body-string>', factory=list)]
    body_string_flag: Annotated[bool, SoupSelect('body > p.body-string')]
    body_int: Annotated[int, SoupFind('<p class="body-int">')]
    body_float: Annotated[float, SoupSelect("body > p.body-int")]
    body_int_x10: Annotated[int, SoupSelect("body > p.body-int", factory=lambda el: int(el) * 10)]

    fail_value_1: Annotated[Optional[str], SoupFind({"name": "spam"})]
    fail_value_2: Annotated[bool, SoupFind("<spam>")]
    fail_value_3: Annotated[str, SoupSelect('body > spam.egg', default="spam")]

    # SoupList
    body_int_list: Annotated[list[int], SoupFindList('<a class="body-list">')]
    body_float_list: Annotated[list[float], SoupSelectList('body > a.body-list')]
    max_body_list: Annotated[int, SoupFindList({"name": "a", "class_": "body-list"},
                                               factory=lambda els: max(int(i) for i in els))]
    body_float_flag: Annotated[bool, SoupFindList({"name": "a", "class_": "body-list"}, factory=bool)]

    fail_list_1: Annotated[Optional[list[int]], SoupFindList({"name": "spam"})]
    fail_list_2: Annotated[bool, SoupSelectList('body > spam.egg')]
    fail_list_3: Annotated[list[str], SoupFindList('<spam class="egg">', default=["spam", "egg"])]


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
