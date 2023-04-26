from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch

markup = "100 lorem"


class Schema(BaseSchema):
    word: ScField[str, ReMatch(r"([a-zA-Z]+)")]
    digit: ScField[int, ReMatch(r"(\d+)")]


print(Schema(markup))
# Schema(word:str='lorem', digit:int=100)
