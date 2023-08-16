from typing import List, Optional

from tests.fixtures import JSON_TEXT

from scrape_schema import BaseSchema, JMESPath, Sc


class JsonSchema(BaseSchema):
    args: Sc[List[str], JMESPath().jmespath("args").getall()]
    headers: Sc[dict, JMESPath().jmespath("headers").get()]
    url: Sc[Optional[str], JMESPath(default=None).jmespath("url").get()]


def test_parse():
    schema = JsonSchema(JSON_TEXT)
    assert schema.dict() == {
        "args": ["spam", "egg"],
        "headers": {"user-agent": "Mozilla 5.0", "lang": "en-US"},
        "url": None,
    }
