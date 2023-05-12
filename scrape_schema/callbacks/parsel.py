"""Callbacks for scrape_schema.fields.parsel"""
from typing import Any, Callable, List, Mapping, Optional, Union

from parsel import Selector, SelectorList
from parsel.selector import _NOT_SET, LXML_SUPPORTS_HUGE_TREE, _SelectorType


def get_text(
    default: Optional[str] = None,
    strip: bool = False,
    deep: bool = False,
    sep: str = "",
) -> Callable[[Union[SelectorList[_SelectorType], Any]], Union[Optional[str], Any]]:
    def wrapper(
        element: Union[SelectorList[_SelectorType], Any]
    ) -> Union[Optional[str], Any]:
        if isinstance(element, (SelectorList, Selector)):
            if deep:
                text = sep.join(element.css("::text").getall())
            else:
                text = element.css("::text").get(default=default)  # type: ignore
            if text:
                return text.strip() if strip else text
            return text
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
    def wrapper(markup: Union[str, Selector]) -> str:
        if isinstance(markup, Selector):
            return markup.css(query).get() or ""
        elif (
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
            "Failed crop part from markup, check params or markup attributes"
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
    def wrapper(markup: Union[str, Selector]) -> List[str]:
        if isinstance(markup, Selector):
            return markup.css(query).getall()
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
    def wrapper(markup: Union[str, Selector]) -> str:
        if isinstance(markup, Selector):
            return (
                markup.xpath(
                    query=query, namespaces=xpath_namespaces, **xpath_kwargs
                ).get()
                or ""
            )
        elif (
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
    def wrapper(markup: Union[str, Selector]) -> List[str]:
        if isinstance(markup, Selector):
            return markup.xpath(
                query=query, namespaces=namespaces, **xpath_kwargs
            ).getall()
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
