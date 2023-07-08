from re import RegexFlag
from typing import Any, Callable, Hashable, KeysView, Pattern, Protocol, Union

from parsel import Selector

from scrape_schema._typing import Self

Selector().attrib.keys()


class SpecialMethodsProtocol(Protocol):
    def sc_parse(self, markup: Any) -> Any:
        pass

    def fn(self, function: Callable[..., Any]) -> Self:
        pass

    def concat_l(self, left_string: str) -> Self:
        pass

    def concat_r(self, right_string: str) -> Self:
        pass

    def sc_replace(self, old: str, new: str, count: int = -1) -> Self:
        pass

    def re_search(
        self,
        pattern: Union[str, Pattern[str]],
        flags: Union[int, RegexFlag] = 0,
        groupdict: bool = False,
    ) -> Self:
        pass

    def re_findall(
        self,
        pattern: Union[str, Pattern[str]],
        flags: Union[int, RegexFlag] = 0,
        groupdict: bool = False,
    ):
        pass

    def __getitem__(self, item) -> Self:
        pass


class AttribProtocol(SpecialMethodsProtocol):
    def get(self, *, key: Hashable) -> Any:
        pass

    def keys(self) -> Any:
        pass

    def values(self) -> Any:
        pass

    def items(self) -> Any:
        pass
