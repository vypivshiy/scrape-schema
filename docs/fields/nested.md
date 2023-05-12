# nested
The `Nested` and `NestedList` fields allow for the nested extraction of data by defining a sub-schema. 
These fields can be used when the target data contains substructures that can be parsed as separate schemas, 
and then combined with the parent schema.

# Nested
## Params:
* `schema: Type[BaseSchema]` - Child Schema class
* `crop_rule: Callable[[str], str]` - split text to part function 
* `factory: Optional[Callable[[BaseSchema], Any]]` - optional rule for conversions to a different type/struct
* `parser : Optional[Type]` - optional parser instance: get by class cached parser from schema instance.
**this feature increase speed by 25%!** if the parser was not cached - raise `AttributeError` 
(new in 0.2.4) 

## Usage
```python
from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch
from scrape_schema.fields import Nested

TEXT = "dolor 100; John Wick 0 old"

class Person(BaseSchema):
    name: ScField[str, ReMatch(r"([A-Z][a-z]+ [A-Z][a-z]+)")]
    age: ScField[int, ReMatch(r"(\d+)")]

class Schema(BaseSchema):
    name: ScField[Person, Nested(Person, crop_rule=lambda s: s.split("; ")[-1])]
    name_values: ScField[tuple[str, int], Nested(Person, 
                                     crop_rule=lambda s: s.split("; ")[-1],
                                     factory=lambda sc: tuple(sc.dict().values()))]
    word: ScField[str, ReMatch(r"(\w+)")]
    digit: ScField[float, ReMatch(r"(\d+)")]

print(Schema(TEXT))
# Schema(name=Person(name:str='John Wick', age:int=0), 
# name_values:tuple=('John Wick', 0), word:str='dolor', digit:float=100.0)
```

# NestedList
## Params
* `schema: Type[BaseSchema]` - Child Schema class
* `crop_rule: Callable[[str], List[str]]` - split text to parts function
* `factory: Optional[Callable[[BaseSchema], Any]]` - optional rule for conversions to a different type/struct

## Usage
```python
from typing import List
from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch
from scrape_schema.fields import NestedList

TEXT = "name shop_list: Thing cost 1 dolors; Egg cost 0.5 dolors; Spam cost 5 dolors"

class Item(BaseSchema):
    name: ScField[str, ReMatch("([A-Z][a-z]+)")]
    price: ScField[float, ReMatch("cost ((?<!\S)\d+(?:\.\d+)?(?!\S))")]


class Schema(BaseSchema):
    name: ScField[str, ReMatch(r"name (\w+)")]
    items: ScField[List[Item], NestedList(Item, crop_rule=lambda s: s.split(": ")[-1].split("; "))]
    expensive_item: ScField[Item, NestedList(Item, 
                                             crop_rule=lambda s: s.split(": ")[-1].split("; "),
                                             factory=lambda lst: max(lst, key=lambda sc: sc.price))]

print(Schema(TEXT))
# Schema(name:str='shop_list', 
# items:list=[
# Item(name:str='Thing', price:float=1.0), 
# Item(name:str='Egg', price:float=0.5), 
# Item(name:str='Spam', price:float=5.0)], 
# expensive_item=Item(name:str='Spam', price:float=5.0))
```
# Example

```python
import pprint
import json
from dataclasses import dataclass
from typing import Optional

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchList
from scrape_schema.fields.nested import Nested, NestedList


@dataclass
class WordData:
    word: Optional[str]
    digit: Optional[int]


class Digits(BaseSchema):
    digits: ScField[list[int], ReMatchList(r'(\d+)')]
    odd_digits: ScField[list[int], ReMatchList(r'(\d+)', filter_=lambda i: int(i) % 2 != 0)]
    even_digits: ScField[list[int], ReMatchList(r'(\d+)', filter_=lambda i: int(i) % 2 == 0)]
    sum: ScField[int, ReMatchList(r'(\d+)', callback=int, factory=sum)]
    max: ScField[int, ReMatchList(r'(\d+)', callback=int, factory=max)]
    min: ScField[int, ReMatchList(r'(\d+)', callback=int, factory=min)]


class Word(BaseSchema):
    digit: ScField[Optional[int], ReMatch(r"(\d+)")]
    word: ScField[Optional[str], ReMatch(r"([a-z]+)")]


class HelloWorld(BaseSchema):
    hello: ScField[str, ReMatch(r"(hello) world")]
    world: ScField[list[str], ReMatch(r"(hello) (world)", group=2, factory=list)]
    digits: ScField[str, Nested(Digits,
                                  crop_rule=lambda s: s,
                                  factory=lambda sc: json.dumps(sc.dict()))]
    words: ScField[list[WordData], NestedList(Word,
                                                crop_rule=lambda s: s.split(),
                                                factory=lambda scs: [WordData(**sc.dict()) for sc in scs])]
    sample_string: ScField[str, Nested(Word,
                                         crop_rule=lambda s: s,
                                         factory=lambda sc: " ".join([str(_) for _ in sc.dict().values()]))]


schema = HelloWorld('1 2 3 hello world 4 5 6 7 8 9 0')
pprint.pprint(schema.dict(), compact=True)
# {'digits': '{"digits": [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], "odd_digits": [1, 3, 5, '
#            '7, 9], "even_digits": [2, 4, 6, 8, 0], "sum": 45, "max": 9, "min": '
#            '0}',
#  'hello': 'hello',
#  'sample_string': '1 hello',
#  'words': [WordData(word=None, digit=1), WordData(word=None, digit=2),
#            WordData(word=None, digit=3), WordData(word='hello', digit=None),
#            WordData(word='world', digit=None), WordData(word=None, digit=4),
#            WordData(word=None, digit=5), WordData(word=None, digit=6),
#            WordData(word=None, digit=7), WordData(word=None, digit=8),
#            WordData(word=None, digit=9), WordData(word=None, digit=0)],
#  'world': ['w', 'o', 'r', 'l', 'd']}
```

