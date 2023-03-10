[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
# Scrape-schema
This library is designed to write structured, readable, 
reusable parsers for various text data (like html, stdout or any text) and
is inspired by **marshmallow** and various **ORM
libraries**
_____
# Features
* Simple type-casting from annotations (str, int, float, bool, list)
* Optional success-attempts parse values
* Factory functions to convert values
* Filter functions to filter for founded values
* Optional validation functions for fields
* Optional checking the success of getting the value from the field
____
# Build-in backends parsers support:
* re
* bs4
* selectolax(Modest)
____
# Install
## Nested + Regex fields (minimalism, zero dependencies)
```shell
pip install scrape-schema
```
## Add all fields
```shell
pip install scrape-schema[all]
```
## Add bs4 fields
```shell
pip install scrape-schema[bs4]
```
## Add selectolax fields
```shell
pip install scrape-schema[slax]
```
____
# Example
```python
import pprint
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch, ReMatchList

TEXT = """
banana potato BANANA POTATO
-foo:10
-bar:20
lorem upsum dolor
192.168.0.1
"""


class Schema(BaseSchema):
    status: str = "OK"
    ip_v4: str = ReMatch(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
    max_digit: int = ReMatchList(r"(\d+)", factory=lambda lst: max(int(i) for i in lst))

    failed_value: bool = ReMatchList(r"(ora)", default=False)
    digits: list[int] = ReMatchList(r"(\d+)")
    digits_float: list[float] = ReMatchList(r"(\d+)", callback=lambda s: f"{s}.5")
    words_lower: list[str] = ReMatchList(r"([a-z]+)")
    words_upper: list[str] = ReMatchList(r"([A-Z]+)")
    
if __name__ == '__main__':
    schema = Schema(TEXT)
    pprint.pprint(schema.dict(), width=48, compact=True)
    # {'digits': [10, 20, 192, 168, 0, 1],
    #  'digits_float': [10.5, 20.5, 192.5, 168.5, 0.5,
    #                   1.5],
    #  'failed_value': False,
    #  'ip_v4': '192.168.0.1',
    #  'max_digit': 192,
    #  'words_lower': ['banana', 'potato', 'foo',
    #                  'bar', 'lorem', 'upsum',
    #                  'dolor'],
    #  'words_upper': ['BANANA', 'POTATO']}
```
_____
# logging
You can logger configuration!
```python
import logging
logger = logging.getLogger("scrape_schema")
logger.setLevel(logging.INFO)
```

See more [examples](examples) and [documentation](docs) for get more information/examples
____
This project is licensed under the terms of the MIT license.
