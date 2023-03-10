from typing import Optional

import pytest
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch, ReMatchList

from tests.fixtures import TEXT


class MockSchema(BaseSchema):

    default_1: str = "default"
    default_2: int = 100

    # ReMatch
    ipv4: str = ReMatch(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
    digit: int = ReMatch(r"(\d+)")
    digit_float: float = ReMatch(r"(\d+)", callback=lambda s: f"{s}.5")
    digit_x10: int = ReMatch(r"(\d+)", factory=lambda result: int(result) * 10)
    b_word: str = ReMatch(r"(b\w+)")
    b_word_chars: list[str] = ReMatch(r"(b\w+)", factory=list)
    b_word_title: str = ReMatch(r"(b\w+)", factory=lambda s: s.title())
    has_b_word: bool = ReMatch(r"(b\w+)")
    has_y_word: bool = ReMatch(r"(y\w+)")

    fail_value_none: Optional[str] = ReMatch(r"(ololo)")
    fail_value: bool = ReMatch(r"(ololo)")
    # ReMatchList
    words_lower: list[str] = ReMatchList(r"([a-z]+)")
    words_upper: list[str] = ReMatchList(r"([A-Z]+)")
    digits: list[int] = ReMatchList(r"(\d+)")
    digits_float: list[float] = ReMatchList(r"(\d+)", callback=lambda s: f"{s}.5")
    max_digit: int = ReMatchList(
        r"(\d+)", factory=lambda lst: max(int(i) for i in lst)
    )
    # auto typing is not stable works for more complex types, usage factory
    fail_list_1: Optional[list[str]] = ReMatchList(r"(ora)",
                                                   factory=lambda lst: [] if isinstance(lst, type(None)) else lst)
    fail_list_2: list[str] = ReMatchList(r"(ora)", default=[],
                                         factory=lambda lst: lst)
    fail_list_3: bool = ReMatchList(r"(ora)", default=False)


re_schema = MockSchema(TEXT)


@pytest.mark.parametrize("attr,result", [
    ("default_1", "default"),
    ("default_2", 100),
    ("ipv4", "192.168.0.1"),
    ("digit", 10),
    ("digit_float", 10.5),
    ("digit_x10", 100),
    ("b_word", "banana"),
    ("b_word_chars", ['b', 'a', 'n', 'a', 'n', 'a']),
    ("b_word_title", "Banana"),
    ("has_b_word", True),
    ("has_y_word", False),
    ("fail_value_none", None),
    ("fail_value", False),
    ("words_lower", ['banana', 'potato', 'foo', 'bar', 'lorem', 'upsum', 'dolor']),
    ("words_upper", ['BANANA', 'POTATO']),
    ("digits", [10, 20, 192, 168, 0, 1]),
    ("digits_float", [10.5, 20.5, 192.5, 168.5, 0.5, 1.5]),
    ("max_digit", 192),
    ("fail_list_1", []),
    ("fail_list_2", []),
    ("fail_list_3", False)
])
def test_re_parse(attr: str, result):
    assert getattr(re_schema, attr) == result
