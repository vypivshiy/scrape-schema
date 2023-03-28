from typing import Annotated
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch


class OrSchema(BaseSchema):
    span_or_spam: Annotated[str, (ReMatch(r'foo=(span)'),
                                  ReMatch(r'foo=(spam)'))]
    # all defaults required or this construction raise error
    digit: Annotated[int, (ReMatch(r'bar=(\d)', default=1),
                           ReMatch(r'bar=(\d\d)', default=2),
                           ReMatch(r'bar=(\d+)', default=100))]


OR_SCHEMA = OrSchema('foo=spam')


def test_multi():
    assert OR_SCHEMA.span_or_spam == 'spam'
    assert OR_SCHEMA.digit == 100
