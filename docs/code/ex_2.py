import pprint
from typing import Annotated, Optional

from scrape_schema import BaseSchema
from scrape_schema.fields.nested import Nested, NestedList
from scrape_schema.fields.regex import ReMatch, ReMatchList


class Digits(BaseSchema):
    digits: Annotated[list[int], ReMatchList(r"(\d+)")]
    odd_digits: Annotated[
        list[int], ReMatchList(r"(\d+)", filter_=lambda i: int(i) % 2 != 0)
    ]
    even_digits: Annotated[
        list[int], ReMatchList(r"(\d+)", filter_=lambda i: int(i) % 2 == 0)
    ]
    sum: Annotated[int, ReMatchList(r"(\d+)", callback=int, factory=sum)]
    max: Annotated[int, ReMatchList(r"(\d+)", callback=int, factory=max)]
    min: Annotated[int, ReMatchList(r"(\d+)", callback=int, factory=min)]


class Word(BaseSchema):
    digit: Annotated[Optional[int], ReMatch(r"(\d+)")]
    word: Annotated[Optional[str], ReMatch(r"([a-z]+)")]


class HelloWorld(BaseSchema):
    hello: Annotated[str, ReMatch(r"(hello) world")]
    world: Annotated[list[str], ReMatch(r"(hello) (world)", group=2, factory=list)]
    digits: Annotated[Digits, Nested(Digits, crop_rule=lambda s: s)]  # ignore crop text
    words: Annotated[list[Word], NestedList(Word, crop_rule=lambda s: s.split())]


schema = HelloWorld("1 2 3 hello world 4 5 6 7 8 9 0")
pprint.pprint(schema.dict(), compact=True)