Usage Nested factory param example:

```python
import pprint
import json
from dataclasses import dataclass
from typing import Optional

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchList
from scrape_schema.fields.nested import Nested, NestedList


@dataclass
class WordData:
    word: Optional[str]
    digit: Optional[int]


class Digits(BaseSchema):
    digits: ScField[list[int], ReMatchList(r'(\d+)')]
    odd_digits: ScField[list[int], ReMatchList(r'(\d+)', filter_=lambda i: int(i) % 2 != 0)]
    even_digits: ScField[list[int], ReMatchList(r'(\d+)', filter_=lambda i: int(i) % 2 == 0)]
    sum: ScField[int, ReMatchList(r'(\d+)', callback=int, factory=sum)]
    max: ScField[int, ReMatchList(r'(\d+)', callback=int, factory=max)]
    min: ScField[int, ReMatchList(r'(\d+)', callback=int, factory=min)]


class Word(BaseSchema):
    digit: ScField[Optional[int], ReMatch(r"(\d+)")]
    word: ScField[Optional[str], ReMatch(r"([a-z]+)")]


class HelloWorld(BaseSchema):
    hello: ScField[str, ReMatch(r"(hello) world")]
    world: ScField[list[str], ReMatch(r"(hello) (world)", group=2, factory=list)]
    digits: ScField[str, Nested(Digits,
                                  crop_rule=lambda s: s,
                                  factory=lambda sc: json.dumps(sc.dict()))]
    words: ScField[list[WordData], NestedList(Word,
                                                crop_rule=lambda s: s.split(),
                                                factory=lambda scs: [WordData(**sc.dict()) for sc in scs])]


schema = HelloWorld('1 2 3 hello world 4 5 6 7 8 9 0')
pprint.pprint(schema.dict(), compact=True)
# {'digits': '{"digits": [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], "odd_digits": [1, 3, 5, '
#            '7, 9], "even_digits": [2, 4, 6, 8, 0], "sum": 45, "max": 9, "min": '
#            '0}',
#  'hello': 'hello',
#  'words': [WordData(word=None, digit=1), WordData(word=None, digit=2),
#            WordData(word=None, digit=3), WordData(word='hello', digit=None),
#            WordData(word='world', digit=None), WordData(word=None, digit=4),
#            WordData(word=None, digit=5), WordData(word=None, digit=6),
#            WordData(word=None, digit=7), WordData(word=None, digit=8),
#            WordData(word=None, digit=9), WordData(word=None, digit=0)],
#  'world': ['w', 'o', 'r', 'l', 'd']}
```

>>> **Note** : 
> Unless necessary, it is better not to convert Nested objects into other structures 
> such as data classes and others, but to do this with a ready-made schema, 
> converting it into a dictionary

```python
from typing import Optional
import json

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchList
from scrape_schema.fields.nested import Nested, NestedList


class Digits(BaseSchema):
    digits: ScField[list[int], ReMatchList(r'(\d+)')]
    odd_digits: ScField[list[int], ReMatchList(r'(\d+)', filter_=lambda i: int(i) % 2 != 0)]
    even_digits: ScField[list[int], ReMatchList(r'(\d+)', filter_=lambda i: int(i) % 2 == 0)]
    sum: ScField[int, ReMatchList(r'(\d+)', callback=int, factory=sum)]
    max: ScField[int, ReMatchList(r'(\d+)', callback=int, factory=max)]
    min: ScField[int, ReMatchList(r'(\d+)', callback=int, factory=min)]

    
class Word(BaseSchema):
    digit: ScField[Optional[int], ReMatch(r"(\d+)")]
    word: ScField[Optional[str], ReMatch(r"([a-z]+)")]

    
class HelloWorld(BaseSchema):
    hello: ScField[str, ReMatch(r"(hello) world")]
    world: ScField[list[str], ReMatch(r"(hello) (world)", group=2, factory=list)]
    digits: ScField[Digits, Nested(Digits, crop_rule=lambda s: s)]
    words: ScField[list[Word], NestedList(Word, crop_rule=lambda s: s.split())]


schema = HelloWorld('1 2 3 hello world 4 5 6 7 8 9 0')
print(json.dumps(schema.dict()))
```