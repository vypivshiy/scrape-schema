from typing import Dict, List

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchDict, ReMatchList


class DisableParseSchema(BaseSchema):
    digit: ScField[int, ReMatch(r"(\d+)")]
    string: ScField[str, ReMatch(r"(\w+)")]
    lst: ScField[List[int], ReMatchList(r"(\d+)")]
    dct: ScField[Dict[str, int], ReMatchDict(r"(?P<key>):(?P<digit>)")]


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
