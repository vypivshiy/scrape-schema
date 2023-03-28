from abc import ABC
from typing import Any, Callable, Optional

from ..base import BaseField, MetaField
from ..callbacks.soup import get_text, element_to_dict

from bs4 import BeautifulSoup, Tag, ResultSet


__all__ = [
    'BaseSoup',
    'SoupFind',
    'SoupFindList',
    'SoupSelect',
    'SoupSelectList'
]

class BaseSoup(BaseField, ABC):
    class Meta(MetaField):
        parser = BeautifulSoup


class SoupFind(BaseSoup):
    def __init__(self,
                 element: str | dict[str, Any],
                 *,
                 default: Optional[Any] = None,
                 callback: Optional[Callable[[Tag], str | Any]] = get_text(),
                 factory: Optional[Callable[[str | Any], Any]] = None,
                 **kwargs):
        super().__init__(default=default, callback=callback, factory=factory, **kwargs)
        self.element = element_to_dict(element) if isinstance(element, str) else element

    def _parse(self, markup: BeautifulSoup | Tag) -> Optional[Tag]:
        return markup.find(**self.element)


class SoupFindList(BaseSoup):
    def __init__(self,
                 element: str | dict[str, Any],
                 *,
                 default: Optional[Any] = None,
                 filter_: Optional[Callable[[Tag], bool]] = None,
                 callback: Optional[Callable[[Tag], str | Any]] = get_text(),
                 factory: Optional[Callable[[list[str | Any] | Any], Any]] = None,
                 ):
        super().__init__(default=default, callback=callback, factory=factory, filter_=filter_)
        self.element = element_to_dict(element) if isinstance(element, str) else element

    def _parse(self, markup: BeautifulSoup | Tag) -> ResultSet:
        return markup.find_all(**self.element)


class SoupSelect(BaseSoup):
    def __init__(self,
                 selector: str,
                 *,
                 default: Optional[Any] = None,
                 callback: Optional[Callable[[Tag], Any]] = get_text(),
                 factory: Optional[Callable[[str | Any], Any]] = None,
                 ):
        super().__init__(default=default, callback=callback, factory=factory)
        self.selector = selector

    def _parse(self, markup: BeautifulSoup | Tag) -> Tag:
        return markup.select_one(self.selector)


class SoupSelectList(BaseSoup):
    def __init__(self,
                 selector: str,
                 *,
                 default: Optional[Any] = None,
                 filter_: Optional[Callable[[Tag], bool]] = None,
                 callback: Optional[Callable[[Tag], Any]] = get_text(),
                 factory: Optional[Callable[[list[str | Any]], Any]] = None,
                 ):
        super().__init__(default=default, callback=callback, factory=factory, filter_=filter_)
        self.selector = selector

    def _parse(self, markup: BeautifulSoup | Tag) -> ResultSet:
        return markup.select(self.selector)
