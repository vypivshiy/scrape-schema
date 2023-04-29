[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Documentation Status](https://readthedocs.org/projects/scrape-schema/badge/?version=latest)](https://scrape-schema.readthedocs.io/en/latest/?badge=latest)
![CI](https://github.com/vypivshiy/scrape_schema/actions/workflows/ci.yml/badge.svg)
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
* python 3.8+ support
* decrease lines of code for your parsers
* partial support type-casting from annotations (str, int, float, bool, list, dict, Optional)
* interacting with values with callbacks, filters, factories
* logging to quickly find problems in extracted values
* optional success-attempts parse values checker from fields objects
* standardization, modularity* of structures-parsers
*If you usage schema-structures and they are separated from the logic of getting the text
(stdout output, HTTP requests, etc)
____
# Build-in libraries parsers support:
- [x] re
- [x] bs4
- [x] selectolax(Modest)
- [ ] parsel
- [ ] lxml
- [ ] selenium
- [ ] playwright
____
# Install

zero dependencies: regex, nested fields (and typing_extension if python < 3.11)
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
# Code comparison
Before scrape_schema: harder to maintain, change logic
```python
import re
import pprint

TEXT = """
banana potato BANANA POTATO
-foo:10
-bar:20
lorem upsum dolor
192.168.0.1
"""


def parse_text(text: str) -> dict:
    if match := re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", text):
        ipv4 = match[1]
    else:
        ipv4 = None

    if matches := re.findall(r"(\d+)", text):
        max_digit = max(int(i) for i in matches)
    else:
        max_digit = None

    failed_value = bool(re.search(r"(ora)", text))

    if matches := re.findall(r"(\d+)", text):
        digits = [int(i) for i in matches]
        digits_float = [float(f'{i}.5') for i in matches]
    else:
        digits = None
        digits_float = None
    words_lower = matches if (matches := re.findall(r"([a-z]+)", text)) else None
    words_upper = matches if (matches := re.findall(r"([A-Z]+)", text)) else None

    return dict(ipv4=ipv4, max_digit=max_digit, failed_value=failed_value,
                digits=digits, digits_float=digits_float, 
                words_lower=words_lower, words_upper=words_upper)
    

if __name__ == '__main__':
    pprint.pprint(parse_text(TEXT), width=48, compact=True)
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
After scrape_schema: easy change of logic, support, portability
```python
from typing import List  # if you usage python3.8 - usage GenericAliases
import pprint

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchList

TEXT = """
banana potato BANANA POTATO
-foo:10
-bar:20
lorem upsum dolor
192.168.0.1
"""


class Schema(BaseSchema):
    ipv4: ScField[str, ReMatch(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")]
    max_digit: ScField[int, ReMatchList(r"(\d+)",
                                          callback=int,                                      
                                          factory=max)]
    failed_value: ScField[bool, ReMatchList(r"(ora)", default=False)]
    digits: ScField[List[int], ReMatchList(r"(\d+)")]
    digits_float: ScField[List[float], ReMatchList(r"(\d+)", 
                                                     callback=lambda s: f"{s}.5")]
    words_lower: ScField[List[str], ReMatchList(r"([a-z]+)")]
    words_upper: ScField[List[str], ReMatchList(r"([A-Z]+)")]
    
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
logger.setLevel(logging.INFO)
...
```

See more [examples](examples) and [documentation](https://scrape-schema.readthedocs.io/en/latest/) 
for get more information/examples
____
This project is licensed under the terms of the MIT license.
