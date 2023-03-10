"""build-in callbacks for soup"""

from typing import Any, Callable, Optional


from bs4 import BeautifulSoup, Tag


__all__ = [
    "get_tag",
    "get_text",
    "crop_by_tag",
    "crop_by_tag_all",
    "crop_by_selector",
    "crop_by_selector_all"
]


def get_text(separator: str = "", strip: bool = False) -> Callable[[Tag], Any]:
    def wrapper(tag: Tag):
        if isinstance(tag, Tag):
            return tag.get_text(separator=separator, strip=strip)
        return tag
    return wrapper


def get_tag(tag_name: str, default: Any = ...) -> Callable[[Tag], Any]:
    def wrapper(tag: Tag):
        if isinstance(tag, Tag):
            if default == Ellipsis:
                return tag.get(tag_name)
            return tag.get(tag_name, default=default)
        return tag
    return wrapper


# TODO convert string to dict
def crop_by_tag_all(element: dict[str, Any], **soup_config) -> Callable[[str], list[str]]:
    def wrapper(markup: str) -> list[str]:
        soup = BeautifulSoup(markup, **soup_config)
        return [str(tag) for tag in soup.find_all(**element)]
    return wrapper


def crop_by_tag(element: dict[str, Any], **soup_config) -> Callable[[str], str]:
    def wrapper(markup: str) -> str:
        soup = BeautifulSoup(markup, **soup_config)
        return str(soup.find_all(**element))
    return wrapper


def crop_by_selector(selector: str,
                     namespaces: Optional[dict[str, Any]] = None,
                     **soup_config) -> Callable[[str], str]:
    def wrapper(markup: str) -> str:
        soup = BeautifulSoup(markup, **soup_config)
        return str(soup.select_one(selector, namespaces))
    return wrapper


def crop_by_selector_all(selector: str,
                         namespaces: Optional[dict[str, Any]] = None,
                         **soup_config) -> Callable[[str], list[str]]:
    def wrapper(markup: str) -> list[str]:
        soup = BeautifulSoup(markup, **soup_config)
        return [str(tag) for tag in soup.select(selector, namespaces)]
    return wrapper
