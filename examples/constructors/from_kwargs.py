from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch

markup = "100 lorem; 200 dolor"


class Schema(BaseSchema):
    word: ScField[str, ReMatch(r"([a-zA-Z]+)")]
    digit: ScField[int, ReMatch(r"(\d+)")]


print(Schema.from_kwargs(word="kwarg word", digit=0))
# Schema(word:str='kwarg word', digit:int=0)
print(Schema.from_kwargs(word={"spam": "egg"}, digit="lol", foo="bar"))
# Schema(word:dict={'spam': 'egg'}, digit:str='lol', foo:str='bar')
print(Schema.from_kwargs())
# Schema()
