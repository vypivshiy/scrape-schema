[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Documentation Status](https://readthedocs.org/projects/scrape-schema/badge/?version=latest)](https://scrape-schema.readthedocs.io/en/latest/?badge=latest)
![CI](https://github.com/vypivshiy/scrape_schema/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/github/license/vypivshiy/scrape-schema)
![Version](https://img.shields.io/pypi/v/scrape-schema)
![Python-versions](https://img.shields.io/pypi/pyversions/scrape_schema)
[![codecov](https://codecov.io/gh/vypivshiy/scrape-schema/branch/master/graph/badge.svg?token=jqSNuE7g5l)](https://codecov.io/gh/vypivshiy/scrape-schema)

# Scrape-schema
This library is designed to write structured, readable,
reusable parsers for html, raw text and is inspired by dataclasses and ORM libraries

!!! warning

    Scrape-schema is currently in Pre-Alpha. Please expect breaking changes.

## Motivation
Simplifying parsers support, where it is difficult to use
or the complete absence of the **API interfaces** and decrease boilerplate code

Also structuring, data serialization and use as an intermediate layer
for third-party serialization libraries: json, dataclasses, pydantic, etc

_____
## Features
- Built top on [Parsel](https://github.com/scrapy/parsel)
- re, css, xpath, jmespath, [chompjs](https://github.com/Nykakin/chompjs) features
- [Fluent interface](https://en.wikipedia.org/wiki/Fluent_interface#Python) simular original parsel.Selector API for easy to use.
- decrease boilerplate code
- Does not depend on the http client implementation, use any!
- Python 3.8+ support
- Reusability, code consistency
- Dataclass-like structure
- Partial support auto type-casting from annotations (str, int, float, bool, list, dict, Optional)
- Detailed logging process to make it easier to write a parser
____

## Install

```shell
pip install scrape-schema
```
## Example

The fields interface is similar to the original [parsel](https://parsel.readthedocs.io/en/latest/)

```
# Example from parsel documentation
>>> from parsel import Selector
>>> text = """
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
>>> selector = Selector(text=text)
>>> selector.css('h1::text').get()
'Hello, Parsel!'
>>> selector.xpath('//h1/text()').re(r'\w+')
['Hello', 'Parsel']
>>> for li in selector.css('ul > li'):
...     print(li.xpath('.//@href').get())
http://example.com
http://scrapy.org
>>> selector.css('script::text').jmespath("a").get()
'b'
>>> selector.css('script::text').jmespath("a").getall()
['b', 'c']
```

```python
from scrape_schema import BaseSchema, Parsel, Sc


class Schema(BaseSchema):
    h1: Sc[str, Parsel().css('h1::text').get()]
    words: Sc[list[str], Parsel().xpath('//h1/text()').re(r'\w+')]
    urls: Sc[list[str], Parsel().css('ul > li').xpath('.//@href').getall()]
    sample_jmespath_1: Sc[str, Parsel().css('script::text').jmespath("a").get()]
    sample_jmespath_2: Sc[list[str], Parsel().css('script::text').jmespath("a").getall()]


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

See more [examples](examples) and [documentation](https://scrape-schema.readthedocs.io/en/latest/)
for get more information/examples
____
This project is licensed under the terms of the MIT license.
