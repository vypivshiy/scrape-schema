from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch

markup = "100 lorem; 200 dolor"


class Schema(BaseSchema):
    word: ScField[str, ReMatch(r"([a-zA-Z]+)")]
    digit: ScField[int, ReMatch(r"(\d+)")]


# get last string from split("; ") method
# "100 lorem; 200 dolor".split("; ")
# ["100 lorem", "200 dolor"]
print(Schema.from_crop_rule(markup, crop_rule=lambda s: s.split("; ")[-1]))
# Schema(word:str='dolor', digit:int=200)
