from typing import Annotated
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch

markup = "100 lorem"


class Schema(BaseSchema):
    word: Annotated[str, ReMatch(r"([a-zA-Z]+)")]
    digit: Annotated[int, ReMatch(r"(\d+)")]


print(Schema(markup))
# Schema(word:str='lorem', digit:int=100)