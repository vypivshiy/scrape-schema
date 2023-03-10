from typing import Optional, Any, Callable

from selectolax.parser import HTMLParser, Node


def crop_by_slax(query: str, **slax_config):
    def wrapper(markup: str) -> str:
        markup = HTMLParser(markup, **slax_config)
        return markup.css_first(query).html

    return wrapper


def crop_by_slax_all(query: str, **slax_config):
    def wrapper(markup: str) -> list[str]:
        markup = HTMLParser(markup)
        return [m.html for m in markup.css(query)]

    return wrapper


def get_tag(name: str, default: Optional[Any] = None):
    def wrapper(node: Node) -> str:
        if isinstance(node, Node):
            return node.attrs.get(name, default=default)
        return node  # type: ignore

    return wrapper


def get_text(deep: bool = True,
             separator: str = "",
             strip: bool = False) -> Callable[[Node], str]:
    def wrapper(element: Node):
        if isinstance(element, Node):
            return element.text(deep=deep, separator=separator, strip=strip)
        return element

    return wrapper
