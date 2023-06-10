from experimental.base import Field, FieldConfig

from bs4 import BeautifulSoup


class Soup(Field):
    class Config(FieldConfig):
        instance = BeautifulSoup
        defaults = {"features": "html.parser"}

    def find(self, name=None, attrs=None, recursive=True, string=None, **kwargs):
        """Look in the children of this PageElement and find the first
               PageElement that matches the given criteria.

               All find_* methods take a common set of arguments. See the online
               documentation for detailed explanations.

               :param name: A filter on tag name.
               :param attrs: A dictionary of filters on attribute values.
               :param recursive: If this is True, find() will perform a
                   recursive search of this PageElement's children. Otherwise,
                   only the direct children will be considered.
               :param limit: Stop looking after finding this many results.
               :kwargs: A dictionary of filters on attribute values.
               :return: A PageElement.
               """
        if attrs is None:
            attrs = {}
        return self.add_method("find", name, attrs=attrs, recursive=recursive, string=string, **kwargs)

    def find_all(self, name=None, attrs=None, recursive=True, string=None, limit=None, **kwargs):
        """Look in the children of this PageElement and find all
                PageElements that match the given criteria.

                All find_* methods take a common set of arguments. See the online
                documentation for detailed explanations.

                :param name: A filter on tag name.
                :param attrs: A dictionary of filters on attribute values.
                :param recursive: If this is True, find_all() will perform a
                    recursive search of this PageElement's children. Otherwise,
                    only the direct children will be considered.
                :param limit: Stop looking after finding this many results.
                :kwargs: A dictionary of filters on attribute values.
                :return: A ResultSet of PageElements.
                """
        if attrs is None:
            attrs = {}
        return self.add_method("find_all", name, attrs=attrs, recursive=recursive, string=string, limit=limit, **kwargs)

    def find_parent(self, name=None, attrs=None, **kwargs):
        """Find the closest parent of this PageElement that matches the given
                criteria.

                All find_* methods take a common set of arguments. See the online
                documentation for detailed explanations.

                :param name: A filter on tag name.
                :param attrs: A dictionary of filters on attribute values.
                :kwargs: A dictionary of filters on attribute values.

                :return: A PageElement.
                """
        if attrs is None:
            attrs = {}
        return self.add_method('find_parent', name, attrs=attrs, **kwargs)

    def find_parents(self, name=None, attrs=None, limit=None, **kwargs):
        """Find all parents of this PageElement that match the given criteria.

               All find_* methods take a common set of arguments. See the online
               documentation for detailed explanations.

               :param name: A filter on tag name.
               :param attrs: A dictionary of filters on attribute values.
               :param limit: Stop looking after finding this many results.
               :kwargs: A dictionary of filters on attribute values.

               :return: A PageElement.
               """
        if not attrs:
            attrs = {}
        return self.add_method('find_parents', name, attrs=attrs, limit=limit, **kwargs)

    def select(self, selector, namespaces=None, limit=None, **kwargs):
        """Perform a CSS selection operation on the current element.

                This uses the SoupSieve library.

                :param selector: A string containing a CSS selector.

                :param namespaces: A dictionary mapping namespace prefixes
                   used in the CSS selector to namespace URIs. By default,
                   Beautiful Soup will use the prefixes it encountered while
                   parsing the document.

                :param limit: After finding this number of results, stop looking.

                :param kwargs: Keyword arguments to be passed into SoupSieve's
                   soupsieve.select() method.

                :return: A ResultSet of Tags.
                """
        return self.add_method('select', selector, namespaces=namespaces, limit=limit, **kwargs)

    def select_one(self,  selector, namespaces=None, **kwargs):
        """Perform a CSS selection operation on the current element.

                :param selector: A CSS selector.

                :param namespaces: A dictionary mapping namespace prefixes
                   used in the CSS selector to namespace URIs. By default,
                   Beautiful Soup will use the prefixes it encountered while
                   parsing the document.

                :param kwargs: Keyword arguments to be passed into Soup Sieve's
                   soupsieve.select() method.

                :return: A Tag.
                """
        return self.add_method('select_one', selector, namespaces=namespaces, **kwargs)

    def get(self, key: str, default=None):
        """Returns the value of the 'key' attribute for the tag, or
                the value given for 'default' if it doesn't have that
                attribute."""
        return self.add_method('get', key=key, default=default)

    def get_text(self, separator="", strip=False):
        """Get all child strings of this PageElement, concatenated using the
        given separator.

        :param separator: Strings will be concatenated using this separator.

        :param strip: If True, strings will be stripped before being
            concatenated.

        :param types: A tuple of NavigableString subclasses. Any
            strings of a subclass not found in this list will be
            ignored. Although there are exceptions, the default
            behavior in most cases is to consider only NavigableString
            and CData objects. That means no comments, processing
            instructions, etc.

        :return: A string.
        """
        return self.add_method('get_text', separator=separator, strip=strip)

    def html(self):
        """Get raw html string"""
        return self.add_method("__str__")


if __name__ == '__main__':
    from experimental.base import BaseSchema, field_param
    from typing import Annotated

    class Schema(BaseSchema):
        class Config:
            parsers = {BeautifulSoup: {"features": 'html.parser'}}

        # title: Annotated[str, Soup().find("title").get_text()]
        # href: Annotated[str, Soup().find("div").find("a").get('href')]
        # a_text: Annotated[float, Soup().find("a").get_text()]
        a_tags: Annotated[list[str], Soup(cast_type=False).find_all("a").html()]
        _title: Annotated[str, Soup().find('title').get_text()]

        @field_param
        def hrefs(self):
            return [tag.split('href="')[1].split('">')[0] for tag in self.a_tags]

        @field_param
        def title(self):
            return self._title.upper().strip('"')

        @property
        def spam(self):
            return "spam"


    sc = Schema('<title>"test title"</title>\n<div><a href="example.com">123</a><\div>\n<a href="go.gle">spam</a>')
    print(sc.dict())
