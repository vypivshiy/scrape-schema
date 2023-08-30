"""typing compat module"""
import sys
from typing import Type

NoneType: Type = type(None)


if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

if sys.version_info >= (3, 10):
    from typing import TypeAlias, get_args, get_origin, get_type_hints
else:
    from typing_extensions import TypeAlias, get_args, get_origin, get_type_hints

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

__all__ = [
    "NoneType",
    "Annotated",
    "TypeAlias",
    "get_args",
    "get_origin",
    "get_type_hints",
    "Self",
]
