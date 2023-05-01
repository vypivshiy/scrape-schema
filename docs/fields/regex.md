# regex
Usage build-in `re` library

# Schema Config
this fields didn't require configuration

# Field methods

- `extract(self, markup: str, type_: Optional[Type] = None) -> Any`: Extracts data from the input text using the regular 
expression pattern and any provided callbacks and factories. Returns the extracted data.
## Params
- `markup: str` - Text to parse
- `type_: Optional[Type] = str`: The type to cast the matched string(s) to. This is only used if `factory` 
is not provided.

# ReMatch
Matches a regular expression pattern and returns the first match as a string or other specified type.

## Params:
- `pattern: str | re.Pattern` - regular expression pattern
- `group: int` - numbered group references. Default `1`
- `flags: int | re.Flag` - regex flags compilation. Default `0`
- `default: Optional[Any]` - default value, if match not founded. Default `None`
- `callback: Optional[Callable[[str], Any]]`: A function that transforms the matched string into 
another value. If not provided, the matched string is returned as is. Default `None`
- `factory: Optional[Callable[[Any], Any]] = None`: A function that processes the value. 
**Disable type-cast feature**. Default `None`

## Usage:
```python
from scrape_schema.fields.regex import ReMatch

re_match = ReMatch(r"([a-zA-Z]+)")
print(re_match.extract("Lorem Ipsum")) # "Lorem"

re_match_2 = ReMatch(r"(\d+)", callback=int)
print(re_match_2.extract("Lorem Ipsum 100")) # 100
print(re_match_2.extract("Lorem Ipsum 100", type_=float)) # 100.0

re_match_3 = ReMatch(r"(\d+)")
print(re_match_3.extract("abcd"))  # None
print(re_match_3.extract("10"))  # "10"
print(re_match_3.extract("10", type_=float))  # 10.0

re_match_4 = ReMatch(r"([a-z]+)", default="default word")
print(re_match_4.extract("9000"))  # "default word"

re_match_5 = ReMatch(r"([a-z]+)", factory=list)
print(re_match_5.extract("hello world"))  # ["h", "e", "l", "l", "o"]
# factory cannot overwrite factory function
print(re_match_5.extract("hello world", type_=str))  # ["h", "e", "l", "l", "o"]
```

# ReMatchList
Matches a regular expression pattern and returns all matches as a list of strings or other specified type.
## Params:
- `pattern: str | re.Pattern` - regular expression pattern 
- `group: int` - numbered group references. Default `1`
- `flags: int | re.Flag` - regex flags compilation. Default `0`
- `default: Optional[Any]` - default value, if matches not founded. Default `None`
- `filter_: Optional[Callable[[str], bool]]` -  A filter matched result. Default `None`
- `callback: Optional[Callable[[str], Any]]` - A function that transforms the matched string into 
another value. If not provided, the matched string is returned as is. Default `None`
- `factory: Optional[Callable[[Any], Any]]` - A function that processes the list of matches. 
**Disable type-cast feature**. Default `None`

## Usage
```python
from scrape_schema.fields.regex import ReMatchList

re_match_list = ReMatchList(r"([a-z]+)")
print(re_match_list.extract("lorem upsum dolor"))
# ["lorem", "upsum", "dolor"]

re_match_list_2 = ReMatchList(r"([a-z]+)", callback=lambda s: s.upper())
print(re_match_list_2.extract("lorem upsum dolor"))
# ["LOREM", "UPSUM", "DOLOR"]
  
re_match_list_3 = ReMatchList(r"(\d+)", factory=lambda lst: ", ".join(lst))
print(re_match_list_3.extract("1 2 3 4 5"))
# "1, 2, 3, 4, 5"

re_match_list_4 = ReMatchList(r"(\d+)", filter_=lambda m: int(m) > 10)
print(re_match_list_4.extract("2 4 6 8 10 12 14"))
# ["12", "14"]

re_match_list_5 = ReMatchList(r"(\d+)", filter_=lambda m: int(m) > 10, callback=int)
print(re_match_list_5.extract("2 4 6 8 10 12 14"))
# [12, 14]
```

# ReMatchDict
Matches a regular expression pattern and returns the first match a group dict
## Params:
- `pattern: str | re.Pattern` - regular expression pattern. **Required named groups**
- `flags: int | re.Flag` - regex flags compilation. Default `0`
- `default: Optional[Any]` - default value, if matches not founded. Default `None`
- `callback: Optional[Callable[[Dict[str, str]], Any]]` A function that transforms the matched string into 
another value. If not provided, the matched string is returned as is. Default `None`
- `factory: Optional[Callable[[Any], Any]]`: A function that processes the list of matches. 
**Disable type-cast feature**. Default `None`

