from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch

markup = "100 lorem; 200 dolor"


class Schema(BaseSchema):
    word: ScField[str, ReMatch(r"([a-zA-Z]+)")]
    digit: ScField[int, ReMatch(r"(\d+)")]


# get last string from split("; ") method
# "100 lorem; 200 dolor".split("; ")
# ["100 lorem", "200 dolor"]
print(*Schema.from_crop_rule_list(markup, crop_rule=lambda s: s.split("; ")), sep="\n")
# Schema(word:str='lorem', digit:int=100)
# Schema(word:str='dolor', digit:int=200)
