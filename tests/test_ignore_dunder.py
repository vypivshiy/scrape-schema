from tests.fixtures import MockField

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields import Nested


class IgnoreDunderSchema(BaseSchema):
    class _HiddenSubSchema(BaseSchema):
        spam: ScField[str, MockField("egg")]

    class PublicSubSchema(BaseSchema):
        egg: ScField[str, MockField("spam")]

    _a: ScField[str, MockField("hidden value")]
    _b: ScField[int, MockField("100")]
    val: ScField[str, MockField("visible value")]
    val_2: ScField[PublicSubSchema, Nested(PublicSubSchema, crop_rule=lambda _: _)]
    val_3: ScField[_HiddenSubSchema, Nested(_HiddenSubSchema, crop_rule=lambda _: _)]
    _val_4: ScField[PublicSubSchema, Nested(PublicSubSchema, crop_rule=lambda _: _)]
    _val_5: ScField[_HiddenSubSchema, Nested(_HiddenSubSchema, crop_rule=lambda _: _)]


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
