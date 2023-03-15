from typing import Optional, Any, Callable, TYPE_CHECKING, Iterable, Sequence
import re

from bs4 import BeautifulSoup, Tag, ResultSet

from ..base import BaseField, BaseSchema
from ..tools.soup import get_text, element_to_dict


__all__ = [
    "SoupFind",
    "SoupFindList",
    "SoupSelect",
    "SoupSelectList"
]

RE_TAG_NAME = re.compile(r"<(\w+)")
RE_TAG_ATTRS = re.compile(r'(?P<name>[\w_\-:.]+)="(?P<value>[\w_\-:.]+)"')


class _SoupFind(BaseField):
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
        """get first value by `BeautifulSoup.find` method

        :param element: string html element or dict of kwargs for `BeautifulSoup.find` method
        :param callback: a callback function. Default extract text
        :param default: default value if Tag not founded. Default None
        :param validator: a validator function. default None
        :param filter_: a filter function. default None
        :param factory: a factory function. default None. If this param added, it ignored typing
        """
        super().__init__(default=default,
                         validator=validator,
                         filter_=filter_,
                         factory=factory,
                         )
        self.element = element_to_dict(element) if isinstance(element, str) else element
        self.callback = callback

    def parse(self, instance: BaseSchema, name: str, markup):
        value = markup.find(**self.element) or self.default

        value = self._filter_process(value)
        value = self._callback(value)
        value = self._typing(instance, name, value)
        value = self._factory(value)
        self._raise_validator(instance, name, value)
        return value


class _SoupFindList(_SoupFind):
    def __init__(self,
                 element: dict[str, Any] | str,
                 *,
                 callback: Callable[[Tag], Any] = get_text(),
                 default: Optional[Any] = None,
                 validator: Optional[Callable[[Any], bool]] = None,
                 filter_: Optional[Callable[[Tag], bool]] = None,
                 factory: Optional[Callable[[list[str]], Any]] = None,
                 ):
        """get all values by `BeautifulSoup.find_all` method

        :param element: string html element or dict of kwargs for `BeautifulSoup.find` method
        :param callback: a callback function. Default extract text
        :param default: default value if Tag not founded. Default None
        :param validator: a validator function. default None
        :param filter_: a filter function. default None
        :param factory: a factory function. default None. If this param added, it ignored typing
        """
        super().__init__(element, default=default, validator=validator, filter_=filter_)
        self.factory = factory
        self.callback = callback

    def parse(self, instance: BaseSchema, name: str, markup: BeautifulSoup) -> ResultSet:
        values = markup.find_all(**self.element) or self.default

        values = self._filter_process(values)
        if values != self.default:
            values = list(map(self._callback, values))
        values = self._typing(instance, name, values)
        values = self._factory(values)
        self._raise_validator(instance, name, values)
        return values


class _SoupSelect(BaseField):
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
        """get first value by `BeautifulSoup.select_one` method

        :param selector: css selector
        :param namespaces:  A dictionary mapping namespace prefixes used in the CSS selector to namespace URIs.
        By default, Beautiful Soup will use the prefixes it encountered while parsing the document.
        :param callback: a callback function. Default extract text
        :param default: default value if Tag not founded. Default None
        :param validator: a validator function. default None
        :param filter_: a filter function. default None
        :param factory: a factory function. default None. If this param added, it ignored typing
        """
        super().__init__(default=default, validator=validator, filter_=filter_,
                         factory=factory)
        self.callback = callback
        self.selector = selector
        self.namespaces = namespaces

    def parse(self, instance: BaseSchema, name: str, markup: BeautifulSoup):
        value = markup.select_one(self.selector, namespaces=self.namespaces) or self.default

        value = self._filter_process(value)
        value = self._callback(value)
        value = self._typing(instance, name, value)
        value = self._factory(value)
        self._raise_validator(instance, name, value)
        return value


class _SoupSelectList(_SoupSelect):

    def __init__(self,
                 selector: str,
                 namespaces: Optional[Any] = None, *,
                 callback: Callable[[Tag], Any] = get_text(),
                 default: Optional[Any] = None,
                 validator: Optional[Callable[[Any], bool]] = None,
                 filter_: Optional[Callable[[Any], bool]] = None,
                 factory: Optional[Callable[[Any], Any]] = None):
        """get first value by `BeautifulSoup.select_one` method

        :param selector: css selector
        :param namespaces:  A dictionary mapping namespace prefixes used in the CSS selector to namespace URIs.
        By default, Beautiful Soup will use the prefixes it encountered while parsing the document.
        :param callback: a callback function. Default extract text
        :param default: default value if Tag not founded. Default None
        :param validator: a validator function. default None
        :param filter_: a filter function. default None
        :param factory: a factory function. default None. If this param added, it ignored typing
        """
        super().__init__(selector, namespaces, callback=callback, default=default, validator=validator, filter_=filter_,
                         factory=factory)

    def parse(self, instance: BaseSchema, name: str, markup):
        values = markup.select(self.selector, namespaces=self.namespaces) or self.default
        values = self._filter_process(values)
        if values != self.default:
            values = list(map(self._callback, values))
        values = self._typing(instance, name, values)
        values = self._factory(values)
        self._raise_validator(instance, name, values)
        return values


# dummy avoid mypy type[assignment] errors
SoupFind: Any = _SoupFind
SoupFindList: Any = _SoupFindList
SoupSelect: Any = _SoupSelect
SoupSelectList: Any = _SoupSelectList
