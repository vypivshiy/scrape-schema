from typing import Any, Callable, Optional, Pattern

from ..base import BaseField
import re

__all__ = [
    'ReMatch',
    'ReMatchList',
    'ReMatchDict',
    'ReMatchListDict'
]

class ReMatch(BaseField):
    def __init__(self,
                 pattern: str | Pattern,
                 group: int = 1,
                 flags: int | re.RegexFlag = 0,
                 *,
                 default: Optional[Any] = None,
                 callback: Optional[Callable[[str], Any]] = None,
                 factory: Optional[Callable[[str | Any], Any]] = None,
                 **kwargs):
        super().__init__(default=default,
                         callback=callback,
                         factory=factory)
        self.pattern = re.compile(pattern, flags) if isinstance(pattern, str) else pattern
        self.group = group

    def _parse(self, markup: str) -> Optional[str]:
        if result := self.pattern.search(markup):
            return result.group(self.group)
        return None


class ReMatchList(BaseField):

    def __init__(self,
                 pattern: str | Pattern,
                 group: int = 1,
                 flags: int | re.RegexFlag = 0,
                 *,
                 default: Optional[Any] = None,
                 filter_: Optional[Callable[[str], bool]] = None,
                 callback: Optional[Callable[[str], Any]] = None,
                 factory: Optional[Callable[[list[str] | Any], Any]] = None,
                 ):
        super().__init__(default=default,
                         filter_=filter_,
                         callback=callback,
                         factory=factory)
        self.pattern = re.compile(pattern, flags) if isinstance(pattern, str) else pattern
        self.group = group

    def _parse(self, markup: str) -> list[str]:
        if matches := self.pattern.finditer(markup):
            return [m.group(self.group) for m in matches]
        return []


class ReMatchDict(BaseField):
    def __init__(self,
                 pattern: str | Pattern,
                 flags: int | re.RegexFlag = 0,
                 *,
                 default: Optional[Any] = None,
                 callback: Optional[Callable[[dict[str, str]], Any]] = None,
                 factory: Optional[Callable[[dict[str, str] | Any], Any]] = None,
                 ):
        super().__init__(default=default,
                         callback=callback,
                         factory=factory)
        self.pattern = re.compile(pattern, flags) if isinstance(pattern, str) else pattern
        if not self.pattern.groupindex:
            raise AttributeError(f"{pattern.pattern} required groups")  # type: ignore

    def _parse(self, markup: str) -> dict[str, str]:
        return result.groupdict() if (result := self.pattern.search(markup)) else {}


class ReMatchListDict(BaseField):
    def __init__(self,
                 pattern: str | Pattern,
                 flags: int | re.RegexFlag = 0,
                 *,
                 default: Optional[Any] = None,
                 filter_: Optional[Callable[[dict[str, str]], bool]] = None,
                 callback: Optional[Callable[[dict[str, str]], Any]] = None,
                 factory: Optional[Callable[[dict[str, str] | Any], Any]] = None,
                 ):
        super().__init__(default=default,
                         callback=callback,
                         filter_=filter_,
                         factory=factory)
        self.pattern = re.compile(pattern, flags) if isinstance(pattern, str) else pattern
        if not self.pattern.groupindex:
            raise AttributeError(f"{pattern.pattern} required groups")  # type: ignore

    def _parse(self, markup: str) -> list[dict[str, str]]:
        if results := self.pattern.finditer(markup):
            return [result.groupdict() for result in results]
        return []
