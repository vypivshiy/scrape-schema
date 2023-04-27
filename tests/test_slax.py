from __future__ import annotations

from typing import Optional

import pytest
from selectolax.parser import HTMLParser
from tests.fixtures import HTML

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.callbacks.slax import get_attr, get_text
from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList


class SlaxSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}

    lang: ScField[str, SlaxSelect("html", callback=get_attr("lang"))]
    charset: ScField[
        str,
        SlaxSelect(
            "head > meta",
            callback=get_attr("charset"),
            factory=lambda s: s.replace("-", ""),
        ),
    ]
    title: ScField[str, SlaxSelect("head > title")]
    title_lower: ScField[
        str, SlaxSelect("head > title", factory=lambda text: text.lower())
    ]
    body_string: ScField[str, SlaxSelect("body > p.body-string")]
    body_string_chars: ScField[
        list[str], SlaxSelect("body > p.body-string", factory=list)
    ]
    body_string_flag: ScField[bool, SlaxSelect("body > p.body-string")]
    body_int: ScField[int, SlaxSelect("body > p.body-int")]
    body_float: ScField[float, SlaxSelect("body > p.body-int")]
    body_int_x10: ScField[
        int, SlaxSelect("body > p.body-int", factory=lambda el: int(el) * 10)
    ]

    fail_value_1: ScField[Optional[str], SlaxSelect("body > spam.egg")]
    fail_value_2: ScField[bool, SlaxSelect("body > spam.egg")]
    fail_value_3: ScField[str, SlaxSelect("body > spam.egg", default="spam")]

    body_int_list: ScField[list[int], SlaxSelectList("body > a.body-list")]
    body_float_list: ScField[list[float], SlaxSelectList("body > a.body-list")]
    max_body_list: ScField[
        int,
        SlaxSelectList(
            "body > a.body-list", callback=lambda el: int(get_text()(el)), factory=max
        ),
    ]
    body_float_flag: ScField[bool, SlaxSelectList("body > a.body-list", factory=bool)]

    fail_list_1: ScField[Optional[list[int]], SlaxSelectList("body > spam.egg")]
    fail_list_2: ScField[bool, SlaxSelectList("body > spam.egg")]
    fail_list_3: ScField[
        list[str], SlaxSelectList("body > spam.egg", default=["spam", "egg"])
    ]


SLAX_SCHEMA = SlaxSchema(HTML)


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
    ],
)
def test_slax_parse(attr, result):
    value = getattr(SLAX_SCHEMA, attr)
    assert value == result
