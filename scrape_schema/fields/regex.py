from typing import Pattern, Optional, Any, Callable
import re

from ..base import BaseField, BaseSchema
from ..tools.other import nothing_callback


class _ReMatch(BaseField):
    def __init__(
        self,
        pattern: Pattern | str,
        group: int | str = 1,
        flags: Optional[int | re.RegexFlag] = None,
        *,
        default: Optional[Any] = None,
        callback: Callable[[str], Any] = nothing_callback,
        filter_: Optional[Callable[[str], bool]] = None,
        factory: Optional[Callable[[str], Any]] = None,
    ):
        """ReMatch field. Match the **first** occurrence and transforms
        according to the given parameters

        :param pattern: str regex or compiled Pattern
        :param group:  group. Default 1
        :param flags: pattern flags. Default None
        :param default: default value, if regex not found a match. Default None
        :param callback: a callback function rule. Default doing nothing
        :param filter_: a filter function rule. Default doing nothing
        :param factory: a factory function rule. Default doing nothing. If this param added,
        it ignored typing
        """
        super().__init__(default=default, factory=factory, filter_=filter_)
        if flags:
            self.pattern = (
                re.compile(pattern, flags=flags)
                if isinstance(pattern, str)
                else pattern
            )
        else:
            self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        self.group = group
        self.callback = callback

    def parse(self, instance: BaseSchema, name: str, markup: str):
        if match := self.pattern.search(markup):
            value = match.group(self.group)
        else:
            value = self.default

        value = self._filter_process(value)
        value = self._callback(value)
        value = self._typing(instance, name, value)
        value = self._factory(value)
        self._raise_validator(instance, name, value)
        return value


class _ReMatchList(_ReMatch):
    def __init__(
        self,
        pattern: Pattern | str,
        group: int | str = 1,
        flags: Optional[int | re.RegexFlag] = None,
        *,
        callback: Callable[[str], Any] = nothing_callback,
        filter_: Optional[Callable[[list[str]], bool]] = None,
        default: Optional[list[Any]] = None,
        factory: Optional[Callable[[list[str]], Any]] = None,
    ):
        """A ReMatchList field. Match the **all** occurrence and
        transforms according to the given parameters

        :param pattern: str regex or compiled Pattern
        :param group:  group. Default 1
        :param flags: pattern flags. Default None
        :param default: default value, if regex not found a match. Default None
        :param callback: a callback function rule. Default doing nothing
        :param filter_: a filter function rule. Default doing nothing
        :param factory: a factory function rule. Default doing nothing. If this param added,
        it ignored typing
        """
        super().__init__(pattern, group, flags)
        self.default = default if isinstance(default, list) else []
        self.factory = factory
        self.filter_ = filter_
        self.callback = callback

    def parse(self, instance: BaseSchema, name: str, markup: str):
        if matches := self.pattern.finditer(markup):
            values = [m.group(self.group) for m in matches]
        else:
            values = self.default  # type: ignore[assignment]
        values = self._filter_process(values)
        values = self._callback(values)
        values = self._typing(instance, name, values)
        values = self._factory(values)
        self._raise_validator(instance, name, values)
        return values


# dummy avoid mypy type[assignment] errors
ReMatch: Any = _ReMatch
ReMatchList: Any = _ReMatchList
