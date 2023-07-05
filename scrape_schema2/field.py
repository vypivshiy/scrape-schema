from typing import Any, Hashable, Mapping, Optional, Pattern, Union, overload

from parsel import Selector
from scrape_schema2.base import Field, FieldConfig
from scrape_schema2._typing import Self


class Parsel(Field):
    class Config(FieldConfig):
        instance = Selector

    def css(self, query: str):
        """Apply the given CSS selector and return a SelectorList instance.

        query is a string containing the CSS selector to apply.

        In the background, CSS queries are translated into XPath queries using cssselect  library and run .xpath() method.
        """
        return self.add_method("css", query)

    def xpath(
        self, query: str, namespaces: Optional[Mapping[str, str]] = None, **kwargs: Any
    ):
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
        return self.add_method("xpath", query=query, namespaces=namespaces, **kwargs)

    def re(self, regex: Union[str, Pattern[str]], replace_entities: bool = True):
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
        return self.add_method("re", regex=regex, replace_entities=replace_entities)

    def _is_attrib(self):
        if (method := self._stack_methods[-1].METHOD_NAME) != "attrib":
            raise TypeError(f"Last method should be `attrib`, not `{method}`")
        return True

    @overload
    def get(self, default: Optional[str] = None) -> Self:
        pass

    @overload
    def get(self, key: Hashable) -> Self:
        pass

    def get(self, default: Optional[str] = None, key: Optional[Hashable] = None) -> Self:  # type: ignore
        """
        Serialize and return the matched nodes in a single string. Percent encoded content is unquoted.

        If `key` param passed - get value from attrib property. attrib should be called in chain methods
        """
        if key and default:
            raise TypeError("__key param should be call after `attrib` property")
        elif key:
            if self._is_attrib():
                return self.add_method("get", key)
        return self.add_method("get", default)

    def jmespath(self, query: str, **kwargs: Any):
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

    def getall(self):
        """Call the .get() method for each element is this list
        and return their results flattened, as a list of strings."""

        return self.add_method("getall")

    @property
    def attrib(self):
        """
        Return the attributes dictionary for the first element.

        If the list is empty, return an empty dict.
        """
        return self.add_method("attrib")

    def keys(self):
        if self._is_attrib():
            return self.add_method("keys")

    def values(self):
        if self._is_attrib():
            return self.add_method("values")

    def items(self):
        if self._is_attrib():
            return self.add_method("items")