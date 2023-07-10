from typing import Any, Hashable, Mapping, Optional, Pattern, Union

from parsel import Selector

from scrape_schema._logger import _logger
from scrape_schema._typing import Self
from scrape_schema.base import Field
from scrape_schema.field_protocols import AttribProtocol, SpecialMethodsProtocol


class Parsel(Field):
    def __init__(
        self, auto_type: bool = True, default: Any = ..., *, raw: bool = False
    ):
        super().__init__(auto_type=auto_type, default=default)
        if raw:
            self.xpath("//p/text()").get()

    def css(self, query: str) -> Self:
        """Apply the given CSS selector and return a SelectorList instance.

        query is a string containing the CSS selector to apply.

        In the background, CSS queries are translated into XPath queries using cssselect  library and run .xpath() method.
        """
        return self.add_method("css", query)

    @property
    def raw_text(self) -> SpecialMethodsProtocol:
        """Shortcut `Parsel().xpath('//p/text()')` call.

        This method for getting raw text (not html), when calling `parsel.Selector` methods will raise an error
        """
        # Parsel is not meant for raw text: it will try to "fix" html and parse as html usage `raw_text` property
        # or `xpath(//p/text()).get()` or raw=True in init constructor
        return self.xpath("//p/text()").get()

    def xpath(
        self, query: str, namespaces: Optional[Mapping[str, str]] = None, **kwargs: Any
    ) -> Self:
        """
        Find nodes matching the xpath ``query`` and return the result as a
        :class:`SelectorList` instance with all elements flattened. List
        elements implement :class:`Selector` interface too.

        ``query`` is a string containing the XPATH query to apply.

        ``namespaces`` is an optional ``prefix: namespace-uri`` mapping (dict)
        for additional prefixes to those registered with ``register_namespace(prefix, uri)``.
        Contrary to ``register_namespace()``, these prefixes are not
        saved for future calls.

        Any additional named arguments can be used to pass values for XPath
        variables in the XPath expression, e.g.::

            selector.xpath('//a[href=$url]', url="http://www.example.com")
        """

        return self.add_method("xpath", query, namespaces, **kwargs)

    def re(
        self, regex: Union[str, Pattern[str]], replace_entities: bool = True
    ) -> SpecialMethodsProtocol:
        """
        Apply the given regex and return a list of strings with the
        matches.

        ``regex`` can be either a compiled regular expression or a string which
        will be compiled to a regular expression using ``re.compile(regex)``.

        By default, character entity references are replaced by their
        corresponding character (except for ``&amp;`` and ``&lt;``).
        Passing ``replace_entities`` as ``False`` switches off these
        replacements.
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
        """
        Serialize and return the matched nodes in a single string. Percent encoded content is unquoted.

        If `key` param passed - get value from attrib property. attrib should be called in chain methods
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
        """
        Find objects matching the JMESPath ``query`` and return the result as a
        :class:`SelectorList` instance with all elements flattened. List
        elements implement :class:`Selector` interface too.

        ``query`` is a string containing the `JMESPath
        <https://jmespath.org/>`_ query to apply.

        Any additional named arguments are passed to the underlying
        ``jmespath.search`` call, e.g.::

            selector.jmespath('author.name', options=jmespath.Options(dict_cls=collections.OrderedDict))
        """
        return self.add_method("jmespath", query, **kwargs)

    def getall(self) -> SpecialMethodsProtocol:
        """Call the .get() method for each element is this list
        and return their results flattened, as a list of strings."""

        return self.add_method("getall")  # type: ignore

    @property
    def attrib(self) -> AttribProtocol:
        """
        Return the attributes dictionary for the first element.

        If the list is empty, return an empty dict.
        """
        return self.add_method("attrib")  # type: ignore

    def keys(self):
        if self._is_attrib():
            return self.add_method("keys")

    def values(self):
        if self._is_attrib():
            return self.add_method("values")

    def items(self):
        if self._is_attrib():
            return self.add_method("items")
