# Base Schema
The base class of field processing.

# How it works
1. accept any string text to constructor
2. get fields from the attributes
3. if field needed a *Parser* class (bs4, selectolax, ...), it 
get config from \_\_MARKUP_PARSERS\_\_ dict. If class not founded - raise exception 
4. field parse, and return value
5. set parsed value to the constructor

## Attributes:
 - \_\_MARKUP_PARSERS\_\_: dict[Type, dict[str, Any]] - dict of a markup parsers classes. 
Default empty dict
 
attribute structure: {Type (not initialized class) parser : - value - dict of kwargs params

Example: 
```python
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema

class Schema(BaseSchema):
    __MARKUP_PARSERS__ = {BeautifulSoup: {"features": "html.parser"}}
    ...
```
- \_\_AUTO_TYPING\_\_: bool - usage typing from annotations. Default True.
if set False - disable this feature

- \_\_VALIDATE\_\_: bool - usage validator rules in fields. Default False

- \_\_MAX_FAILS_COUNTER\_\_: int - Limit of unsuccessfully parsed fields (checks against the default value) . Default -1

>>> If the value is negative - this feature is disabled. (default)
> 
>>> If it is 0 - at the first fail it raise exception
> 
>>>If equal to 1 - with two fails it raise exception
> 
>>>If equal to N - at N errors it raise exception

Example:

```python
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch, ReMatchList
TEXT = "1 2 3"

class SchemaOne(BaseSchema):
    digits: list[int] = ReMatchList(r'(\d+)')
    word: str = ReMatch(r'([a-z]+)')  # never founded


class SchemaTwo(BaseSchema):
    __MAX_FAILS_COUNTER__ = 1
    digits: list[int] = ReMatchList(r'(\d+)')
    word: str = ReMatch(r'([a-z]+)')  # never founded
    

class SchemaThree(BaseSchema):
    __MAX_FAILS_COUNTER__ = 0
    digits: list[int] = ReMatchList(r'(\d+)')
    word: str = ReMatch(r'([a-z]+)')  # never founded

if __name__ == '__main__':
    schema_1 = SchemaOne(TEXT)  # nothing
    schema_2 = SchemaTwo(TEXT)  # print warning
    schema_3 = SchemaThree(TEXT)  # raise ParseFailAttemptsError
```
