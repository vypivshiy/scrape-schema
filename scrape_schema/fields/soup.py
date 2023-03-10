from typing import Optional, Any, Callable, TYPE_CHECKING, Iterable, Sequence
import re

from bs4 import BeautifulSoup, Tag, ResultSet

from ..base import BaseField, BaseSchema
from ..tools.soup import get_text


__all__ = [
    "SoupFind",
    "SoupFindList",
    "SoupSelect",
    "SoupSelectList"
]

RE_TAG_NAME = re.compile(r"<(\w+)")
RE_TAG_ATTRS = re.compile(r'(?P<name>[\w_\-:.]+)="(?P<value>[\w_\-:.]+)"')


class SoupFind(BaseField):
    __MARKUP_PARSER__ = BeautifulSoup

    def __init__(self,
                 element: dict[str, Any] | str,
                 *,
                 callback: Callable[[Tag], Any] = get_text(),
                 default: Optional[Any] = None,
                 validator: Optional[Callable[[Any], bool]] = None,
                 filter_: Optional[Callable[[Tag], bool]] = None,
                 factory: Optional[Callable[[str], Any]] = None,
                 ):
        super().__init__(default=default,
                         validator=validator,
                         filter_=filter_,
                         factory=factory,
                         )
        self.element = self._element_to_dict(element) if isinstance(element, str) else element
        self.callback = callback

    @staticmethod
    def _element_to_dict(element: str) -> dict[str, Any]:
        tag_name = RE_TAG_NAME.search(element).group(1)
        attrs = dict(RE_TAG_ATTRS.findall(element))
        return {"name": tag_name, "attrs": attrs}

    def parse(self, instance: BaseSchema, name: str, markup):
        value = markup.find(**self.element) or self.default

        value = self._filter_process(value)
        value = self.callback(value)
        value = self._typing(instance, name, value)
        value = self._factory(value)
        self._raise_validator(instance, name, value)
        return value


class SoupFindList(SoupFind):
    def __init__(self,
                 element: dict[str, Any] | str,
                 *,
                 callback: Callable[[Tag], Any] = get_text(),
                 default: Optional[Any] = None,
                 validator: Optional[Callable[[Any], bool]] = None,
                 filter_: Optional[Callable[[Tag], bool]] = None,
                 factory: Optional[Callable[[list[str]], Any]] = None,
                 ):
        super().__init__(element, default=default, validator=validator, filter_=filter_)
        self.factory = factory
        self.callback = callback

    def parse(self, instance: BaseSchema, name: str, markup: BeautifulSoup) -> ResultSet:
        values = markup.find_all(**self.element) or self.default

        values = self._filter_process(values)
        if values != self.default:
            values = list(map(self.callback, values))
        values = self._typing(instance, name, values)
        values = self._factory(values)
        self._raise_validator(instance, name, values)
        return values


class SoupSelect(BaseField):
    __MARKUP_PARSER__ = BeautifulSoup

    def __init__(self,
                 selector: str,
                 namespaces: Optional[Any] = None,
                 *,
                 callback: Callable[[Tag], Any] = get_text(),
                 default: Optional[Any] = None,
                 validator: Optional[Callable[[Any], bool]] = None,
                 filter_: Optional[Callable[[Any], bool]] = None,
                 factory: Optional[Callable[[Any], Any]] = None,
                 ):
        super().__init__(default=default, validator=validator, filter_=filter_,
                         factory=factory)
        self.callback = callback
        self.selector = selector
        self.namespaces = namespaces

    def parse(self, instance: BaseSchema, name: str, markup: BeautifulSoup):
        value = markup.select_one(self.selector, namespaces=self.namespaces) or self.default

        value = self._filter_process(value)
        value = self.callback(value)
        value = self._typing(instance, name, value)
        value = self._factory(value)
        self._raise_validator(instance, name, value)
        return value


class SoupSelectList(SoupSelect):
    def parse(self, instance: BaseSchema, name: str, markup):
        values = markup.select(self.selector, namespaces=self.namespaces) or self.default
        values = self._filter_process(values)
        if values != self.default:
            values = list(map(self.callback, values))
        values = self._typing(instance, name, values)
        values = self._factory(values)
        self._raise_validator(instance, name, values)
        return values

