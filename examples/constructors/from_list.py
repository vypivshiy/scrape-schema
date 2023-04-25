from typing import Annotated
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch

markups = ["100 lorem", "200 dolor"]


class Schema(BaseSchema):
    word: Annotated[str, ReMatch(r"([a-zA-Z]+)")]
    digit: Annotated[int, ReMatch(r"(\d+)")]


print(*Schema.from_list(markups), sep="\n")
# Schema(word:str='lorem', digit:int=100)
# Schema(word:str='dolor', digit:int=200)
