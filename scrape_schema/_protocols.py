"""This module contains Protocol annotations for help type hint
Fluent interface better
"""
from re import RegexFlag
from typing import Any, Callable, Hashable, Optional, Pattern, Protocol, Union

from scrape_schema._typing import Self


class SpecialMethodsProtocol(Protocol):
    """Special methods protocol typing"""

    def sc_parse(self, markup: Any) -> Any:
        pass  # pragma: no cover

    def fn(self, function: Callable[..., Any]) -> Self:
        pass  # pragma: no cover

    def concat_l(self, left_string: str) -> Self:
        pass  # pragma: no cover

    def concat_r(self, right_string: str) -> Self:
        pass  # pragma: no cover

    def sc_replace(self, old: str, new: str, count: int = -1) -> Self:
        pass  # pragma: no cover

    def replace(self, old: str, new: str, count: int = -1) -> Self:
        pass  # pragma: no cover

    def re_search(
        self,
        pattern: Union[str, Pattern[str]],
        flags: Union[int, RegexFlag] = 0,
        groupdict: bool = False,
    ) -> Self:
        pass  # pragma: no cover

    def re_findall(
        self,
        pattern: Union[str, Pattern[str]],
        flags: Union[int, RegexFlag] = 0,
        groupdict: bool = False,
    ) -> Self:
        pass  # pragma: no cover

    def chomp_js_parse(
        self, unicode_escape: Any = False, json_params: Any = None
    ) -> Self:
        pass  # pragma: no cover

    def chomp_js_parse_all(
        self,
        unicode_escape: Any = False,
        omitempty: Any = False,
        json_params: Any = None,
    ) -> Self:
        pass  # pragma: no cover

    def strip(self, chars: Optional[str] = None) -> Self:
        pass  # pragma: no cover

    def rstrip(self, chars: Optional[str] = None) -> Self:
        pass  # pragma: no cover

    def lstrip(self, chars: Optional[str] = None) -> Self:
        pass  # pragma: no cover

    def lower(self) -> Self:
        pass  # pragma: no cover

    def upper(self) -> Self:
        pass  # pragma: no cover

    def capitalize(self) -> Self:
        pass  # pragma: no cover

    def split(self, sep: Optional[str] = None, max_split: int = -1) -> Self:
        pass  # pragma: no cover

    def join(self, join_sep: str) -> Self:
        pass  # pragma: no cover

    def count(self) -> Self:
        pass  # pragma: no cover

    def __getitem__(self, item) -> Self:
        pass  # pragma: no cover


class AttribProtocol(SpecialMethodsProtocol):
    """Parsel.Selector.attrib protocol"""

    def get(self, *, key: Hashable) -> Self:  # type: ignore
        pass  # pragma: no cover

    def keys(self) -> Self:  # type: ignore
        pass  # pragma: no cover

    def values(self) -> Self:  # type: ignore
        pass  # pragma: no cover

    def items(self) -> Self:  # type: ignore
        pass  # pragma: no cover
