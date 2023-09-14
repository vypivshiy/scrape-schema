# typing.Annotated
This project usage Annotated [(PEP 593)](https://docs.python.org/3/library/typing.html#typing.Annotated)
typehint for annotation fields in runtime and make the static type checker happy 😀
and didn't need write a mypy plugin 🤯.

This project have `Annotated` shortcut `Sc`

```python
from typing import Annotated
# for python 3.8
# from typing_extensions import Annotated
# or import Annotated alias
from scrape_schema import Sc

assert Annotated == Sc  # OK
```

# Annotating in attribute-style

There is a way to create a schema using normal field assignment.
But for now there is no mypy plugin to throw an exception and mypy will throw
error with code `assigment`.

!!! warning
    There is currently no plugin for [mypy](https://mypy.readthedocs.io/en/stable/) and this method
    will give an `assignment` error.

    if you have mypy in your project, turn off checking for this type of error by
    `# mypy: disable-error-code="assignment"` expression

```python
# mypy: disable-error-code="assignment"
from scrape_schema import BaseSchema, Text


class Schema(BaseSchema):
    digit: int = Text().re_search(r"\d+")[0]
    word: str = Text().re_search(r"[a-zA-Z]+")[0]


Schema("test 100").dict()
# {"digit": 100, "word": "test"}
```

## Type caster
If a field in the `BaseSchema` class is successfully processed and the `auto_type=False`
argument **is not passed** to `Field`, then it is **guaranteed** to convert to the following types:

- int
- float
- str
- bool
- dict
- list
- Optional
- for `Nested` fields - BaseSchema, List\[BaseSchema\], list\[BaseSchema\]
