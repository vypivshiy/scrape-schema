from typing import Optional
import pytest

from selectolax.parser import HTMLParser

from scrape_schema import BaseSchema
from scrape_schema.fields.slax import SLaxSelect, SLaxSelectList
from scrape_schema.tools.slax import get_tag

from fixtures import HTML


class SLaxSchema(BaseSchema):
    __MARKUP_PARSERS__ = {HTMLParser: {}}
    lang: str = SLaxSelect("html", callback=get_tag("lang"))
    charset: str = SLaxSelect("head > meta", callback=get_tag("charset"), factory=lambda s: s.replace("-", ""))
    title: str = SLaxSelect('head > title')
    title_lower: str = SLaxSelect("head > title", factory=lambda text: text.lower())
    body_string: str = SLaxSelect('body > p.body-string')
    body_string_chars: list[str] = SLaxSelect('body > p.body-string', factory=list)
    body_string_flag: bool = SLaxSelect('body > p.body-string')
    body_int: int = SLaxSelect('body > p.body-int')
    body_float: float = SLaxSelect("body > p.body-int")
    body_int_x10: int = SLaxSelect("body > p.body-int", factory=lambda el: int(el) * 10)

    fail_value_1: Optional[str] = SLaxSelect('body > spam.egg')
    fail_value_2: bool = SLaxSelect("body > spam.egg")
    fail_value_3: str = SLaxSelect('body > spam.egg', default="spam")

    body_int_list: list[int] = SLaxSelectList('body > a.body-list')
    body_float_list: list[float] = SLaxSelectList('body > a.body-list')
    max_body_list: int = SLaxSelectList('body > a.body-list', factory=lambda els: max(int(i) for i in els))
    body_float_flag: bool = SLaxSelectList('body > a.body-list', factory=bool)

    fail_list_1: Optional[list[int]] = SLaxSelectList('body > spam.egg')
    fail_list_2: bool = SLaxSelectList('body > spam.egg')
    fail_list_3: list[str] = SLaxSelectList('body > spam.egg', default=["spam", "egg"])


SLAX_SCHEMA = SLaxSchema(HTML)


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
def test_slax_parse(attr, result):
    value = getattr(SLAX_SCHEMA, attr)
    assert value == result
