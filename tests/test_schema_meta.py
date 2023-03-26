import pytest

from scrape_schema import BaseSchema, MetaSchema
from scrape_schema.exceptions import ParseFailAttemptsError
from scrape_schema.fields.regex import ReMatch


# raises ParseFailAttemptsError if fail not founded
class FailedSchema(BaseSchema):
    class Meta(MetaSchema):
        fails_attempt = 0
    foo = ReMatch(r"(lorem)")
    fail = ReMatch(r"(\d+)")


# print RuntimeWarning message
class WarningSchema(BaseSchema):
    class Meta(MetaSchema):
        fails_attempt = 1
    foo = ReMatch(r"(lorem)")
    fail = ReMatch(r"(\d+)")


def test_raise_attempts():
    with pytest.raises(ParseFailAttemptsError):
        FailedSchema("lorem upsum dolor")


def test_warning_attempts():
    with pytest.warns(RuntimeWarning):
        WarningSchema("lorem upsum dolor")
