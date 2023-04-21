"""This fields usage selectolax backend

References:

* https://selectolax.readthedocs.io/en/latest/index.html

**SlaxSelect**

* https://selectolax.readthedocs.io/en/latest/parser.html#selectolax.parser.HTMLParser.css_first

**SlaxSelectList**

* https://selectolax.readthedocs.io/en/latest/parser.html#selectolax.parser.HTMLParser.css

"""
from abc import ABC
from typing import Any, Callable, Optional

from selectolax.parser import HTMLParser, Node

from ..base import BaseConfigField, BaseField
from ..callbacks.slax import get_text

__all__ = ["BaseSlax", "SlaxSelect", "SlaxSelectList"]


class BaseSlax(BaseField, ABC):
    class Config(BaseConfigField):
        parser = HTMLParser


class SlaxSelect(BaseSlax):
    def __init__(
        self,
        selector: str,
        strict: bool = False,
        *,
        default: Optional[Any] = None,
        callback: Optional[Callable[[Node], str | Any]] = get_text(),
        factory: Optional[Callable[[str | Any], Any]] = None,
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
        callback: Optional[Callable[[Node], str | Any]] = get_text(),
        factory: Optional[Callable[[list[str | Any]], Any]] = None,
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

    def _parse(self, markup: HTMLParser) -> list[Node]:
        return markup.css(self.selector)
