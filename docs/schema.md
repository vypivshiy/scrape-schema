# BaseSchema
The primary means of defining objects in scrape_schema is via models 
(classes inherited from `BaseSchema`).

# Constructors

## Default init constructor
### Params
- `markup: str` - target string for parsing
- `parse_markup: bool` - parse fields object. Default True
- `**kwargs` - keyword arguments for setattr in schema

### Example
```python
from typing import Annotated
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch

markup = "100 lorem"


class Schema(BaseSchema):
    word: Annotated[str, ReMatch(r"([a-zA-Z]+)")]
    digit: Annotated[int, ReMatch(r"(\d+)")]


print(Schema(markup))
# Schema(word:str='lorem', digit:int=100)
```
## from_markup
Parse fields from markup. Alias for `BaseSchema(markup, parse_markup=True, **kwargs)`

### Params:
- `markup: str` - target string for parsing
- `**kwargs: Any` - keyword arguments for setattr in schema

### Example
```python
from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch

markup = "100 lorem"


class Schema(BaseSchema):
    word: ScField[str, ReMatch(r"([a-zA-Z]+)")]
    digit: ScField[int, ReMatch(r"(\d+)")]


print(*Schema.from_markup(markup))
# Schema(word:str='lorem', digit:int=100)
```
## from_list
parse fields from list of markups

### Params:
- `markups: Iterable[str]` - sequence of strings 
- `**kwargs: Any` - any keyword arguments for setattr in schema

### Example
```python
from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch

markups = ["100 lorem", "200 dolor"]


class Schema(BaseSchema):
    word: ScField[str, ReMatch(r"([a-zA-Z]+)")]
    digit: ScField[int, ReMatch(r"(\d+)")]


print(*Schema.from_list(markups), sep="\n")
# Schema(word:str='lorem', digit:int=100)
# Schema(word:str='dolor', digit:int=200)
```

## from_crop_rule
Split string by crop_rule method and return schema object

### Params
- `markup: str` – target string for parsing
- `crop_rule: Callable[[str], str]` – crop rule function to **one part**.
- `**kwargs: Any` - any keyword arguments for setattr in schema

### Example
```python
from scrape_schema import BaseSchema, ScField
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
```
## from_crop_rule_list

### Params
* `markup: str` – target string for parsing
* `crop_rule: Callable[[str], Iterable[str]]` – crop rule function to **parts**.
* `**kwargs: Any` - keyword arguments for setattr in schema

### Example
```python
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

```
## from_kwargs
Disable parse fields and set arguments manual. 

Alias for `BaseSchema("", parse_markup=False, **kwargs)`
### Params
- `**kwargs: Any` keyword arguments for setattr in schema

>> Note: 
> This method doesn't validate types and does not automatically typecast attributes!
> 
> This method is like a dataclass on minimal

```python
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
```

# Config
`Config` (inherited from `BaseConfig`) class contains configurations in `BaseSchema`.

### Params
- `config_parser: dict[Type[Any], dict[str, Any]]` - third-party parsers configurations. 
If you are using third party libraries and don't specify them - 
- the scheme throw `MarkupNotFoundError` exception in runtime.

```python
from selectolax.parser import HTMLParser
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList

class Schema(BaseSchema):
    title: ScField[str, SlaxSelect("title")]
    a: ScField[list[str], SlaxSelectList("a")]
    # ... any fields
Schema("...")
# MarkupNotFoundError
```

```python
# Add BeautifulSoup, selectolax parsers support
from selectolax.parser import HTMLParser
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList

class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "lxml"}, HTMLParser: {}}
    title: ScField[str, SlaxSelect("title")]
    a: ScField[list[str], SlaxSelectList("a")]
    # ... any fields
```

* type_caster: bool - enable type-casting feature. Default `True`
* fail_attempts: int - inclusion of check on success of obtaining data from the field **(compares to default value)**.

