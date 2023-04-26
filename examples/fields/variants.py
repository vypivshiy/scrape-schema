# TODO documentary this
from typing import Optional

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch


class Schema(BaseSchema):
    digit: ScField[Optional[int], (ReMatch(r"spam=(\d+)"), ReMatch(r"egg=(\d+)"))]

    word: ScField[Optional[str], (ReMatch(r"egg=([a-z]+)"), ReMatch(r"spam=([a-z]+)"))]


if __name__ == "__main__":
    print(Schema("egg=100\nspam=lorem").dict())
    # {'digit': 100, 'word': 'lorem'}
