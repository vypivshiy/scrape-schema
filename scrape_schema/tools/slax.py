from typing import Optional, Any

from selectolax.parser import HTMLParser, Node


def crop_by_slax(query: str):
    def wrapper(markup: HTMLParser) -> str:
        return markup.css_first(query).html
    return wrapper


def crop_by_slax_all(query: str):
    def wrapper(markup: str) -> list[str]:
        markup = HTMLParser(markup)
        return [m.html for m in markup.css(query)]
    return wrapper


def get_tag(name: str, default: Optional[Any] = None):
    def wrapper(node: Node) -> str:
        return node.attrs.get(name, default=default)
    return wrapper
