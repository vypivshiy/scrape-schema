"""this fields usage parsel library

Reference:

* https://parsel.readthedocs.io/en/latest/

"""
from abc import ABC
from functools import partial
from typing import Any, Callable, Mapping, Optional, Union

from parsel import Selector, SelectorList
from parsel.selector import _SelectorType

from scrape_schema.callbacks.parsel import get_text
from scrape_schema.fields.nested import Nested, NestedList

from ..base import BaseField, BaseFieldConfig

__all__ = [
    "BaseParselField",
    "ParselSelect",
    "ParselSelectList",
    "ParselXPath",
    "ParselXPathList",
    "NestedParsel",
    "NestedParselList",
]

NestedParsel = partial(Nested, parser=Selector)
NestedParselList = partial(NestedList, parser=Selector)


class BaseParselField(BaseField, ABC):
    class Config(BaseFieldConfig):
        parser = Selector


class ParselSelect(BaseParselField):
    def __init__(
        self,
        query: str,
        *,
        default: Optional[Any] = None,
        callback: Optional[Callable[[_SelectorType], Union[str, Any]]] = get_text(),
        factory: Optional[Callable[[Union[str, Any]], Any]] = None,
    ):
        super().__init__(default=default, callback=callback, factory=factory)
        self.query = query

    def _parse(self, markup: _SelectorType) -> Optional[_SelectorType]:
        return tag[0] if (tag := markup.css(self.query)) else None


class ParselSelectList(BaseParselField):
    def __init__(
        self,
        query: str,
        *,
        default: Optional[Any] = None,
        callback: Optional[Callable[[_SelectorType], Union[str, Any]]] = get_text(),
        filter_: Optional[Callable[[_SelectorType], bool]] = None,
        factory: Optional[Callable[[Union[str, Any]], Any]] = None,
    ):
        super().__init__(
            default=default, callback=callback, factory=factory, filter_=filter_
        )
        self.query = query

    def _parse(self, markup: _SelectorType) -> SelectorList[_SelectorType]:
        return markup.css(self.query)


class ParselXPath(BaseParselField):
    def __init__(
        self,
        query: str,
        namespaces: Optional[Mapping[str, str]] = None,
        *,
        default: Optional[Any] = None,
        callback: Optional[Callable[[_SelectorType], Union[str, Any]]] = get_text(),
        factory: Optional[Callable[[Union[str, Any]], Any]] = None,
        **xpath_kwargs: Any,
    ):
        super().__init__(default=default, callback=callback, factory=factory)
        self.query = query
        self.namespaces = namespaces
        self.xpath_kwargs = xpath_kwargs

    def _parse(self, markup: _SelectorType) -> Optional[_SelectorType]:
        return (
            tag[0]
            if (
                tag := markup.xpath(
                    query=self.query, namespaces=self.namespaces, **self.xpath_kwargs
                )
            )
            else None
        )


class ParselXPathList(BaseParselField):
    def __init__(
        self,
        query: str,
        namespaces: Optional[Mapping[str, str]] = None,
        *,
        default: Optional[Any] = None,
        callback: Optional[Callable[[_SelectorType], Union[str, Any]]] = get_text(),
        factory: Optional[Callable[[Union[str, Any]], Any]] = None,
        filter_: Optional[Callable[[_SelectorType], bool]] = None,
        **xpath_kwargs: Any,
    ):
        super().__init__(
            default=default, callback=callback, factory=factory, filter_=filter_
        )
        self.query = query
        self.namespaces = namespaces
        self.xpath_kwargs = xpath_kwargs

    def _parse(self, markup: _SelectorType) -> SelectorList[_SelectorType]:
        return markup.xpath(
            query=self.query, namespaces=self.namespaces, **self.xpath_kwargs
        )
