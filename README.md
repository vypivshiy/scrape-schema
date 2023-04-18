[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Documentation Status](https://readthedocs.org/projects/scrape-schema/badge/?version=latest)](https://scrape-schema.readthedocs.io/en/latest/?badge=latest)
# Scrape-schema
This library is designed to write structured, readable, 
reusable parsers for unstructured text data (like html, stdout or any text) and
is inspired by dataclasses

# Motivation
Simplifying parsers support, where it is difficult to use 
or the complete absence of the **API interfaces** and decrease lines of code

Also structuring, data serialization and use as an intermediate layer 
for third-party serialization libraries: json, dataclasses, pydantic, etc

_____
# Features
* Partial support type-casting from annotations (str, int, float, bool, list, dict)
* Optional success-attempts parse values checker
* Factory functions for convert values
* Filter functions for filter a founded values
* Optional checking the success of getting the value from the field
____
# Build-in backends parsers support:
* re
* bs4
* selectolax(Modest)
* parsel (TODO)
____
# Install

zero dependencies (regex, nested fields)
```shell
pip install scrape-schema
```
add bs4 fields
```shell
pip install scrape-schema[bs4]
```

add selectolax fields
```shell
pip install scrape-schema[selectolax]
```
add all fields
```shell
pip install scrape-schema[all]
```
____
# Example
```python
from typing import Annotated
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
    ipv4: Annotated[str, ReMatch(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")]
    max_digit: Annotated[int, ReMatchList(r"(\d+)",
                                          callback=int,                                      
                                          factory=max)]
    failed_value: Annotated[bool, ReMatchList(r"(ora)", default=False)]
    digits: Annotated[list[int], ReMatchList(r"(\d+)")]
    digits_float: Annotated[list[float], ReMatchList(r"(\d+)", 
                                                     callback=lambda s: f"{s}.5")]
    words_lower: Annotated[list[str], ReMatchList(r"([a-z]+)")]
    words_upper: Annotated[list[str], ReMatchList(r"([A-Z]+)")]
    
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
In this project, logging to the `DEBUG` level is enabled by default. 

To set up logger, you can get it by the name `"scrape_schema"`
```python
import logging

logger = logging.getLogger("scrape_schema")
logger.setLevel(logging.WARNING)
...
```

See more [examples](examples) and [documentation](https://scrape-schema.readthedocs.io/en/latest/) 
for get more information/examples
____
This project is licensed under the terms of the MIT license.
