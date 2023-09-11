"""Validator methods and decorators"""
import re
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Union

from parsel import Selector, SelectorList

from scrape_schema.exceptions import SchemaPreValidationError

if TYPE_CHECKING:
    from scrape_schema import BaseSchema


MARKUP_TYPE = Union[str, bytes, "Selector", "SelectorList"]

__all__ = ["markup_pre_validator"]


class MarkupPreValidator:
    """pre validate markup decorator"""

    def __init__(
        self,
        *,
        pattern: Optional[str] = None,
        css: Optional[str] = None,
        xpath: Optional[str] = None,
        selector_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """Pre-validation of markup for the schema.

        If the given pattern returns False, it will throw SchemaPreValidationError

        Args:
            pattern: regex pattern
            css: css query
            xpath: xpath query
            selector_kwargs: kwargs for parsel.Selector class

        Returns:
            Schema if all checks passed

        Raises:
            SchemaPreValidationError: if any match returns False

        """
        self.selector_kwargs = selector_kwargs or {}
        self.xpath = xpath
        self.css = css
        self.pattern = pattern

    def __call__(self, func: Callable[["BaseSchema"], bool]):
        # hack for hook this validator in Schema constructor
        # by __wrapped__ method
        @wraps(MarkupPreValidator)
        def inner(cls_self: "BaseSchema"):
            if self.pattern and not self._pre_validate_re(cls_self.__raw__):
                msg = f"Failed validate re `{self.pattern}` in `{cls_self.__schema_name__}`"
                raise SchemaPreValidationError(msg)
            if self.css and not self._pre_validate_css(cls_self.__raw__):
                msg = (
                    f"Failed validate css `{self.css}` in `{cls_self.__schema_name__}`"
                )
                raise SchemaPreValidationError(msg)
            if self.xpath and not self._pre_validate_xpath(cls_self.__raw__):
                msg = f"Failed validate xpath `{self.xpath}` in `{cls_self.__schema_name__}`"
                raise SchemaPreValidationError(msg)
            return func(cls_self)

        return inner

    def _pre_validate_re(self, markup: MARKUP_TYPE) -> bool:
        if isinstance(markup, (Selector, SelectorList)):
            return bool(markup.re(self.pattern))  # type: ignore
        elif isinstance(markup, bytes):
            return bool(re.search(self.pattern, str(markup)))  # type: ignore
        return bool(re.search(self.pattern, markup))  # type: ignore

    def _pre_validate_css(self, markup: MARKUP_TYPE) -> bool:
        if isinstance(markup, (Selector, SelectorList)):
            return bool(markup.css(self.css).get())  # type: ignore
        elif isinstance(markup, bytes):
            return bool(  # type: ignore
                Selector(body=markup, **self.selector_kwargs).css(self.css).get()  # type: ignore
            )
        return bool(Selector(markup, **self.selector_kwargs).css(self.css).get())  # type: ignore

    def _pre_validate_xpath(self, markup: MARKUP_TYPE) -> bool:
        if isinstance(markup, (Selector, SelectorList)):
            return bool(markup.xpath(self.xpath).get())  # type: ignore
        elif isinstance(markup, bytes):
            return bool(
                Selector(body=markup, **self.selector_kwargs).xpath(self.xpath).get()  # type: ignore
            )
        return bool(Selector(markup, **self.selector_kwargs).xpath(self.xpath).get())  # type: ignore


markup_pre_validator = MarkupPreValidator
