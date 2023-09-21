from uuid import uuid4

from scrape_schema import BaseSchema, Callback


class CallbackSchema(BaseSchema):
    uuid: str = Callback(lambda: str(uuid4()))


def test_callback_schema():
    assert len(CallbackSchema("").uuid) == 36
