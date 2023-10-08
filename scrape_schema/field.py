"""build-in fields"""
import re
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Hashable,
    List,
    Mapping,
    Optional,
    Pattern,
    TypedDict,
    Union,
)

from scrape_schema._logger import _logger
from scrape_schema._protocols import AttribProtocol, SpecialMethodsProtocol
from scrape_schema._typing import Self
from scrape_schema.base import Field
from scrape_schema.special_methods import SpecialMethods

if TYPE_CHECKING:
    from parsel import Selector, SelectorList

TableDictView = TypedDict(
    "TableDictView",
    {
        "columns": List[str],
        "cells": List[List[str]],
        "table": Dict[str, List[Optional[str]]],
    },
)


class Parsel(Field):
    """This field provide parsel.Selector api and special methods"""

    def __init__(
        self,
        auto_type: bool = True,
        default: Any = ...,
        *,
        raw: bool = False,
        alias: Optional[str] = None,
    ) -> None:
        """Base field provide Parsel.Selector API and special methods

                Args:
                    auto_type: usage auto type feature in BaseSchema scope. Default True
                    default: set default value, if method return traceback.
        Disable auto type andIf not set - raise error
                    raw: raw text parse mode. Auto accept `.xpath("//p/text()").get()` method
                    alias: field alias. default None
        """
        super().__init__(auto_type=auto_type, default=default, alias=alias)
        if raw:
            self.xpath("//p/text()").get()

    def css(self, query: str) -> Self:
        """Apply the given CSS selector and return a SelectorList instance.

        query is a string containing the CSS selector to apply.

        In the background, CSS queries are translated into XPath queries using cssselect
        library and run .xpath() method.
        """
        return self.add_method("css", query)

    @property
    def raw_text(self) -> SpecialMethodsProtocol:
        """Shortcut `Parsel().xpath('//p/text()')` call.

        This method for getting raw text (not html), when calling `parsel.Selector`
        methods will raise an error
        """
        # Parsel is not meant for raw text: it will try to "fix" html and parse as html usage `raw_text` property
        # or `xpath(//p/text()).get()` or raw=True in init constructor
        return self.xpath("//p/text()").get()

    def xpath(
        self, query: str, namespaces: Optional[Mapping[str, str]] = None, **kwargs: Any
    ) -> Self:
        """Xpath selector
        Args:
            query: is a string containing the XPATH query to apply.
            namespaces: is an optional ``prefix: namespace-uri`` mapping (dict) for additional prefixes.
            **kwargs: field alias. default None

        Returns:
            SelectorList

        """

        return self.add_method("xpath", query, namespaces, **kwargs)

    def re(
        self, regex: Union[str, Pattern[str]], replace_entities: bool = True
    ) -> SpecialMethodsProtocol:
        """
        Apply the given regex and return a list of strings with the
        matches.

        Args:
            regex: regular expression
            replace_entities: replace char entity refers replaced by their corresponding char (``&amp;``, ``&lt;``).

        Returns:
            string
        """
        return self.add_method("re", regex, replace_entities)  # type: ignore

    def _is_attrib(self):
        if (method := self._stack_methods[-1].METHOD_NAME) != "attrib":
            _logger.error("Last method should be `attrib, not %s", method)
            raise TypeError(f"Last method should be `attrib`, not `{method}`")
        return True

    def get(
        self, default: Optional[str] = None, key: Optional[Hashable] = None
    ) -> SpecialMethodsProtocol:  # type: ignore
        """Serialize and return the matched nodes in a single string.

        Percent encoded content is unquoted.

        If `key` param passed - get value from attrib property.

        Args:
            default: invoke Selector.get() method and return default value if is None
            key: get value from attrib property *attrib should be called in chain methods*

        Raises:
            TypeError: if passed default and key arguments
        """
        if key and default:
            _logger.error(
                "get should be accept `key` OR `default` param, not `key` AND `default`"
            )
            raise TypeError(
                "get should be accept `key` OR `default` param, not `key` AND `default`"
            )
        elif key:
            if self._is_attrib():
                return self.add_method("get", key)  # type: ignore
        return self.add_method("get", default)  # type: ignore

    def jmespath(self, query: str, **kwargs: Any) -> Self:
        """Find objects matching the JMESPath ``query`` and return the result as a
        SelectorList instance with all elements flattened.
        List elements implement `Selector` interface too.

        Args:
            query: JMESPath string query
            **kwargs:  Any additional named arguments are passed to the underlying
        """
        return self.add_method("jmespath", query, **kwargs)

    def getall(self) -> SpecialMethodsProtocol:
        """Call the .get() method for each element is this list
        and return their results flattened, as a list of strings.

        Returns:
            list[str]
        """
        return self.add_method("getall")  # type: ignore

    @property
    def attrib(self) -> AttribProtocol:
        """
        Return the attributes dictionary for the first element.

        If the list is empty, return an empty dict.

        Returns:
            dict[str, str]
        """
        return self.add_method("attrib")  # type: ignore

    def keys(self) -> SpecialMethodsProtocol:  # type: ignore
        """Get attrib keys

        Returns:
            dict keys
        Raises:
            TypeError: if prev chain is not attrib
        """
        if self._is_attrib():
            return self.add_method("keys")  # type: ignore

    def values(self) -> SpecialMethodsProtocol:  # type: ignore
        """Get attrib values

        Returns:
            dict_values
        Raises:
            TypeError: if prev chain is not attrib
        """
        if self._is_attrib():
            return self.add_method("values")  # type: ignore

    def items(self) -> SpecialMethodsProtocol:  # type: ignore
        """Get attrib items

        Returns:
            dict items
        Raises:
            TypeError: if prev chain is not attrib
        """
        if self._is_attrib():
            return self.add_method("items")  # type: ignore


