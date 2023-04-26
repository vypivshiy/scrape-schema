from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch

markups = ["100 lorem", "200 dolor"]


class Schema(BaseSchema):
    word: ScField[str, ReMatch(r"([a-zA-Z]+)")]
    digit: ScField[int, ReMatch(r"(\d+)")]


print(*Schema.from_list(markups), sep="\n")
# Schema(word:str='lorem', digit:int=100)
# Schema(word:str='dolor', digit:int=200)
