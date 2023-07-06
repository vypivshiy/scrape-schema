# Scrape-schema

This library is designed to write structured, readable, 
reusable parsers for html, raw text and is inspired by dataclasses

# Motivation
Simplifying parsers support, where it is difficult to use 
or the complete absence of the **API interfaces** and decrease lines of code

Also structuring, data serialization and use as an intermediate layer 
for third-party serialization libraries: json, dataclasses, pydantic, etc

_____
# Features
- [Parsel](https://github.com/scrapy/parsel) backend.
- [Fluent interface](https://en.wikipedia.org/wiki/Fluent_interface#Python) simulate original parsel.Selector API for easy to use. 
- Python 3.8+ support
- Dataclass-like structure
- Partial support auto type-casting from annotations (str, int, float, bool, list, dict, Optional)
- logging to quickly find problems in extracted values
____

# Install

```shell
pip install scrape-schema
```

# Example
```python
from scrape_schema2 import BaseSchema, Parsel, Sc


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