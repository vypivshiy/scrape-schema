from typing import Dict, List, Optional, Union

import pytest

from scrape_schema._type_caster import TypeCaster


def test_typing_to_builtin():
    tc = TypeCaster()
    assert tc._typing_to_builtin(Optional[str]) == Optional[str]


def test_cast_list():
    tc = TypeCaster()
    assert tc.cast(List[int], ["1", "2", "3"]) == [1, 2, 3]
    assert tc.cast(List[str], [1, 2, 3]) == ["1", "2", "3"]
    assert tc.cast(List[str], ["a", "b", "c"]) == ["a", "b", "c"]


def test_cast_dict():
    tc = TypeCaster()
    assert tc.cast(Dict[str, int], {"a": "1", "b": "2", "c": "3"}) == {
        "a": 1,
        "b": 2,
        "c": 3,
    }
    assert tc.cast(Dict[str, List[int]], {"a": ["1", "2"], "b": ["3", "4"]}) == {
        "a": [1, 2],
        "b": [3, 4],
    }


def test_cast_optional():
    tc = TypeCaster()
    assert tc.cast(Optional[int], 1) == 1
    assert tc.cast(Optional[int], None) is None


def test_cast_not_supported_union():
    tc = TypeCaster()
    assert tc.cast(Union[int, str], 1) is None
    assert tc.cast(Union[int, str], "a") is None


def test_cast_bool():
    tc = TypeCaster()
    assert tc.cast(bool, 1) is True
    assert tc.cast(bool, 0) is False


def test_cast_direct():
    tc = TypeCaster()
    assert tc.cast(int, "1") == 1
    assert tc.cast(str, 1) == "1"
    assert tc.cast(List[str], "spam") == ["s", "p", "a", "m"]
