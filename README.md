[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Documentation Status](https://readthedocs.org/projects/scrape-schema/badge/?version=latest)](https://scrape-schema.readthedocs.io/en/latest/?badge=latest)
![CI](https://github.com/vypivshiy/scrape_schema/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/github/license/vypivshiy/scrape-schema)
![Version](https://img.shields.io/pypi/v/scrape-schema)
![Python-versions](https://img.shields.io/pypi/pyversions/scrape_schema)
[![codecov](https://codecov.io/gh/vypivshiy/scrape-schema/branch/master/graph/badge.svg?token=jqSNuE7g5l)](https://codecov.io/gh/vypivshiy/scrape-schema)

**UNMAINTAINED, currently contunue experiments in [selector_schema_codegen](https://github.com/vypivshiy/selector_schema_codegen)**

# Scrape-schema
This library is designed to write structured, readable and
reusable parsers for html, raw text and is inspired by dataclasses and ORM libraries

> 🚨 Scrape-schema is currently in Pre-Alpha. Please expect breaking changes.


## Motivation
Simplifying parsers support, where it is difficult to use
or the complete absence of the API interfaces, decrease boilerplate code and
easy separate extraction logic from the crawling

Structuring, data serialization and use as an intermediate layer
for third-party serialization libraries: pydantic, json, dataclasses, attrs, etc

_____
## Features
- Built top on [Parsel](https://github.com/scrapy/parsel).
- re, css, xpath, jmespath, [chompjs](https://github.com/Nykakin/chompjs) features.
- [Fluent interface](https://en.wikipedia.org/wiki/Fluent_interface#Python) simular parsel.Selector API for easy to use.
- Decrease boilerplate code.
- Does not depend on the http client implementation, use any!
- Python 3.8+ support.
- Reusability, code consistency.
- Dataclass-like structure.
- Partial support auto type-casting from annotations (str, int, float, bool, list, dict, Optional)
- Detailed logging process to make it easier to write a parser
____

## Install

```shell
pip install scrape-schema
```
## Example

The fields interface is similar to the original [parsel](https://parsel.readthedocs.io/en/latest/) library

```python
# Example from parsel documentation
from parsel import Selector
text = """
        <html>
            <body>
                <h1>Hello, Parsel!</h1>
                <ul>
                    <li><a href="http://example.com">Link 1</a></li>
                    <li><a href="http://scrapy.org">Link 2</a></li>
                </ul>
                <script type="application/json">{"a": ["b", "c"]}</script>
            </body>
        </html>"""

def schema(txt: str):
    selector = Selector(text=txt)
    return {
        "h1": selector.css('h1::text').get(),
        "words": selector.xpath('//h1/text()').re(r'\w+'),
        "urls": selector.css('ul > li').xpath('.//@href').getall(),
        "sample_jmespath_1": selector.css('script::text').jmespath("a").get(),
        "sample_jmespath_2": selector.css('script::text').jmespath("a").getall()
    }

print(schema(text))
# {'h1': 'Hello, Parsel!',
# 'words': ['Hello', 'Parsel'],
# 'urls': ['http://example.com', 'http://scrapy.org'],
# 'sample_jmespath_1': 'b',
# 'sample_jmespath_2': ['b', 'c']}
```

```python
from scrape_schema import BaseSchema, Parsel


class Schema(BaseSchema):
    h1: str = Parsel().css('h1::text').get()
    words: list[str] = Parsel().xpath('//h1/text()').re(r'\w+')
    urls: list[str] = Parsel().css('ul > li').xpath('.//@href').getall()
    sample_jmespath_1: str = Parsel().css('script::text').jmespath("a").get()
    sample_jmespath_2: list[str] = Parsel().css('script::text').jmespath("a").getall()


text = """
        <html>
            <body>
                <h1>Hello, Parsel!</h1>
                <ul>
                    <li><a href="http://example.com">Link 1</a></li>
                    <li><a href="http://scrapy.org">Link 2</a></li>
                </ul>
                <script type="application/json">{"a": ["b", "c"]}</script>
            </body>
        </html>"""

print(Schema(text).dict())
# {'h1': 'Hello, Parsel!',
# 'words': ['Hello', 'Parsel'],
# 'urls': ['http://example.com', 'http://scrapy.org'],
# 'sample_jmespath_1': 'b',
# 'sample_jmespath_2': ['b', 'c']}
```

The scrape_schema example output looks like the previous one, why do you need this library?

- Easy to modify
- Easy add additional methods
- Easy to port to another project without having to deal with the logic and call stack
- IDE typing support

For example, if you need to modify a parser, with `scrape_schema` it is easy and simple to do!

```python
from uuid import uuid4
from datetime import datetime

from scrape_schema import BaseSchema, Parsel, sc_param, Callback
from scrape_schema.validator import markup_pre_validator


class Schema(BaseSchema):
    # invoke simple functions to fields output
    # add uuid4 id
    id: str = Callback(lambda: str(uuid4()))
    # add parse date
    date: str = Callback(lambda: str(datetime.today()))

    h1: str = Parsel().css('h1::text').get()
    # convert to upper case
    h1_upper: str = Parsel().css('h1::text').get().upper()
    # convert to lower case
    h1_lower: str = Parsel().css('h1::text').get().lower()

    words: list[str] = Parsel().xpath('//h1/text()').re(r'\w+')
    # alt solution split words
    words_2: list[str] = Parsel().xpath('//h1/text()').get().split()
    # join result by ' - ' string
    words_join: str = Parsel().xpath('//h1/text()').re(r'\w+').join(" AND ")
    urls: list[str] = Parsel().css('ul > li').xpath('.//@href').getall()
    # replace http protocol to https
    urls_https: list[str] = Parsel().css('ul > li').xpath('.//@href').getall().replace("http://", "https://")
    # you can modify output keys
    sample_jmespath_1: str = Parsel(alias="jsn1").css('script::text').jmespath("a").get()
    sample_jmespath_2: list[str] = Parsel(alias="class").css('script::text').jmespath("a").getall()

    # or calc json count values
    jsn_len: int = Parsel(auto_type=False).css('script::text').jmespath("a").getall().count()

    # pre validation markup input before parse text.
    # if text from first h1 element != 'Hello, Parsel!' - throw `SchemaPreValidationError` exception
    @markup_pre_validator()
    def validate_markup(self) -> bool:
        return self.__selector__.css('h1::text').get() == 'Hello, Parsel!'

    # or create fields with custom rule
    @sc_param
    def custom(self) -> str:
        return "hello world!"

    # you can add extra methods!
    def parse_urls(self):
        for url in self.urls:
            print(f"parse {url}")


text = """
        <html>
            <body>
                <h1>Hello, Parsel!</h1>
                <ul>
                    <li><a href="http://example.com">Link 1</a></li>
                    <li><a href="http://scrapy.org">Link 2</a></li>
                </ul>
                <script type="application/json">{"a": ["b", "c"]}</script>
            </body>
        </html>"""

schema = Schema(text)
# invoke custom method
schema.parse_urls()
# parse http://example.com
# parse http://scrapy.org

print(schema.dict())

# !!!field from @sc_param decorator
#   vvvvvvvvvvvvvvvvvvvvvv
# {'custom': 'hello world!',
#  !!!simple functions callbacks output
#  vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
# 'id': '6b66de7b-5b5f-445a-b8a7-3b17332c1ff5',
# 'date': '2023-09-29 18:47:03.638941',
# 'h1': 'Hello, Parsel!', 'h1_upper': 'HELLO, PARSEL!', 'h1_lower': 'hello, parsel!',
# 'words': ['Hello', 'Parsel'], 'words_2': ['Hello,', 'Parsel!'],
# 'words_join': 'Hello AND Parsel',
# 'urls': ['http://example.com', 'http://scrapy.org'],
# 'urls_https': ['https://example.com', 'https://scrapy.org'],
#         !!!changed key alias 'sample_jmespath_2' TO 'class'!!!
#               vvvvvvvvvvvvvvvvv
# 'jsn1': 'b', 'class': ['b', 'c'], 'jsn_len': 2}

```

See more [examples](examples) and [documentation](https://scrape-schema.readthedocs.io/en/latest/)
for get more information/examples
____
This project is licensed under the terms of the MIT license.
