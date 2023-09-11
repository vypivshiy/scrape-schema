"""Validator methods and decorators"""
import re
from functools import wraps
from typing import TYPE_CHECKING, Callable, Optional, Union

from parsel import Selector, SelectorList

from scrape_schema.exceptions import SchemaPreValidationError

if TYPE_CHECKING:
    from scrape_schema import BaseSchema


__all__ = ["markup_pre_validator"]


class MarkupPreValidator:
    """pre validate markup decorator"""

    def __init__(
        self,
        *,
        pattern: Optional[str] = None,
        css: Optional[str] = None,
        xpath: Optional[str] = None,
    ):
        """Pre-validation of markup for the schema.

        If the given pattern returns False, it will throw SchemaPreValidationError

        Args:
            pattern: regex pattern
            css: css query
            xpath: xpath query

        Returns:
            Schema if all checks passed

        Raises:
            SchemaPreValidationError: if any match returns False

        """
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
            if self.css and not self._pre_validate_css(cls_self.__selector__):
                msg = (
                    f"Failed validate css `{self.css}` in `{cls_self.__schema_name__}`"
                )
                raise SchemaPreValidationError(msg)
            if self.xpath and not self._pre_validate_xpath(cls_self.__selector__):
                msg = f"Failed validate xpath `{self.xpath}` in `{cls_self.__schema_name__}`"
                raise SchemaPreValidationError(msg)
            return func(cls_self)

        return inner

    def _pre_validate_re(self, markup: str) -> bool:
        return bool(re.search(self.pattern, markup))  # type: ignore

    def _pre_validate_css(self, markup: Union[Selector, SelectorList]) -> bool:
        return bool(markup.css(self.css).get())  # type: ignore

    def _pre_validate_xpath(self, markup: Union[Selector, SelectorList]) -> bool:
        return bool(markup.xpath(self.xpath).get())  # type: ignore


markup_pre_validator = MarkupPreValidator
