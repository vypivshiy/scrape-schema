from typing import Annotated

from tests.fixtures import TEXT

from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatchDict, ReMatchListDict


class RegexSchemaDicts(BaseSchema):
    @staticmethod
    def _lst_dict_1_callback(dct: dict[str, str]) -> dict[str, int]:
        dct["digit"] = int(dct.get("digit"))  # type: ignore
        return dct  # type: ignore

    dict_1: Annotated[dict[str, str], ReMatchDict(r"\-(?P<key>\w+):(?P<value>\d+)")]
    dict_2: Annotated[dict[str, int], ReMatchDict(r":(?P<value>\d+)")]
    lst_dict_1: Annotated[
        list[dict[str, int]],
        ReMatchListDict(r":(?P<digit>\d+)", callback=_lst_dict_1_callback),
    ]


REGEX_SCHEMA_DICTS = RegexSchemaDicts(TEXT)


def test_values():
    assert REGEX_SCHEMA_DICTS.dict_1 == {"key": "foo", "value": "10"}
    assert REGEX_SCHEMA_DICTS.dict_2 == {"value": 10}
    assert REGEX_SCHEMA_DICTS.lst_dict_1 == [{"digit": 10}, {"digit": 20}]
