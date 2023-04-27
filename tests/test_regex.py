from __future__ import annotations

from typing import Optional

import pytest
from tests.fixtures import TEXT

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchList


class MockSchema(BaseSchema):
    default_1: str = "default"
    default_2: int = 100

    # ReMatch
    ipv4: ScField[str, ReMatch(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")]
    digit: ScField[int, ReMatch(r"(\d+)")]
    digit_float: ScField[float, ReMatch(r"(\d+)", callback=lambda s: f"{s}.5")]
    digit_x10: ScField[int, ReMatch(r"(\d+)", factory=lambda result: int(result) * 10)]
    b_word: ScField[str, ReMatch(r"(b\w+)")]
    b_word_chars: ScField[list[str], ReMatch(r"(b\w+)", factory=list)]
    b_word_title: ScField[str, ReMatch(r"(b\w+)", factory=lambda s: s.title())]
    has_b_word: ScField[bool, ReMatch(r"(b\w+)")]
    has_y_word: ScField[bool, ReMatch(r"(y\w+)")]

    fail_value_none: ScField[Optional[str], ReMatch(r"(ololo)")]
    fail_value: ScField[bool, ReMatch(r"(ololo)")]
    # ReMatchList
    words_lower: ScField[list[str], ReMatchList(r"([a-z]+)")]
    words_upper: ScField[list[str], ReMatchList(r"([A-Z]+)")]
    digits: ScField[list[int], ReMatchList(r"(\d+)")]
    digits_float: ScField[
        list[float], ReMatchList(r"(\d+)", callback=lambda s: f"{s}.5")
    ]
    max_digit: ScField[int, ReMatchList(r"(\d+)", callback=int, factory=max)]
    # auto typing is not stable works for more complex types, usage factory
    fail_list_1: ScField[
        Optional[list[str]],
        ReMatchList(
            r"(ora)", factory=lambda lst: [] if isinstance(lst, type(None)) else lst
        ),
    ]

    fail_list_2: ScField[
        list[str], ReMatchList(r"(ora)", default=[], factory=lambda lst: lst)
    ]
    fail_list_3: ScField[bool, ReMatchList(r"(ora)", default=False)]


re_schema = MockSchema(TEXT)


@pytest.mark.parametrize(
    "attr,result",
    [
        ("default_1", "default"),
        ("default_2", 100),
        ("ipv4", "192.168.0.1"),
        ("digit", 10),
        ("digit_float", 10.5),
        ("digit_x10", 100),
        ("b_word", "banana"),
        ("b_word_chars", ["b", "a", "n", "a", "n", "a"]),
        ("b_word_title", "Banana"),
        ("has_b_word", True),
        ("has_y_word", False),
        ("fail_value_none", None),
        ("fail_value", False),
        ("words_lower", ["banana", "potato", "foo", "bar", "lorem", "upsum", "dolor"]),
        ("words_upper", ["BANANA", "POTATO"]),
        ("digits", [10, 20, 192, 168, 0, 1]),
        ("digits_float", [10.5, 20.5, 192.5, 168.5, 0.5, 1.5]),
        ("max_digit", 192),
        ("fail_list_1", []),
        ("fail_list_2", []),
        ("fail_list_3", False),
    ],
)
def test_re_parse(attr: str, result):
    assert getattr(re_schema, attr) == result
