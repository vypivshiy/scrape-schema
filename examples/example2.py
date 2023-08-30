# mypy: disable-error-code="assignment"
# FIXME need create mypy plugin

from scrape_schema import BaseSchema, Text


class Schema(BaseSchema):
    digit: int = Text().re_search(r"\d+")[0]
    word: str = Text().re_search(r"[a-zA-Z]+")[0]


sc = Schema("test 100")
