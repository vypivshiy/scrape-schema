from typing import Pattern, Optional, Any, Callable
import re

from ..base import BaseField, BaseSchema
from ..tools.other import nothing_callback


class ReMatch(BaseField):
    def __init__(self,
                 pattern: Pattern | str,
                 group: int | str | tuple[str | int, ...] = 1,
                 flags: Optional[int | re.RegexFlag] = None,
                 *,
                 default: Optional[Any] = None,
                 callback: Callable[[str], Any] = nothing_callback,
                 filter_: Optional[Callable[[str], bool]] = None,
                 factory: Optional[Callable[[str], Any]] = None,
                 ):
        super().__init__(default=default, factory=factory, filter_=filter_)
        self.pattern = re.compile(pattern, flags=flags) if isinstance(pattern, str) else pattern
        self.group = group
        self.callback = callback

    def parse(self, instance: BaseSchema, name: str, markup: str):
        if match := self.pattern.search(markup):
            value = match.group(self.group)
        else:
            value = self.default
        value = list(filter(self._filter, [value]))[0]
        value = self.callback(value)
        if self.factory:
            value = self.factory(value)
        elif type_ := self._get_type(instance, name):
            value = type_(value)
        self._raise_validator(instance, name, value)
        return value


class ReMatchList(ReMatch):
    def __init__(self,
                 pattern: Pattern | str,
                 group: int | str | tuple[str | int, ...] = 1,
                 flags: Optional[int | re.RegexFlag] = None,
                 *,
                 callback: Callable[[list[str]], Any] = nothing_callback,
                 filter_: Optional[Callable[[list[str]], bool]] = None,
                 default: Optional[Any] = None,
                 factory: Optional[Callable[[list[str]], Any]] = None,
                 ):
        super().__init__(pattern, group, flags, default=default, factory=factory, filter_=filter_)
        self.callback = callback

    def parse(self, instance: BaseSchema, name: str, markup: str):
        if match := list(self.pattern.finditer(markup)):
            values = [m.group(self.group) for m in match]
        else:
            values = self.default
        values = list(filter(self._filter, values))
        values = self.callback(values)
        if self.factory:
            values = self.factory(values)
        elif type_ := self._get_type(instance, name):
            values = [type_(value) for value in values]
        self._raise_validator(instance, name, values)
        return values
