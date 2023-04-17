from typing import Optional, Any, Callable

from selectolax.parser import HTMLParser, Node

__all__ = ["crop_by_slax", "crop_by_slax_all", "get_attr", "get_text", "replace_text"]


def crop_by_slax(query: str, **slax_config):
    """crop markup document to string chunk by selectolax selector

    :param query: css path
    :param slax_config: any selectolax.parser.HTMLParser kwargs
    """

    def wrapper(markup: str) -> str:
        parser = HTMLParser(markup, **slax_config)
        return parser.css_first(query).html

    return wrapper


def crop_by_slax_all(query: str, **slax_config):
    """crop markup document to string chunks by selectolax selector

    :param query: css path
    :param slax_config: any selectolax.parser.HTMLParser kwargs
    """

    def wrapper(markup: str) -> list[str]:
        parser = HTMLParser(markup, **slax_config)
        return [m.html for m in parser.css(query)]

    return wrapper


def get_attr(name: str, default: Optional[Any] = None):
    """get tag from Node object

    :param name: tag name
    :param default: default value, if tag is not founded. default None
    """

    def wrapper(node: Node | Any) -> str:
        if isinstance(node, Node):
            return node.attrs.get(name, default=default)
        return node

    return wrapper


def replace_text(
    old: str,
    new: str,
    count: int = -1,
    *,
    deep: bool = True,
    separator: str = "",
    strip: bool = False,
):
    def wrapper(element: Node):
        if isinstance(element, Node):
            return element.text(deep=deep, separator=separator, strip=strip).replace(
                old, new, count
            )
        return element

    return wrapper


def get_text(
    deep: bool = True, separator: str = "", strip: bool = False
) -> Callable[[Node], str]:
    """get text from Node object

    :param deep: If True, includes text from all child nodes.
    :param separator: The separator to use when joining text from different nodes.
    :param strip: If true, calls str.strip() on each text part to remove extra white spaces.
    """

    def wrapper(element: Node):
        if isinstance(element, Node):
            return element.text(deep=deep, separator=separator, strip=strip)
        return element

    return wrapper
