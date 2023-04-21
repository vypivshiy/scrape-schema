"""This fields usage standard python `re` backend

References:


**Base**

* https://docs.python.org/3.11/library/re.html

* https://docs.python.org/3.11/library/re.html#regular-expression-syntax

* https://docs.python.org/3.11/library/re.html#flags

* https://docs.python.org/3.11/howto/regex.html#regex-howto

**ReMatch, ReMatchList**

* https://docs.python.org/3.11/library/re.html#re.search

* https://docs.python.org/3.11/library/re.html#re.Match.group

**ReMatchList, ReMatchListDict**

* https://docs.python.org/3.11/library/re.html#re.finditer

**ReMatchDict, ReMatchListDict**

* https://docs.python.org/3.11/library/re.html#re.Match.groupdict
"""
import re
from typing import Any, Callable, Optional, Pattern

from ..base import BaseField

__all__ = ["ReMatch", "ReMatchList", "ReMatchDict", "ReMatchListDict"]


class ReMatch(BaseField):
    def __init__(
        self,
        pattern: str | Pattern,
        group: int = 1,
        flags: int | re.RegexFlag = 0,
        *,
        default: Optional[Any] = None,
        callback: Optional[Callable[[str], Any]] = None,
        factory: Optional[Callable[[str | Any], Any]] = None,
    ):
        """get first match by `re.search`

        :param pattern: re.compile pattern or string
        :param group: match group. default 1
        :param flags: regex compile flags. default 0
        :param default: default value if match not founded. default None
        :param callback: function eval result. default None
        :param factory: function cast final result. If passed - ignore type-casting. Default None
        """
        super().__init__(default=default, callback=callback, factory=factory)
        self.pattern = (
            re.compile(pattern, flags) if isinstance(pattern, str) else pattern
        )
        self.group = group

    def _parse(self, markup: str) -> Optional[str]:
        if result := self.pattern.search(markup):
            return result.group(self.group)
        return None


class ReMatchList(BaseField):
    def __init__(
        self,
        pattern: str | Pattern,
        group: int = 1,
        flags: int | re.RegexFlag = 0,
        *,
        default: Optional[Any] = None,
        filter_: Optional[Callable[[str], bool]] = None,
        callback: Optional[Callable[[str], Any]] = None,
        factory: Optional[Callable[[list[str] | Any], Any]] = None,
    ):
        """get all matches by `re.finditer`

        :param pattern: re.compile pattern or string
        :param group: match group. default 1
        :param flags: regex compile flags. default 0
        :param default: default value if match not founded. default None
        :param filter_: function for filter result list. default None
        :param callback: function eval result. default None
        :param factory: function cast final result. If passed - ignore type-casting. Default None
        """
        super().__init__(
            default=default, filter_=filter_, callback=callback, factory=factory
        )
        self.pattern = (
            re.compile(pattern, flags) if isinstance(pattern, str) else pattern
        )
        self.group = group

    def _parse(self, markup: str) -> list[str]:
        if matches := self.pattern.finditer(markup):
            return [m.group(self.group) for m in matches]
        return []


class ReMatchDict(BaseField):
    def __init__(
        self,
        pattern: str | Pattern,
        flags: int | re.RegexFlag = 0,
        *,
        default: Optional[Any] = None,
        callback: Optional[Callable[[dict[str, str]], Any]] = None,
        factory: Optional[Callable[[dict[str, str] | Any], Any]] = None,
    ):
        """get first match by `re.search(...).groupdict()`. Pattern required named groups

        :param pattern: re.compile pattern or string. Pattern required named groups
        :param flags: regex compile flags. default 0
        :param default: default value if match not founded. default None
        :param callback: function eval result. default None
        :param factory: function final cast result. If passed - ignore type-casting. Default None
        """
        super().__init__(default=default, callback=callback, factory=factory)
        self.pattern = (
            re.compile(pattern, flags) if isinstance(pattern, str) else pattern
        )
        if not self.pattern.groupindex:
            raise AttributeError(f"{pattern.pattern} required named groups")  # type: ignore

    def _parse(self, markup: str) -> dict[str, str]:
        return result.groupdict() if (result := self.pattern.search(markup)) else {}


class ReMatchListDict(BaseField):
    def __init__(
        self,
        pattern: str | Pattern,
        flags: int | re.RegexFlag = 0,
        *,
        default: Optional[Any] = None,
        filter_: Optional[Callable[[dict[str, str]], bool]] = None,
        callback: Optional[Callable[[dict[str, str]], Any]] = None,
        factory: Optional[Callable[[dict[str, str] | Any], Any]] = None,
    ):
        """get all matches by `re.finditer` and `re.search(...).groupdict()`. Pattern required named groups

        :param pattern: re.compile pattern or string. Pattern required named groups
        :param flags: regex compile flags. default 0
        :param default: default value if match not founded. default None
        :param filter_: function for filter result list. default None
        :param callback: function eval result. default None
        :param factory: function cast final result. If passed - ignore type-casting. Default None
        """
        super().__init__(
            default=default, callback=callback, filter_=filter_, factory=factory
        )
        self.pattern = (
            re.compile(pattern, flags) if isinstance(pattern, str) else pattern
        )
        if not self.pattern.groupindex:
            raise AttributeError(f"{pattern.pattern} required named groups")  # type: ignore

    def _parse(self, markup: str) -> list[dict[str, str]]:
        if results := self.pattern.finditer(markup):
            return [result.groupdict() for result in results]
        return []
