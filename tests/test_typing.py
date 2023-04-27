from __future__ import annotations

import pytest
from tests.fixtures import MockField

from scrape_schema import BaseSchema
from scrape_schema.base import Annotated, Optional


class TypingSchema(BaseSchema):
    # default
    def_1 = 1
    def_2 = "spam"
    def_3 = [1, 2, 3]
    def_4 = True

    # default typing
    t_def_1: int = 10
    t_def_2: str = "egg"
    t_def_3: list[int] = [4, 5, 6]
    t_def_4: bool = False
    a_val_1: Annotated[int, MockField("1")]
    a_val_2: Annotated[str, MockField(100)]
    a_val_3: Annotated[float, MockField(1.5)]
    a_val_4: Annotated[int, MockField("1.5", callback=float, factory=round)]
    a_val_5: Annotated[str, MockField(999)]
    a_val_6: Annotated[bool, MockField("ok")]
    a_val_7: Annotated[bool, MockField(None)]
    a_val_8: Annotated[list[int], MockField([1, 2, 3, 4])]
    a_val_9: Annotated[list[int], MockField([1, 2, 3, 4], factory=sum)]
    a_val_10: Annotated[dict[str, int], MockField({"a": "1", "b": "2"})]
    a_val_11: Annotated[Optional[str], MockField(None)]
    a_val_12: Annotated[Optional[str], MockField("yes")]
    a_val_13: Annotated[Optional[int], MockField(None)]
    a_val_14: Annotated[Optional[int], MockField("10")]
    a_val_15: Annotated[Optional[list[str]], MockField([])]
    a_val_16: Annotated[Optional[list[str]], MockField([], default=[])]
    a_val_17: Annotated[list[str], MockField([], default=[])]
    a_val_18: Annotated[Optional[list[int]], MockField(["1", "2"])]
    a_val_19: Annotated[
        list[str], MockField("foobar", factory=list)
    ]  # str ignored typing, - cast manual
    # filter
    f_val_1: Annotated[
        list[int], MockField([1, 10, 100, 2, 9, 5], filter_=lambda i: i <= 10)
    ]
    f_val_2: Annotated[
        list[int],
        MockField(
            ["lorem", "3", "upsum", "dolor", "1", "2"], filter_=lambda s: s.isdigit()
        ),
    ]
    f_val_3: Annotated[
        list[str],
        MockField(
            ["lorem", "3", "upsum", "dolor", "1", "2"],
            filter_=lambda s: not s.isdigit(),
        ),
    ]


CAST_SCHEMA = TypingSchema(":)")


@pytest.mark.parametrize(
    "attr,result",
    [
        ("a_val_10", {"a": 1, "b": 2}),
        ("a_val_11", None),
        ("a_val_12", "yes"),
        ("a_val_13", None),
        ("a_val_14", 10),
        ("a_val_15", None),
        ("a_val_16", []),
        ("a_val_17", []),
        ("a_val_18", [1, 2]),
        ("a_val_19", ["f", "o", "o", "b", "a", "r"]),
        ("a_val_2", "100"),
        ("a_val_3", 1.5),
        ("a_val_4", 2),
        ("a_val_5", "999"),
        ("a_val_6", True),
        ("a_val_7", False),
        ("a_val_8", [1, 2, 3, 4]),
        ("a_val_9", 10),
        ("def_1", 1),
        ("def_2", "spam"),
        ("def_3", [1, 2, 3]),
        ("def_4", True),
        ("f_val_1", [1, 10, 2, 9, 5]),
        ("f_val_2", [3, 1, 2]),
        ("f_val_3", ["lorem", "upsum", "dolor"]),
        ("t_def_1", 10),
        ("t_def_2", "egg"),
        ("t_def_3", [4, 5, 6]),
        ("t_def_4", False),
    ],
)
def test_cast(attr, result):
    assert getattr(CAST_SCHEMA, attr) == result
