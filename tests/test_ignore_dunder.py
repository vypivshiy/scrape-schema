from typing import Annotated

from tests.fixtures import MockField

from scrape_schema import BaseSchema
from scrape_schema.fields import Nested


class IgnoreDunderSchema(BaseSchema):
    class _HiddenSubSchema(BaseSchema):
        spam: Annotated[str, MockField("egg")]

    class PublicSubSchema(BaseSchema):
        egg: Annotated[str, MockField("spam")]

    _a: Annotated[str, MockField("hidden value")]
    _b: Annotated[int, MockField("100")]
    val: Annotated[str, MockField("visible value")]
    val_2: Annotated[PublicSubSchema, Nested(PublicSubSchema, crop_rule=lambda _: _)]
    val_3: Annotated[_HiddenSubSchema, Nested(_HiddenSubSchema, crop_rule=lambda _: _)]
    _val_4: Annotated[PublicSubSchema, Nested(PublicSubSchema, crop_rule=lambda _: _)]
    _val_5: Annotated[_HiddenSubSchema, Nested(_HiddenSubSchema, crop_rule=lambda _: _)]


ID_SCHEMA = IgnoreDunderSchema("")


def test_hidden_values():
    assert ID_SCHEMA.dict() == {
        "val": "visible value",
        "val_2": {"egg": "spam"},
        "val_3": {"spam": "egg"},
    }


def test_get_hidden_value():
    assert ID_SCHEMA._b == 100


def test_repr_output():
    assert (
        repr(ID_SCHEMA) == "IgnoreDunderSchema(val:str='visible value', "
        "val_2=PublicSubSchema(egg:str='spam'), val_3=_HiddenSubSchema(spam:str='egg'))"
    )
