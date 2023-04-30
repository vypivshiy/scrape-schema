from typing import Any, Callable, List, Mapping, Optional, Union

from parsel import Selector, SelectorList
from parsel.selector import _NOT_SET, LXML_SUPPORTS_HUGE_TREE, _SelectorType


def get_text(
    default: Optional[str] = None,
) -> Callable[[Union[SelectorList[_SelectorType], Any]], Union[Optional[str], Any]]:
    def wrapper(
        element: Union[SelectorList[_SelectorType], Any]
    ) -> Union[Optional[str], Any]:
        if isinstance(element, (SelectorList, Selector)):
            return element.css("::text").get(default=default)
        return element

    return wrapper


def replace_text(
    __old: str, __new: str, __count: int = -1, *, default: Optional[str] = None
) -> Callable[[Union[SelectorList[_SelectorType], Any]], Optional[Optional[str]]]:
    def wrapper(element: Union[SelectorList[_SelectorType], Any]) -> Union[str, Any]:
        if isinstance(element, (SelectorList, Selector)):
            if text := element.css("::text").get(default=default):
                return text.replace(__old, __new, __count)
        return element

    return wrapper


def get_attr(attr: str):
    def wrapper(
        element: Union[SelectorList[_SelectorType], Any]
    ) -> Union[Optional[str], Any]:
        if isinstance(element, (SelectorList, Selector)):
            return el_attr if (el_attr := element.attrib.get(attr)) else element
        return element

    return wrapper


def crop_by_selector(
    query: str,
    *,
    type: Optional[str] = None,
    body: bytes = b"",
    encoding: str = "utf8",
    namespaces: Optional[Mapping[str, str]] = None,
    root: Optional[Any] = _NOT_SET,
    base_url: Optional[str] = None,
    _expr: Optional[str] = None,
    huge_tree: bool = LXML_SUPPORTS_HUGE_TREE,
):
    def wrapper(markup: str) -> str:
        if (
            markup_part := Selector(
                text=markup,
                type=type,
                body=body,
                encoding=encoding,
                namespaces=namespaces,
                root=root,
                base_url=base_url,
                huge_tree=huge_tree,
            )
            .css(query)
            .get()
        ):
            return markup_part
        raise AttributeError(
            "Failed crop part from markup, check params or markup attribute"
        )

    return wrapper


def crop_by_selector_all(
    query: str,
    *,
    type: Optional[str] = None,
    body: bytes = b"",
    encoding: str = "utf8",
    namespaces: Optional[Mapping[str, str]] = None,
    root: Optional[Any] = _NOT_SET,
    base_url: Optional[str] = None,
    _expr: Optional[str] = None,
    huge_tree: bool = LXML_SUPPORTS_HUGE_TREE,
):
    def wrapper(markup: str) -> List[str]:
        return (
            Selector(
                text=markup,
                type=type,
                body=body,
                encoding=encoding,
                namespaces=namespaces,
                root=root,
                base_url=base_url,
                huge_tree=huge_tree,
            )
            .css(query)
            .getall()
        )

    return wrapper


def crop_by_xpath(
    query: str,
    xpath_namespaces: Optional[Mapping[str, str]] = None,
    *,
    type: Optional[str] = None,
    body: bytes = b"",
    encoding: str = "utf8",
    namespaces: Optional[Mapping[str, str]] = None,
    root: Optional[Any] = _NOT_SET,
    base_url: Optional[str] = None,
    _expr: Optional[str] = None,
    huge_tree: bool = LXML_SUPPORTS_HUGE_TREE,
    **xpath_kwargs,
):
    def wrapper(markup: str) -> str:
        if (
            markup_part := Selector(
                text=markup,
                type=type,
                body=body,
                encoding=encoding,
                namespaces=namespaces,
                root=root,
                base_url=base_url,
                huge_tree=huge_tree,
            )
            .xpath(query=query, namespaces=xpath_namespaces, **xpath_kwargs)
            .get()
        ):
            return markup_part
        raise AttributeError(
            "Failed crop part from markup, check params or markup attribute"
        )

    return wrapper


def crop_by_xpath_all(
    query: str,
    xpath_namespaces: Optional[Mapping[str, str]] = None,
    *,
    type: Optional[str] = None,
    body: bytes = b"",
    encoding: str = "utf8",
    namespaces: Optional[Mapping[str, str]] = None,
    root: Optional[Any] = _NOT_SET,
    base_url: Optional[str] = None,
    _expr: Optional[str] = None,
    huge_tree: bool = LXML_SUPPORTS_HUGE_TREE,
    **xpath_kwargs,
):
    def wrapper(markup: str) -> List[str]:
        return (
            Selector(
                text=markup,
                type=type,
                body=body,
                encoding=encoding,
                namespaces=namespaces,
                root=root,
                base_url=base_url,
                huge_tree=huge_tree,
            )
            .xpath(query=query, namespaces=xpath_namespaces, **xpath_kwargs)
            .getall()
        )

    return wrapper
