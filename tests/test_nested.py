import pytest

from selectolax.parser import HTMLParser
from scrape_schema import BaseSchema

from scrape_schema.fields.slax import SLaxSelect, SLaxSelectList
from scrape_schema.fields.nested import NestedList, Nested
from scrape_schema.tools.slax import get_tag, get_text, crop_by_slax, crop_by_slax_all
from fixtures import HTML


class SLaxSchema(BaseSchema):
    __MARKUP_PARSERS__ = {HTMLParser: {}}


class SubDict(SLaxSchema):
    p: str = SLaxSelect("p.sub-string", factory=lambda text: text.strip())
    a: list[int] = SLaxSelectList("a.sub-list")


class DivDict(SLaxSchema):
    p: str = SLaxSelect('p.string')
    a_int: list[int] = SLaxSelectList('a.list')
    a_float: list[float] = SLaxSelectList("a.list")
    sub_dict: SubDict = Nested(SubDict, crop_rule=crop_by_slax('div.sub-dict'))


class NestedSchema(SLaxSchema):
    title: str = SLaxSelect("head > title")
    first_div: DivDict = Nested(DivDict, crop_rule=crop_by_slax('body > div.dict'))
    nested_list: list[DivDict] = NestedList(DivDict, crop_rule=crop_by_slax_all('body > div.dict'))


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
