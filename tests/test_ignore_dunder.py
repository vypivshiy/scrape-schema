from typing import Annotated

from tests.fixtures import MockField

from scrape_schema import BaseSchema


class IgnoreDunderSchema(BaseSchema):
    _a: Annotated[str, MockField("hidden value")]
    _b: Annotated[int, MockField("100")]
    val: Annotated[str, MockField("visible value")]


ID_SCHEMA = IgnoreDunderSchema("")


def test_hidden_values():
    assert ID_SCHEMA.dict() == {"val": "visible value"}


def test_get_hidden_value():
    assert ID_SCHEMA._b == 100


def test_repr_output():
    assert repr(ID_SCHEMA) == "IgnoreDunderSchema(val:str='visible value')"
