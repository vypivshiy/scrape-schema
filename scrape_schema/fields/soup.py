"""This fields usage bs4 backend

References:

* https://beautiful-soup-4.readthedocs.io/en/latest/

**SoupFind**

* https://beautiful-soup-4.readthedocs.io/en/latest/#find

**SoupFindList**

* https://beautiful-soup-4.readthedocs.io/en/latest/#find-all

**BeautifulSoup(...).find, BeautifulSoup(...).find_all** features:

* https://beautiful-soup-4.readthedocs.io/en/latest/#a-regular-expression

* https://beautiful-soup-4.readthedocs.io/en/latest/#a-list

* https://beautiful-soup-4.readthedocs.io/en/latest/#a-function


**SoupSelect, SoupSelectList**

* https://beautiful-soup-4.readthedocs.io/en/latest/#css-selectors
"""
from abc import ABC
from typing import Any, Callable, Optional

from bs4 import BeautifulSoup, ResultSet, Tag

from ..base import BaseConfigField, BaseField
from ..callbacks.soup import element_to_dict, get_text

__all__ = ["BaseSoup", "SoupFind", "SoupFindList", "SoupSelect", "SoupSelectList"]


class BaseSoup(BaseField, ABC):
    class Config(BaseConfigField):
        parser = BeautifulSoup


class SoupFind(BaseSoup):
    def __init__(
        self,
        element: str | dict[str, Any],
        *,
        default: Optional[Any] = None,
        callback: Optional[Callable[[Tag], str | Any]] = get_text(),
        factory: Optional[Callable[[str | Any], Any]] = None,
    ):
        """get Tag by BeautifulSoup(...).find method

        :param element: html tag or dict of keyword args for BeautifulSoup(...).find method
        :param default: default value if match not founded. default None
        :param callback: function eval result. default get text from element
        :param factory: function final cast result. If passed - ignore type-casting. Default None
        """
        super().__init__(default=default, callback=callback, factory=factory)
        self.element = element_to_dict(element) if isinstance(element, str) else element

    def _parse(self, markup: BeautifulSoup | Tag) -> Optional[Tag]:
        return markup.find(**self.element)


class SoupFindList(BaseSoup):
    def __init__(
        self,
        element: str | dict[str, Any],
        *,
        default: Optional[Any] = None,
        filter_: Optional[Callable[[Tag], bool]] = None,
        callback: Optional[Callable[[Tag], str | Any]] = get_text(),
        factory: Optional[Callable[[list[str | Any] | Any], Any]] = None,
    ):
        """get Tags by BeautifulSoup(...).find_all method

        :param element: html tag or dict of keyword args for BeautifulSoup(...).find_all method
        :param default: default value if match not founded. default None
        :param filter_: function for filter result list. default None
        :param callback: function eval result. default get text from element
        :param factory: function final cast result. If passed - ignore type-casting. Default None
        """
        super().__init__(
            default=default, callback=callback, factory=factory, filter_=filter_
        )
        self.element = element_to_dict(element) if isinstance(element, str) else element

    def _parse(self, markup: BeautifulSoup | Tag) -> ResultSet:
        return markup.find_all(**self.element)


class SoupSelect(BaseSoup):
    def __init__(
        self,
        selector: str,
        *,
        default: Optional[Any] = None,
        callback: Optional[Callable[[Tag], Any]] = get_text(),
        factory: Optional[Callable[[str | Any], Any]] = None,
    ):
        """Get tag by BeautifulSoup(...).select_one method

        :param selector: css selector
        :param default: default value if match not founded. default None
        :param callback: function eval result. default get text from element
        :param factory: function final cast result. If passed - ignore type-casting. Default None
        """
        super().__init__(default=default, callback=callback, factory=factory)
        self.selector = selector

    def _parse(self, markup: BeautifulSoup | Tag) -> Tag:
        return markup.select_one(self.selector)


class SoupSelectList(BaseSoup):
    def __init__(
        self,
        selector: str,
        *,
        default: Optional[Any] = None,
        filter_: Optional[Callable[[Tag], bool]] = None,
        callback: Optional[Callable[[Tag], Any]] = get_text(),
        factory: Optional[Callable[[list[str | Any]], Any]] = None,
    ):
        """Get tags by BeautifulSoup(...).select method

        :param selector: css selector
        :param default: default value if match not founded. default None
        :param filter_: function for filter result list. default None
        :param callback: function eval result. default get text from element
        :param factory: function final cast result. If passed - ignore type-casting. Default None
        """
        super().__init__(
            default=default, callback=callback, factory=factory, filter_=filter_
        )
        self.selector = selector

    def _parse(self, markup: BeautifulSoup | Tag) -> ResultSet:
        return markup.select(self.selector)
