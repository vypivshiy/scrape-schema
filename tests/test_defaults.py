# mypy: disable-error-code="assignment"
from typing import List, Optional

from scrape_schema import BaseSchema, Parsel


class SchemaDefaults(BaseSchema):
    a: str = Parsel(default="a").css("a").get()
    b: Optional[str] = Parsel().css("a").get()
    c: List[str] = Parsel().css("a").getall()
    d: Optional[List[str]] = Parsel(default=None).css("a").getall()


def test_defaults():
    assert SchemaDefaults("a").dict() == {"a": "a", "b": None, "c": [], "d": None}
