from abc import ABC
from typing import Any, Optional, Callable

from ..base import BaseField, MetaField
from ..callbacks.slax import get_text

from selectolax.parser import HTMLParser, Node


class BaseSlax(BaseField, ABC):
    class Meta(MetaField):
        parser = HTMLParser


class SlaxSelect(BaseSlax):
    def __init__(self,
                 selector: str,
                 strict: bool = False,
                 *,
                 default: Optional[Any] = None,
                 callback: Optional[Callable[[Node], str | Any]] = get_text(),
                 factory: Optional[Callable[[str | Any], Any]] = None,
                 ):
        super().__init__(default=default, callback=callback, factory=factory)
        self.selector = selector
        self.strict = strict

    def _parse(self, markup: HTMLParser) -> Node:
        return markup.css_first(self.selector, strict=self.strict)


class SlaxSelectList(BaseSlax):

    def __init__(self,
                 selector: str,
                 *,
                 default: Optional[Any] = None,
                 filter_: Optional[Callable[[Node], bool]] = None,
                 callback: Optional[Callable[[Node], str | Any]] = get_text(),
                 factory: Optional[Callable[[list[str | Any]], Any]] = None,
                 ):
        super().__init__(default=default, callback=callback, factory=factory, filter_=filter_)
        self.selector = selector

    def _parse(self, markup: HTMLParser) -> list[Node]:
        return markup.css(self.selector)
