from typing import Annotated

from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch, ReMatchDict, ReMatchList


class DisableParseSchema(BaseSchema):
    digit: Annotated[int, ReMatch(r"(\d+)")]
    string: Annotated[str, ReMatch(r"(\w+)")]
    lst: Annotated[list[int], ReMatchList(r"(\d+)")]
    dct: Annotated[dict[str, int], ReMatchDict(r"(?P<key>):(?P<digit>)")]


NO_PARSED_SCHEMA = DisableParseSchema(
    "",
    parse_markup=False,
    digit=1,
    string="test123",
    lst=["a", "b", "c"],
    dct={"key": "spam", "digit": 100},
)


def test_disable_parse_schema():
    assert NO_PARSED_SCHEMA.dict() == {
        "digit": 1,
        "string": "test123",
        "lst": ["a", "b", "c"],
        "dct": {"key": "spam", "digit": 100},
    }
