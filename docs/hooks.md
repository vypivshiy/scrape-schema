# scrape_schema.hooks
This module contains hooks and structures for reusing callback functions in Fields

# FieldHook, FieldHookList
TypedDict structures that store values for fields classes
## FieldHook
### Attributes:
- `default: Optional[Any]` default attribute
- `callback: Optional[Callable[..., Any]]` callback attribute
- `factory: Optional[Callable[..., Any]]` factory attribute

### Usage
```python
from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchList
from scrape_schema.hooks import FieldHook


hook_lower_case = FieldHook(default="no lower case")
hook_int_x2 = FieldHook(default=1, callback=lambda s: int(s)*2, factory=int)
hook_float = FieldHook(default=0, callback=float, factory=lambda d: d+0.3)


class HookSchema(BaseSchema):
    word_lower: ScField[str, ReMatch(r"([a-z]+)", **hook_lower_case)]
    digit_x2: ScField[int, ReMatch(r"(\d+)", **hook_int_x2)]
    digit_float_03: ScField[float, ReMatch(r"(\d+)", **hook_float)]

print(HookSchema("LOWER CASE? 5 11 17 23"))
# HookSchema(word_lower:str='no lower case', digit_x2:int=10, digit_float_03:float=5.3)
print(HookSchema("okay)"))
# HookSchema(word_lower:str='okay', digit_x2:int=2, digit_float_03:float=0.3)

# without schema
print(ReMatch(r"([a-z]+)", **hook_lower_case).extract("BOOO"))
# no lower case
print(ReMatch(r"([a-z]+)", **hook_lower_case).extract("dolor"))
# dolor
print(ReMatch(r"(\d+)", **hook_int_x2).extract("a"))
# 2
print(ReMatch(r"(\d+)", **hook_int_x2).extract("10"))
# 20
```

## FieldHookList
TypedDict structures that store values for collection fields values
- `default: Optional[Any]` default attribute
- `callback: Optional[Callable[..., Any]]` callback attribute
- `factory: Optional[Callable[..., Any]]` factory attribute
- `filter_: Optional[Callable[..., bool]]` filter_ attribute

### Usage
```python
from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatchList
from scrape_schema.hooks import FieldHookList

hook_float = FieldHookList(default=[0], callback=float, factory=lambda lst: [i + .3 for i in lst])
hook_filter_ge_10 = FieldHookList(default=[11], filter_=lambda v: int(v) > 10)


class HookSchema(BaseSchema):
    digit_float_03: ScField[list[float], ReMatchList(r"(\d+)", **hook_float)]
    digits_ge_10: ScField[list[int], ReMatchList(r"(\d+)", **hook_filter_ge_10)]

print(HookSchema("LOWER CASE? 5 11 17 23"))
# HookSchema(digit_float_03:list=[5.3, 11.3, 17.3, 23.3], digits_ge_10:list=[11, 17, 23])
print(HookSchema("okay)"))
# HookSchema(digit_float_03:list=[0.3], digits_ge_10:list=[11])

print(ReMatchList(r"(\d+)", **hook_filter_ge_10).extract("1 4 9"))
# []
print(ReMatchList(r"(\d+)", **hook_filter_ge_10).extract("aaaa"))
# [11]
print(ReMatchList(r"(\d+)", **hook_float).extract("1"))
# [1.3]
print(ReMatchList(r"(\d+)", **hook_filter_ge_10).extract("31", type_=list[int]))
# [31]
```

# FieldHooksStorage
Singleton class storage. 
Sets the default field attributes globally. By default, callback functions take precedence over
named arguments. if you need argument precedence, set `hooks_priority=False` in the `class Config`.

```python
from scrape_schema import BaseSchemaConfig

class Config(BaseSchemaConfig):
    hooks_priority = False # disable hooks priority
```

## decorator hooks syntax:
```
hooks = HooksStorage()

@hooks.on_<action>("<SchemaName>.<attribute_1>",
                    "<SchemaName>.<attribute_2>",
                    ...
                    "<SchemaName>.<attribute_n>")
def something_action(value):
    ...
```
## Methods
- `on_filter(*attrs_names: str)` decorate `filter_` attribute for attr names in schemas

