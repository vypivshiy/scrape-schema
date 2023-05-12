"""This fields usage selectolax backend

References:

* https://selectolax.readthedocs.io/en/latest/index.html

**SlaxSelect**

* https://selectolax.readthedocs.io/en/latest/parser.html#selectolax.parser.HTMLParser.css_first

**SlaxSelectList**

* https://selectolax.readthedocs.io/en/latest/parser.html#selectolax.parser.HTMLParser.css

"""

from abc import ABC
from functools import partial
from typing import Any, Callable, List, Optional, Union

from selectolax.parser import HTMLParser, Node

from scrape_schema.base import BaseField, BaseFieldConfig
from scrape_schema.callbacks.slax import get_text
from scrape_schema.fields.nested import Nested, NestedList

__all__ = ["BaseSlax", "SlaxSelect", "SlaxSelectList", "NestedSlax", "NestedSlaxList"]


NestedSlax = partial(Nested, parser=HTMLParser)
NestedSlaxList = partial(NestedList, parser=HTMLParser)


class BaseSlax(BaseField, ABC):
    class Config(BaseFieldConfig):
        parser = HTMLParser


class SlaxSelect(BaseSlax):
    def __init__(
        self,
        selector: str,
        strict: bool = False,
        *,
        default: Optional[Any] = None,
        callback: Optional[Callable[[Node], Union[str, Any]]] = get_text(),
        factory: Optional[Callable[[Union[str, Any]], Any]] = None,
    ):
        """Get Node by HTMLParser(...).css_first

        :param selector: css selector
        :param strict: Check if there is strictly only one match in the document. Default False
        :param default: default value if match not founded. default None
        :param callback: function eval result. default get text from element
        :param factory: function final cast result. If passed - ignore type-casting. Default None
        """
        super().__init__(default=default, callback=callback, factory=factory)
        self.selector = selector
        self.strict = strict

    def _parse(self, markup: HTMLParser) -> Node:
        return markup.css_first(self.selector, strict=self.strict)


class SlaxSelectList(BaseSlax):
    def __init__(
        self,
        selector: str,
        *,
        default: Optional[Any] = None,
        filter_: Optional[Callable[[Node], bool]] = None,
        callback: Optional[Callable[[Node], Union[str, Any]]] = get_text(),
        factory: Optional[Callable[[List[Union[str, Any]]], Any]] = None,
    ):
        """get all Nodes by HTMLParser(...).css

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

    def _parse(self, markup: HTMLParser) -> List[Node]:
        return markup.css(self.selector)
