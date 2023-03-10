# Overview

Scrape Schema - a library for serialization of chaotic plain text data 
to python datatypes

# Why?
This project is an attempt to serialize chaos from 
unstructured text into readable, reusing structures.

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
# Logs
for enable/disable/config logger, get `scrape_schema` logger:

```python
import logging
logger = logging.getLogger("scrape_schema")
...
```
# Quickstart
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

