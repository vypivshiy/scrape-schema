# TODO: write mypy plugin for avoid assignment errors
from scrape_schema import BaseSchema, Text


class AttrSchema(BaseSchema):
    word: str = Text().re_search(r"\w+")[0]
    digit: int = Text().re_search(r"\d+")[0]
    float_digit: float = Text().re_search(r"\d+")[0].concat_l("5.")


def test_attr_schema():
    schema = AttrSchema("test 123")
    assert schema.dict() == {"word": "test", "digit": 123, "float_digit": 5.123}
