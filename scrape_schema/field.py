from typing import Any, Hashable, Mapping, Optional, Pattern, Union

from scrape_schema._logger import _logger
from scrape_schema._protocols import AttribProtocol, SpecialMethodsProtocol
from scrape_schema._typing import Self
from scrape_schema.base import Field


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
        return self.add_method("re", regex=regex, replace_entities=replace_entities)  # type: ignore

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