| value | mode    | description                                                                                                          |
|-------|---------|----------------------------------------------------------------------------------------------------------------------|
| < 0   | disable | disable fields values checker (default)                                                                              |
| == 0  | enable  | throw `ParseFailAttemptsError` if _first_ field return `default` value                                               |
| n > 0 | enable  | print *n* warning's messages if field return `default` value. if n == fail_attempts - throw `ParseFailAttemptsError` |

```python
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields.regex import ReMatch


class FailedSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        fails_attempt = 0

    foo: ScField[str, ReMatch(r"(lorem)")]
    fail: ScField[str, ReMatch(r"(\d+)")]


FailedSchema("lorem upsum dolor")
# raise `ParseFailAttemptsError`
```
_____
```python
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields.regex import ReMatch


class FailedSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        fails_attempt = 1

    foo: ScField[str, ReMatch(r"(lorem)")]
    fail: ScField[str, ReMatch(r"(\d+)")]


FailedSchema("lorem upsum dolor")  # print warning message
```
____
```python
from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.fields.regex import ReMatch


class FailedSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        fails_attempt = 1

    foo: ScField[str, ReMatch(r"(lorem)")]
    fail_1: ScField[str, ReMatch(r"(\d+)")]
    fail_2: ScField[str, ReMatch(r"(\d+)")]


FailedSchema("lorem upsum dolor")
# print warning message, and raise `ParseFailAttemptsError`
```
___
# BaseField
The base class of the field for interacting with the `BaseSchema`

* `default` - default value if failed or not matched result. Default `None`

* `filter_` - filter values to this function rule. **Works only iterable fields**

* `callback` - eval function for first match result value 

* `factory` - convert result value to another type/struct. Avoid type-casting feature

| name   | callback arg                  | scope                                | parser lib         |
|--------|-------------------------------|--------------------------------------|--------------------|
| regex  | str                           | any text                             | re                 |
 | soup   | bs4.Tag                       | bs4.BeautifulSoup, (html, xml)       | bs4                |
| slax   | selectolax.parser.Node        | selectolax.parser.HTMLParser, (html) | selectolax(Modest) |
| parsel | parsel.selector._SelectorType | parsel.Selector, (html, xml)         | parsel             |

# type-casting
If in `Config` class set `type_casting = True`, then the scheme will try auto cast in the simple types.

**Auto type-casting doesn't work with:**
* Generics
* Union types **(except Optional)**
* A more complex types like: `dict[str, dict[str, dict[str, dict[str, int]]]]`
* A custom types/strictures like dataclasses, TypedDict, NamedTuple, etc


```python
# Error
from dataclasses import dataclass

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatchDict

@dataclass
class MyStruct:
    spam: str
    egg: int

    
class Schema(BaseSchema):
    foo: ScField[MyStruct, ReMatchDict(r'spam:(?P<spam>\w+) egg:(?P<egg>\d+)')]

...
```

If you need complex structures - convert them manually using the `factory` parameter

```python
# OK
from dataclasses import dataclass

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatchDict

@dataclass
class MyStruct:
    spam: str
    egg: int

    
class Schema(BaseSchema):
    foo: ScField[MyStruct, ReMatchDict(r'spam:(?P<spam>\w+) egg:(?P<egg>\d+)',
                                         factory=lambda dct: MyStruct(**dct))]

...
```

## factory
Change type-casting to this enchant function param. if this param None, try type-casting

```python
from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch


class Schema(BaseSchema):
    # convert 'hello' to 'hello' with usage type-casting
    hello: ScField[list[str], ReMatch(r'(hello)')]
    

print(Schema('hello world ').dict())  # {'hello': 'hello'} incorrect output type
```

with factory:

```python
from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch


class Schema(BaseSchema):
    # convert 'hello' to ['h', 'e', 'l', 'l', 'o'], without usage type-casting
    hello: ScField[list[str], ReMatch(r'(hello)', factory=list)]
    
    
print(Schema('hello world').dict())  # {'hello': ['h', 'e', 'l', 'l', 'o']} OK
```
