from typing import Annotated

from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch, ReMatchList


class HelloWorld(BaseSchema):
    hello: Annotated[str, ReMatch(r"(hello) world")]
    world: Annotated[list[str], ReMatch(r"(hello) (world)", group=2, factory=list)]
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


schema = HelloWorld("1 2 3 hello world 4 5 6 7 8 9 0")

print(schema.dict())
# {'hello': 'hello',
# 'world': ['w', 'o', 'r', 'l', 'd'],
# 'digits': [1, 2, 3, 4, 5, 6, 7, 8, 9, 0],
# 'odd_digits': [1, 3, 5, 7, 9],
# 'even_digits': [2, 4, 6, 8, 0],
# 'sum': 45,
# 'max': 9,
# 'min': 0}
