# BaseSchema
The primary means of defining objects in scrape_schema is via models 
(classes inherited from `BaseSchema`).

* markup: str - target string for parsing

# Config
`Config` (inherited from `BaseConfig`) class contains configurations in `BaseSchema`.

* config_parser: dict[Type[Any], dict[str, Any]] - backend parsers confing. If you are using third party backends and don't
specify them - the scheme throw `MarkupNotFoundError` exception in runtime.

```python
# Add BeautifulSoup, selectolax parsers support
from selectolax.parser import HTMLParser
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig


class Schema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "lxml"}, HTMLParser: {}}
    ...
```

* type_caster: bool - usage type casting feature. Default `True` 
* fail_attempts: int - inclusion of check on success of obtaining data from the field **(compares to default value)**.

| value | mode    | description                                                                                                          |
|-------|---------|----------------------------------------------------------------------------------------------------------------------|
| < 0   | disable | disable fields values checker (default)                                                                              |
| == 0  | enable  | throw `ParseFailAttemptsError` if _first_ field return `default` value                                               |
| n > 0 | enable  | print *n* warning's messages if field return `default` value. if n == fail_attempts - throw `ParseFailAttemptsError` |

```python
from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.fields.regex import ReMatch


class FailedSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        fails_attempt = 0

    foo = ReMatch(r"(lorem)")
    fail = ReMatch(r"(\d+)")


FailedSchema("lorem upsum dolor")
```
raise `ParseFailAttemptsError`
_____
```python
from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.fields.regex import ReMatch


class FailedSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        fails_attempt = 1

    foo = ReMatch(r"(lorem)")
    fail = ReMatch(r"(\d+)")


FailedSchema("lorem upsum dolor")
```
print warning message
____
```python
from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.fields.regex import ReMatch


class FailedSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        fails_attempt = 1

    foo = ReMatch(r"(lorem)")
    fail_1 = ReMatch(r"(\d+)")
    fail_2 = ReMatch(r"(\d+)")


FailedSchema("lorem upsum dolor")
```
print warning message, and raise `ParseFailAttemptsError`
___
# BaseField

The base class of the field for interacting with the `BaseSchema`

* `default` - default value if failed or not matched result. Default `None`

* `filter_` - filter values to this function rule. **Works only iterables**

* `callback` - eval function for first match result value 

* `factory` - convert result value to another type/struct avoid type-casting feature

| name  | callback arg   | scope               | backend              |
|-------|----------------|---------------------|----------------------|
| regex | str            | any text            | re                   |
 | soup  | Tag            | BeautifulSoup, html | bs4                  |
| slax  | Node           | HTMLParser, html    | selectolax(Modest)   |

# type-casting
If in `Config` class set `type_casting = True`, then the scheme will try auto cast in the simple types.

**Auto type-casting doesn't work with:**
* Generics
* A more complex types like: `dict[str, dict[str, dict[str, dict[str, int]]]]`
* A custom types/strictures like dataclasses, TypedDict, NamedTuple, etc


```python
# Error
from dataclasses import dataclass
from typing import Annotated

from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatchDict

@dataclass
class MyStruct:
    spam: str
    egg: int

    
class Schema(BaseSchema):
    foo: Annotated[MyStruct, ReMatchDict(r'spam:(?P<spam>\w+) egg:(?P<egg>\d+)')]

...
```

If you need complex structures - convert them manually using the `factory` parameter

```python
# OK
from dataclasses import dataclass
from typing import Annotated

from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatchDict

@dataclass
class MyStruct:
    spam: str
    egg: int

    
class Schema(BaseSchema):
    foo: Annotated[MyStruct, ReMatchDict(r'spam:(?P<spam>\w+) egg:(?P<egg>\d+)',
                                         factory=lambda dct: MyStruct(**dct))]

...
```

## factory
change type-casting to this enchant function param. if this param None, try type-casting

```python
from typing import Annotated
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch


class Schema(BaseSchema):
    # convert 'hello' to 'hello' with usage type-casting
    hello = Annotated[list[str], ReMatch(r'(hello)')]
    

print(Schema('hello world ').dict())  # {'hello': 'hello'} incorrect output type
```

with factory:

```python
from typing import Annotated
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch


class Schema(BaseSchema):
    # convert 'hello' to ['h', 'e', 'l', 'l', 'o'], without usage type-casting
    hello = Annotated[list[str], ReMatch(r'(hello)', factory=list)]
    
    
print(Schema('hello world').dict())  # {'hello': ['h', 'e', 'l', 'l', 'o']} OK
```
