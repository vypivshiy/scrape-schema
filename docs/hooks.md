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
