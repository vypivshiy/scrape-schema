from typing import Callable, Any, Optional

from selectolax.parser import HTMLParser
from selectolax.parser import Node

from .. import BaseSchema
from ..base import BaseField
from ..tools.slax import get_text

__all__ = [
    "SLaxSelect",
    "SLaxSelectList"
]


class SLaxSelect(BaseField):
    __MARKUP_PARSER__ = HTMLParser

    def __init__(self,
                 query: str,
                 strict: bool = False,
                 *,
                 callback: Callable[[Node], Any] = get_text(),
                 default: Optional[Any] = None,
                 validator: Optional[Callable[[Any], bool]] = None,
                 filter_: Optional[Callable[[Node], bool]] = None,
                 factory: Optional[Callable[[str], Any]] = None,
                 ):
        super().__init__(default=default, validator=validator,
                         filter_=filter_, factory=factory)
        self.query = query
        self.strict = strict
        self.callback = callback

    def parse(self, instance: BaseSchema, name: str, markup: HTMLParser):
        value = markup.css_first(self.query, strict=self.strict)
        if not value:
            value = self.default
        value = self._filter_process(value)
        value = self.callback(value)
        value = self._typing(instance, name, value)
        value = self._factory(value)
        self._raise_validator(instance, name, self.default)
        return value


class SLaxSelectList(SLaxSelect):
    def __init__(self,
                 query: str,
                 strict: bool = False,
                 *,
                 callback: Callable[[Node], Any] = get_text(),
                 default: Optional[Any] = None,
                 validator: Optional[Callable[[Any], bool]] = None,
                 filter_: Optional[Callable[[Node], bool]] = None,
                 factory: Optional[Callable[[list[str]], Any]] = None):
        super().__init__(query, strict, callback=callback, default=default, validator=validator, filter_=filter_,
                         factory=factory)

    def parse(self, instance: BaseSchema, name: str, markup: HTMLParser):
        values = markup.css(self.query)
        if not values:
            values = self.default

        values = self._filter_process(values)
        if values != self.default:
            values = list(map(self.callback, values))
        values = self._typing(instance, name, values)
        values = self._factory(values)
        self._raise_validator(instance, name, values)
        return values
