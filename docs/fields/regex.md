# regex
Usage build-in `re` library

# Schema Config
this fields didn't require configuration

# ReMatch, ReMatchList
* pattern - compiled regex or string pattern
* group - numbered group references. **default 1**
* flags - regex flags compilation, **default 0**

# ReMatchDict, ReMatchListDict 
* pattern - compiled regex or string pattern. This pattern required [named group(s)](https://docs.python.org/3/howto/regex.html#non-capturing-and-named-groups)
* flags - regex flags compilation, **default 0**

# Example
Without schema:
```python
from scrape_schema.fields.regex import ReMatch, ReMatchList, ReMatchDict, ReMatchListDict


ReDigit = ReMatch(r"(\d+)")
ReWord = ReMatch(r"([a-zA-Z]+)")

ReDigits = ReMatchList(r"(\d+)")
ReWords = ReMatchList(r"([a-zA-Z]+)")

ReSentence = ReMatchList(r"([a-zA-Z]+)", factory=lambda lst: " ".join(lst))
ReSum = ReMatchList(r"(\d+)", callback=int, factory=sum)

ReDigitDict = ReMatchDict(r"(?P<digit>\d+)")
ReDigitListDict = ReMatchListDict(r"(?P<digit>\d+)")

TEXT = "lorem 10 upsum 100 900 dolor"

digit: int = ReDigit.extract(TEXT, type_=int)
digits: list[int] = ReDigits.extract(TEXT, type_=list[int])
digits_sum: int = ReSum.extract(TEXT)
print(digit, digits, digits_sum, sep="\n--\n")

word: str = ReWord.extract(TEXT)
words: list[str] = ReWords.extract(TEXT)
sentence: str = ReSentence.extract(TEXT)
print(word, words, sentence, sep="\n--\n")

digit_dict: dict[str, int] = ReDigitDict.extract(TEXT, type_=dict[str, int])
digit_list_dict: list[dict[str, str]] = ReDigitListDict.extract(TEXT)
print(digit_dict, digit_list_dict, sep="\n--\n")
# 10
# --
# [10, 100, 900]
# --
# 1010
# lorem
# --
# ['lorem', 'upsum', 'dolor']
# --
# lorem upsum dolor
# {'digit': 10}
# --
# [{'digit': '10'}, {'digit': '100'}, {'digit': '900'}]
```
With schema:
```python
from typing import Annotated
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch, ReMatchList


class HelloWorld(BaseSchema):
    hello: Annotated[str, ReMatch(r"(hello) world")]
    world: Annotated[list[str], ReMatch(r"(hello) (world)", group=2, factory=list)]
    digits: Annotated[list[int], ReMatchList(r'(\d+)')]
    odd_digits: Annotated[list[int], ReMatchList(r'(\d+)', filter_=lambda i: int(i) % 2 != 0)]
    even_digits: Annotated[list[int], ReMatchList(r'(\d+)', filter_=lambda i: int(i) % 2 == 0)]
    sum: Annotated[int, ReMatchList(r'(\d+)', callback=int, factory=sum)]
    max: Annotated[int, ReMatchList(r'(\d+)', callback=int, factory=max)]
    min: Annotated[int, ReMatchList(r'(\d+)', callback=int, factory=min)]


schema = HelloWorld('1 2 3 hello world 4 5 6 7 8 9 0')
print(schema.dict())
# {'hello': 'hello', 
# 'world': ['w', 'o', 'r', 'l', 'd'], 
# 'digits': [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], 
# 'odd_digits': [1, 3, 5, 7, 9], 
# 'even_digits': [2, 4, 6, 8, 0], 
# 'sum': 45, 
# 'max': 9, 
# 'min': 0}
```
