from typing import Annotated

import pytest

from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.exceptions import ParseFailAttemptsError
from scrape_schema.fields.regex import ReMatch


# raises ParseFailAttemptsError if fail not founded
class FailedSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        fails_attempt = 0

    foo: Annotated[str, ReMatch(r"(lorem)")]
    fail: Annotated[str, ReMatch(r"(\d+)")]


# print RuntimeWarning message
class WarningSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        fails_attempt = 1

    foo: Annotated[str, ReMatch(r"(lorem)")]
    fail: Annotated[str, ReMatch(r"(\d+)")]


class DisabledTypingSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        type_cast = False

    foo: Annotated[int, ReMatch(r"(\d+)")]


def test_raise_attempts():
    with pytest.raises(ParseFailAttemptsError):
        FailedSchema("lorem upsum dolor")


def test_warning_attempts():
    with pytest.warns(RuntimeWarning, match="Failed parse"):
        WarningSchema("lorem upsum dolor")


def test_disable_typing():
    sc = DisabledTypingSchema("lorem 100500")
    assert not isinstance(sc.foo, int)
    assert isinstance(sc.foo, str)
