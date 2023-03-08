from typing import Callable, Any, Optional

from selectolax.parser import HTMLParser
from selectolax.parser import Node

from .. import BaseSchema
from ..base import BaseField

__all__ = [
    "SLaxSelect",
    "SLaxSelectList"
]


def default_callback(deep: bool = True,
                     separator: str = "",
                     strip: bool = False) -> Callable[[Node], str]:
    def wrapper(element: Node):
        return element.text(deep=deep, separator=separator, strip=strip)

    return wrapper


class SLaxSelect(BaseField):
    __MARKUP_PARSER__ = HTMLParser

    def __init__(self,
                 query: str,
                 strict: bool = False,
                 *,
                 callback: Callable[[Node], Any] = default_callback(),
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
            self._raise_validator(instance, name, self.default)
            return self.default
        value = list(filter(self._filter, [value]))[0]
        value = self.callback(value)
        if self.factory:
            value = self.factory(value)
        elif type_ := self._get_type(instance, name):
            value = type_(value)
        self._raise_validator(instance, name, self.default)
        return value


class SLaxSelectList(SLaxSelect):
    def __init__(self,
                 query: str,
                 strict: bool = False,
                 *,
                 callback: Callable[[Node], Any] = default_callback(),
                 default: Optional[Any] = None,
                 validator: Optional[Callable[[Any], bool]] = None,
                 filter_: Optional[Callable[[Node], bool]] = None,
                 factory: Optional[Callable[[list[str]], Any]] = None):
        super().__init__(query, strict, callback=callback, default=default, validator=validator, filter_=filter_,
                         factory=factory)

    def parse(self, instance: BaseSchema, name: str, markup: HTMLParser):
        values = markup.css(self.query)
        if not values:
            self._raise_validator(instance, name, self.default)
            return self.default
        values = list(filter(self._filter, values))
        values = list(map(self.callback, values))
        if self.factory:
            values = self.factory(values)
        elif type_ := self._get_type(instance, name):
            values = [type_(val) for val in values]
        self._raise_validator(instance, name, values)
        return values