```python
from typing import List

import bs4

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.hooks import HooksStorage
from scrape_schema.fields.soup import SoupFindList
from scrape_schema.callbacks.soup import get_attr

hooks = HooksStorage()


@hooks.on_filter("Schema1.hrefs", "Schema1.urls",
                 "Schema2.hrefs", "Schema2.urls")
def _is_example_netloc(tag: bs4.Tag):
    return tag.get("href").startswith("example.com")


class Schema1(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {bs4.BeautifulSoup: {"features": "html.parser"}}
        hooks_priority = False

    # hooks_priority = False, usage `filter_` keyword argument and ` ignore _is_example_netloc` hook
    urls: ScField[List[str], SoupFindList("<a>", filter_=lambda _: True, callback=get_attr("href"))]
    hrefs: ScField[List[str], SoupFindList("<a>", callback=get_attr("href"))]


class Schema2(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {bs4.BeautifulSoup: {"features": "html.parser"}}

    # hooks_priority = True, usage `_is_example_netloc` and ignore filter_ keyword argument
    urls: ScField[List[str], SoupFindList("<a>", filter_=lambda _: True, callback=get_attr("href"))]
    hrefs: ScField[List[str], SoupFindList("<a>", callback=get_attr("href"))]
    # out of scope in on_filter hook - get all urls
    urls_: ScField[List[str], SoupFindList("<a>", callback=get_attr("href"))]


HTML = '<a href="example.com/1"></a>\n<a href="evil.site"></a>\n<a href="example.com/2"></a>'

print(Schema1(HTML))
# `lambda _: True` accept all values and ignore `on_filter` hook
#                                        vvvvv
# Schema1(urls:list=['example.com/1', 'evil.site', 'example.com/2'], hrefs:list=['example.com/1', 'example.com/2'])
print(Schema2(HTML))
# Schema2(urls:list=['example.com/1', 'example.com/2'],
# hrefs:list=['example.com/1', 'example.com/2'],
# urls_:list=['example.com/1', 'evil.site', 'example.com/2'])
```

- `on_callback(*attrs_names: str)` - decorate `callback` attribute for attr names in schemas.

```python
from scrape_schema import ScField, BaseSchema
from scrape_schema.hooks import HooksStorage
from scrape_schema.fields.regex import ReMatch

hooks = HooksStorage()

@hooks.on_callback("Schema.word")
def _upper(val: str) -> str:
    return val.upper()

class Schema(BaseSchema):
    word: ScField[str, ReMatch(r"([a-z]+)")]
print(Schema("dolor"))
# Schema(word:str='DOLOR')
```
- `on_factory(*attrs_names: str)` - decorate `factory` attribute for attr names in schemas.
```python
from scrape_schema import ScField, BaseSchema
from scrape_schema.hooks import HooksStorage
from scrape_schema.fields.regex import ReMatch

hooks = HooksStorage()

@hooks.on_factory("Schema.word")
def _to_reverse(val: str) -> str:
    return val[::-1]

class Schema(BaseSchema):
    word: ScField[str, ReMatch(r"([a-z]+)")]
print(Schema("dolor"))
# Schema(word:str='rolod')
```
- `get_callback(self, name: str)` - get callback by attr name. if not founded - return None
- `get_filter(self, name: str)` - get filter by attr name. if not founded - return None
- `get_factory(self, name: str)` - get factory by attr name. if not founded - return None
```python
from scrape_schema import ScField, BaseSchema
from scrape_schema.hooks import HooksStorage
from scrape_schema.fields.regex import ReMatch

hooks = HooksStorage()

@hooks.on_callback("Schema.word")
def _upper(val: str) -> str:
    return val.upper()

@hooks.on_filter("Schema.words")
def _filter(val: str) -> bool:
    return len(val) > 5

@hooks.on_factory("Schema.word")
def _reverse(val: str) -> str:
    return val[::-1]

hooks.get_callback("Schema.word")  # <function _upper at ...>
hooks.get_callback("Schema.spam")  # None
hooks.get_filter("Schema.words")  # <function _filter at ...>
hooks.get_filter("Schema.eggs")  # None
hooks.get_factory("Schema.word")  # <function _reverse at ...>
hooks.get_factory("Schema.words")  # None

```
- `add_hook(name: str, hook: FieldHook | FieldHookList)` - storage `FieldHook or FieldHookList` by name
- `add_kwargs_hook(name: str, default: Optional[Any] = None, callback: Optional[Callable] = None,
filter_: Optional[Callable] = None, factory: Optional[Callable] = None)` - create and storage hook by keywords arguments
- `get_hook(name: str)` - get hook by name. if not founded - return empty dict
- `hook_keys()` - get all stored hook keys
### Examples:
```python
from scrape_schema.hooks import HooksStorage, FieldHook, FieldHookList
from scrape_schema.fields.regex import ReMatch, ReMatchList

hooks = HooksStorage()
hooks.add_hook("default_any", FieldHook(default="Any"))
hooks.add_hook("is_digit", FieldHookList(filter_=lambda s: str(s).isdigit()))

hooks.get_hook("to_list")
# {'default': 'kwargs', 'callback': None, 'factory': <class 'list'>}
hooks.get_hook("magic_hook")
# {}
hooks.add_kwargs_hook("to_list", default="kwargs", factory=list)
# hooks.hook_keys()
# dict_keys(['default_any', 'is_digit', 'to_list'])

# usage:
print(ReMatch(r"([a-z]+)", **hooks.get_hook("default_any")).extract("100500"))
# "Any"
print(ReMatch(r"([a-z]+)", **hooks.get_hook("to_list")).extract("word"))
# ['w', 'o', 'r', 'd']

print(ReMatchList(r"(\w+)", **hooks.get_hook("is_digit")).extract("logs messages count: 10 error: over 9000"))
# ['10', '9000']
```