class JMESPath(Field):
    """This field provide parsel.Selector api and special methods for json data"""

    def __init__(
        self, auto_type: bool = False, default: Any = ..., alias: Optional[str] = None
    ) -> None:
        """this field provide jmespath and special methods API

        Args:
            auto_type: usage auto_type feature. Default False
            default: default
            alias: field alias. default None
        """
        super().__init__(auto_type=auto_type, default=default, alias=alias)

    def jmespath(self, query: str, **kwargs: Any) -> Self:
        """Find objects matching the JMESPath ``query`` and return the result as a
        SelectorList instance with all elements flattened.
        List elements implement `Selector` interface too.

        Args:
            query: JMESPath string query
            **kwargs:  Any additional named arguments are passed to the underlying
        """
        return self.add_method("jmespath", query, **kwargs)

    def get(
        self, default: Optional[str] = None
    ) -> SpecialMethodsProtocol:  # type: ignore
        """Serialize and return the matched nodes in a single string.

        Percent encoded content is unquoted.

        If `key` param passed - get value from attrib property.

        Args:
            default: invoke Selector.get() method and return default value if is None

        Raises:
            TypeError: if passed default and key arguments
        """
        return self.add_method("get", default)  # type: ignore

    def getall(self) -> SpecialMethodsProtocol:
        """Call the .get() method for each element is this list
        and return their results flattened, as a list of strings.

        Returns:
            list[str]
        """

        return self.add_method("getall")  # type: ignore


class Text(Field):
    """This field provide special methods for raw text data (regex only)"""

    def __init__(
        self, auto_type: bool = True, default: Any = ..., alias: Optional[str] = None
    ):
        """this field provide special methods API

        Args:
            auto_type: usage auto type feature in BaseSchema scope. Default True
            default: set default value, if method return traceback.
            alias: field alias. default None
        """
        super().__init__(auto_type=auto_type, default=default, alias=alias)
        # prepare get raw text
        self.add_method("xpath", "//body/p/text()")
        self.add_method("get")


class Callback(Field):
    """This field provide callback functions. SpecialMethods support too

    Useful for auto enumerate, set UUID, etc.
    """

    def __init__(
        self,
        callback: Callable[[], Any],
        auto_type=False,
        default: Any = ...,
        alias: Optional[str] = None,
    ):
        """This field provide callback functions

        Args:
            callback: callback function. function should be not accept any arguments
            auto_type: usage auto type feature in BaseSchema scope. Default False
            default: set default value, if method return traceback.
            alias: field alias. default None
        """
        super().__init__(auto_type=auto_type, default=default, alias=alias)
        self.callback = callback

    def sc_parse(self, _) -> Any:
        return self._call_stack_methods(self.callback())