## Usage
```python
from typing import Optional
from scrape_schema.fields.regex import ReMatchDict

re_match_dict_1 = ReMatchDict(
    r'(?P<lat>-?\d+\.\d+),(?P<long>-?\d+\.\d+)')
print(re_match_dict_1.extract('37.7749,-122.4194'))
# {'lat': '37.7749', 'long': '-122.4194'}

print(re_match_dict_1.extract('37.7749,-122.4194', type_=dict[str, float]))
# {'lat': 37.7749, 'long': -122.4194}

print(re_match_dict_1.extract('37.7749,-122.4194', type_=Optional[dict[str, float]]))
# {'lat': 37.7749, 'long': -122.4194}

print(re_match_dict_1.extract('', type_=Optional[dict[str, float]]))
# None

print(re_match_dict_1.extract('37.7749,-122.4194', type_=bool))
# True

print(re_match_dict_1.extract('', type_=bool))
# False

print(re_match_dict_1.extract('', type_=Optional[bool]))
# None

re_match_dict_2 = ReMatchDict(
    r"(?P<first>\w+) (?P<last>\w+): (?P<age>\d+) years old")

print(re_match_dict_2.extract("John Smith: 42 years old"))
# {'first': 'John', 'last': 'Smith', "age": "42"}

def _re_match_dict_callback(dct: dict[str, str]):
    dct["age"] = int(dct["age"])
    return dct

re_match_dict_3 = ReMatchDict(
    r"(?P<first>\w+) (?P<last>\w+): (?P<age>\d+) years old",
    callback=_re_match_dict_callback)

print(re_match_dict_3.extract("John Smith: 42 years old"))
# {'first': 'John', 'last': 'Smith', "age": 42}

re_match_dict_4 = ReMatchDict(
    r"(?P<first>\w+) (?P<last>\w+): (?P<age>\d+) years old",
    factory=lambda dct: f"{dct['first']}_{dct['last']}_{dct['age']}")

print(re_match_dict_4.extract("John Smith: 42 years old"))  
# "John_Smith_42"
```
# ReMatchListDict
Matches a regular expression pattern and returns all matches as a groups dict
## Params
- `pattern: str | Pattern` - compiled regex or string pattern. **Required named groups**
- `flags: int | re.Flag` - regex flags compilation. Default `0`
- `default: Optional[Any]` - default value, if matches not founded. Default `None`
- `filter_: Optional[Callable[[Dict[str, str]], bool]]` - A filter matched result. Default `None`
- `callback: Optional[Callable[[Dict[str, str]], Any]]` - A function that transforms the matched string into 
another value. If not provided, the matched string is returned as is. Default `None`
- `factory: Optional[Callable[[Any], Any]]`  - A function that processes the list of matches. 
**Disable type-cast feature**. Default `None`

## Usage
```python
from typing import Optional
from scrape_schema.fields.regex import ReMatchListDict

re_match_list_dict = ReMatchListDict(r'(?P<lat>-?\d+\.\d+),(?P<long>-?\d+\.\d+)')
print(re_match_list_dict.extract('37.7749,-122.4194 37.8202,-122.2194'))
# [{'lat': '37.7749', 'long': '-122.4194'}, {'lat': '37.8202', 'long': '-122.2194'}]

print(re_match_list_dict.extract('37.7749,-122.4194 37.8202,-122.2194', type_=list[dict[str, float]]))
# [{'lat': 37.7749, 'long': -122.4194}, {'lat': 37.8202, 'long': -122.2194}]

print(re_match_list_dict.extract('37.7749,-122.4194 37.8202,-122.2194', 
                                 type_=Optional[dict[str, float]]))
# [{'lat': 37.7749, 'long': -122.4194}, {'lat': 37.8202, 'long': -122.2194}]

print(re_match_list_dict.extract('', type_=Optional[dict[str, float]]))  # None

print(re_match_list_dict.extract('37.7749,-122.4194 37.8202,-122.2194', type_=bool))  # True

print(re_match_list_dict.extract('', type_=bool))  # False

print(re_match_list_dict.extract('', type_=Optional[bool]))  # None

re_match_list_dict_2 = ReMatchListDict(r'(?P<lat>-?\d+\.\d+),(?P<long>-?\d+\.\d+)', 
                                     callback=lambda dct: tuple(dct.values()))

print(re_match_list_dict_2.extract('37.7749,-122.4194 37.8202,-122.2194'))
# [('37.7749', '-122.4194'), ('37.8202', '-122.2194')]
```

## Schema Usage
```python
from typing import List, Dict  # python 3.8 support
from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchList, ReMatchDict, ReMatchListDict


markup = "100 lorem coordinates: 37.7749,-122.4194 37.8202,-122.2194 dolor"


class Schema(BaseSchema):
    word: ScField[str, ReMatch(r"([a-zA-Z]+)")]
    word_list: ScField[List[str], ReMatchList(r"([a-zA-Z]+)")]
    digit: ScField[int, ReMatch(r"(\d+)")]
    coord: ScField[Dict[str, float], ReMatchDict(r'(?P<lat>-?\d+\.\d+),(?P<long>-?\d+\.\d+)')]
    coord_list: ScField[List[Dict[str, float]], ReMatchListDict(r'(?P<lat>-?\d+\.\d+),(?P<long>-?\d+\.\d+)')]

    
print(Schema(markup))
# Schema(word:str='lorem', word_list:list=['lorem', 'coordinates', 'dolor'], digit:int=100, 
# coord:dict={'lat': 37.7749, 'long': -122.4194}, 
# coord_list:list=[{'lat': 37.7749, 'long': -122.4194}, {'lat': 37.8202, 'long': -122.2194}])
```


# Reference:

* https://docs.python.org/3.11/library/re.html

* https://docs.python.org/3.11/library/re.html#regular-expression-syntax

* https://docs.python.org/3.11/library/re.html#flags

* https://docs.python.org/3.11/howto/regex.html#regex-howto

* https://docs.python.org/3.11/library/re.html#re.search

* https://docs.python.org/3.11/library/re.html#re.Match.group

* https://docs.python.org/3.11/library/re.html#re.finditer

* https://docs.python.org/3.11/library/re.html#re.Match.groupdict