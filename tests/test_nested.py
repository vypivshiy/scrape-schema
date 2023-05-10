from typing import List

import pytest

from fixtures import HTML
from selectolax.parser import HTMLParser

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.callbacks.slax import crop_by_slax, crop_by_slax_all
from scrape_schema.fields.nested import Nested, NestedList
from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList


class SLaxSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}


class SubDict(SLaxSchema):
    p: ScField[str, SlaxSelect("p.sub-string", factory=lambda text: text.strip())]
    a: ScField[List[int], SlaxSelectList("a.sub-list")]


class DivDict(SLaxSchema):
    p: ScField[str, SlaxSelect("p.string")]
    a_int: ScField[List[int], SlaxSelectList("a.list")]
    a_float: ScField[List[float], SlaxSelectList("a.list")]
    sub_dict: ScField[SubDict, Nested(SubDict, crop_rule=crop_by_slax("div.sub-dict"))]


class NestedSchema(SLaxSchema):
    title: ScField[str, SlaxSelect("head > title")]
    first_div: ScField[
        DivDict, Nested(DivDict, crop_rule=crop_by_slax("body > div.dict"))
    ]
    nested_list: ScField[
        List[DivDict],
        NestedList(DivDict, crop_rule=crop_by_slax_all("body > div.dict")),
    ]


NESTED_SCHEMA = NestedSchema(HTML)


def test_base_nested():
    assert NESTED_SCHEMA.title == "TEST PAGE"


def test_nested_first():
    assert NESTED_SCHEMA.first_div.dict() == {
        "p": "test-1",
        "a_int": [1, 2, 3],
        "a_float": [1.0, 2.0, 3.0],
        "sub_dict": {"p": "spam-1", "a": [10, 20, 30]},
    }


def test_schema_to_dict():
    assert NESTED_SCHEMA.dict() == {
        "first_div": {
            "a_float": [1.0, 2.0, 3.0],
            "a_int": [1, 2, 3],
            "p": "test-1",
            "sub_dict": {"a": [10, 20, 30], "p": "spam-1"},
        },
        "nested_list": [
            {
                "a_float": [1.0, 2.0, 3.0],
                "a_int": [1, 2, 3],
                "p": "test-1",
                "sub_dict": {"a": [10, 20, 30], "p": "spam-1"},
            },
            {
                "a_float": [4.0, 5.0, 6.0],
                "a_int": [4, 5, 6],
                "p": "test-2",
                "sub_dict": {"a": [40, 50, 60], "p": "spam-2"},
            },
            {
                "a_float": [7.0, 8.0, 9.0],
                "a_int": [7, 8, 9],
                "p": "test-3",
                "sub_dict": {"a": [70, 80, 90], "p": "spam-3"},
            },
        ],
        "title": "TEST PAGE",
    }


def test_nested_to_nested():
    assert NESTED_SCHEMA.first_div.sub_dict.dict() == {"p": "spam-1", "a": [10, 20, 30]}


def test_nested_list():
    assert [instance.dict() for instance in NESTED_SCHEMA.nested_list] == [
        {
            "a_float": [1.0, 2.0, 3.0],
            "a_int": [1, 2, 3],
            "p": "test-1",
            "sub_dict": {"a": [10, 20, 30], "p": "spam-1"},
        },
        {
            "a_float": [4.0, 5.0, 6.0],
            "a_int": [4, 5, 6],
            "p": "test-2",
            "sub_dict": {"a": [40, 50, 60], "p": "spam-2"},
        },
        {
            "a_float": [7.0, 8.0, 9.0],
            "a_int": [7, 8, 9],
            "p": "test-3",
            "sub_dict": {"a": [70, 80, 90], "p": "spam-3"},
        },
    ]


def test_raise_nested():
    with pytest.raises(NotImplementedError):
        Nested(SubDict, crop_rule=lambda _: _).extract("spam")


def test_raise_nested_list():
    with pytest.raises(NotImplementedError):
        NestedList(SubDict, crop_rule=lambda _: _).extract("spam")