class RawDLField(Field):
    """Field for parse Description List element <dl>, <dt> <dd>:

    See Also:
        https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dl
    """

    def __init__(
        self, auto_type=False, default: Any = ..., alias: Optional[str] = None
    ):
        super().__init__(auto_type=auto_type, default=default, alias=alias)

    def css_dl(
        self,
        dl_css: str = "dl",
        dt_css: str = "dt",
        dd_css: str = "dd",
        *,
        str_join: Optional[str] = None,
        strip: bool = False,
        re_sub_pattern: Optional[Union[str, Pattern]] = None,
        re_sub_count: int = 100,
    ) -> SpecialMethodsProtocol:
        """

        Args:
            dl_css: dl css selector
            dt_css: dt css selector
            dd_css: dd css selector
            str_join: join text result from dd elements? default set value as list
            strip: strip text? default False
            re_sub_pattern: re.sub regular expr. If argument None - skip
            re_sub_count: re.sub subs count
        Returns:
            dict[<dt ::text key> : <dd ::text value>, ...]
        """

        def __parse_dl_raw(markup: Union["Selector", "SelectorList"]):
            table = {}
            dl = markup.css(dl_css)
            if not bool(dl):
                msg = f"This markup not contains dataline element from `{dt_css}` selector"
                raise TypeError(msg)

            for dt, dd in zip(dl.css(dt_css), dl.css(dd_css)):
                key = dt.css("::text").get().strip()
                if re_sub_pattern:
                    key = re.sub(re_sub_pattern, "", key, count=re_sub_count)
                key = key.strip() if strip else key
                values = [v.strip() if strip else v for v in dd.css("::text").getall()]

                if re_sub_pattern:
                    values = [re.sub(re_sub_pattern, "", v) for v in values]

                if isinstance(str_join, str):
                    values = str_join.join(values)  # type: ignore
                table[key] = values
            return table

        return self.add_method(SpecialMethods.FN, function=__parse_dl_raw)  # type: ignore


class RawTableField(Field):
    """Field for parse <table> <tbody> HTML constructions:

    See Also:
        https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table
        https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tbody
    """

    def __init__(
        self,
        auto_type=False,
        default: Any = ...,
        alias: Optional[str] = None,
    ):
        super().__init__(auto_type=auto_type, alias=alias, default=default)

    def table(self, table_css: str = "table"):
        """Parse table element.

        return python dict in {"columns": List[str], # list all <th> values elements,
        "cells": List[list[str]],  # 2-dimensional list with all <td> values (len calculate by "columns" len and fill
            missing attributes by None
        "table": dict{str: List[str],  # try to represent in dict(<th>: list[<td>], ...) format
        }

        Args:
            table_css: table or tbody css target element

        Returns:
            TableDictView dict with all columns, cells and try to represent as dict

        """

        def __parse_table(markup) -> TableDictView:
            table = markup.css(table_css)
            if not bool(table):
                msg = f"This markup not contains table element from `{table_css}` selector"
                raise TypeError(msg)

            all_columns: List[str] = []
            all_cells: List[List[str]] = []
            data: Dict[str, List[Optional[str]]] = {}

            for tr in table.css("tr"):
                for col in tr.css("th"):
                    if column_item := col.css("::text").getall():
                        column_item = " ".join([cell.strip() for cell in column_item])
                        all_columns.append(column_item)
                rows = []
                for row in tr.css("td"):
                    if cell_item := row.css("::text").getall():
                        cell_item = " ".join([cell.strip() for cell in cell_item])
                        rows.append(cell_item)
                if rows:
                    all_cells.append(rows)
            for i, column in enumerate(all_columns):
                data[column] = [row[i] if i < len(row) else None for row in all_cells]

            return TableDictView(columns=all_columns, cells=all_cells, table=data)

        return self.add_method(SpecialMethods.FN, function=__parse_table)


class DictField(Field):
    def __init__(
        self, auto_type=False, default: Any = ..., alias: Optional[str] = None, **kwargs
    ):
        super().__init__(auto_type=auto_type, default=default, alias=alias, **kwargs)

    def dict(
        self,
        keys_field: Union["Field", "SpecialMethodsProtocol"],
        keys_values: Union["Field", "SpecialMethodsProtocol"],
    ) -> Self:
        """Alias of `dict(zip(keys_fields: keys_values))` construction. All fields should be return iterator object.

        Create dict by two Parsel fields arguments.
        """

        def __create_dict(markup):
            return dict(zip(keys_field.sc_parse(markup), keys_values.sc_parse(markup)))  # type: ignore

        return self.add_method(SpecialMethods.FN, __create_dict)

    def dict_one(
        self,
        key_field: Union["Parsel", "SpecialMethodsProtocol"],
        key_value: Union["Parsel", "SpecialMethodsProtocol"],
    ):
        """Alias of `dict(keys_field: key_value))` construction. key_field should be return `Hashable` object.

        Create dict by two Parsel fields arguments.
        """

        def __create_dict(markup):
            key = key_field.sc_parse(markup)
            if not isinstance(key, Hashable):
                msg = f"key_field is not hashable, got `{key}`"
                raise TypeError(msg)
            return {key: key_value.sc_parse(markup)}  # type: ignore

        return self.add_method(SpecialMethods.FN, __create_dict)
