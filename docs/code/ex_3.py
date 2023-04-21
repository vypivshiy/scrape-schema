import json
import pprint
from dataclasses import dataclass
from typing import Annotated, Optional

from scrape_schema import BaseSchema
from scrape_schema.fields.nested import Nested, NestedList
from scrape_schema.fields.regex import ReMatch, ReMatchList


@dataclass
class WordData:
    word: Optional[str]
    digit: Optional[int]


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
    digits: Annotated[
        str,
        Nested(Digits, crop_rule=lambda s: s, factory=lambda sc: json.dumps(sc.dict())),
    ]
    words: Annotated[
        list[WordData],
        NestedList(
            Word,
            crop_rule=lambda s: s.split(),
            factory=lambda scs: [WordData(**sc.dict()) for sc in scs],
        ),
    ]
    sample_string: Annotated[
        str,
        Nested(
            Word,
            crop_rule=lambda s: s,
            factory=lambda sc: " ".join([str(_) for _ in sc.dict().values()]),
        ),
    ]


schema = HelloWorld("1 2 3 hello world 4 5 6 7 8 9 0")
pprint.pprint(schema.dict(), compact=True)
# {'digits': '{"digits": [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], "odd_digits": [1, 3, 5, '
#            '7, 9], "even_digits": [2, 4, 6, 8, 0], "sum": 45, "max": 9, "min": '
#            '0}',
#  'hello': 'hello',
#  'sample_string': '1 hello',
#  'words': [WordData(word=None, digit=1), WordData(word=None, digit=2),
#            WordData(word=None, digit=3), WordData(word='hello', digit=None),
#            WordData(word='world', digit=None), WordData(word=None, digit=4),
#            WordData(word=None, digit=5), WordData(word=None, digit=6),
#            WordData(word=None, digit=7), WordData(word=None, digit=8),
#            WordData(word=None, digit=9), WordData(word=None, digit=0)],
#  'world': ['w', 'o', 'r', 'l', 'd']}
