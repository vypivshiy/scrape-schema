from re import RegexFlag
from typing import Any, Callable, Hashable, Pattern, Protocol, Union

from scrape_schema._typing import Self


class SpecialMethodsProtocol(Protocol):
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

    def __getitem__(self, item) -> Self:
        pass  # pragma: no cover


class AttribProtocol(SpecialMethodsProtocol):
    def get(self, *, key: Hashable) -> SpecialMethodsProtocol:  # type: ignore
        pass  # pragma: no cover

    def keys(self) -> SpecialMethodsProtocol:  # type: ignore
        pass  # pragma: no cover

    def values(self) -> SpecialMethodsProtocol:  # type: ignore
        pass  # pragma: no cover

    def items(self) -> SpecialMethodsProtocol:  # type: ignore
        pass  # pragma: no cover
