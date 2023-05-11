from typing import Any, Callable, Optional, TypedDict


class FieldHook(TypedDict, total=False):
    """Typed dict kwargs for fields classes"""

    default: Optional[Any]
    callback: Optional[Callable[..., Any]]
    factory: Optional[Callable[..., Any]]


class FieldHookList(FieldHook, total=False):
    """typed dict kwargs for iterable fields (+ filter_ argument)"""

    filter_: Optional[Callable[..., bool]]
