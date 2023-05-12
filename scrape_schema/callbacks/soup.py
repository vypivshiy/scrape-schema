"""build-in callbacks for fields.soup"""
import re
from typing import Any, Callable, Dict, List, Optional, Union

from bs4 import BeautifulSoup, Tag

RE_TAG_NAME = re.compile(r"<(\w+)")
RE_TAG_ATTRS = re.compile(r'(?P<name>[\w_\-:.]+)="(?P<value>[\w_\-:.\s]+)"')

__all__ = [
    "get_attr",
    "get_text",
    "replace_text",
    "crop_by_tag",
    "crop_by_tag_all",
    "crop_by_selector",
    "crop_by_selector_all",
    "element_to_dict",
]


def replace_text(
    old: str, new: str, count: int = -1, *, separator: str = "", strip: bool = False
) -> Callable[[Union[Tag, Any]], Union[str, Any]]:
    def wrapper(tag: Union[Tag, Any]) -> Union[str, Any]:
        if isinstance(tag, Tag):
            return tag.get_text(separator=separator, strip=strip).replace(
                old, new, count
            )
        return tag

    return wrapper


def element_to_dict(
    element: str,
) -> Dict[str, Union[str, Dict[str, Union[Union[str, List[str]]]]]]:
    """Convert string element to dict

    Example:
        <p> -> {"name": "p", "attrs":{}}
        <a id="1", class="thing"> -> {"name": "a", "attrs": {"id": "1", "class": "thing"}}
    """
    if not (match := RE_TAG_NAME.search(element)):
        raise TypeError(f"Element `{element}` is not valid HTML tag")
    tag_name = match.group(1)
    attrs = dict(RE_TAG_ATTRS.findall(element))
    if (klass := attrs.get("class")) and len(klass.split(" ")) != 1:
        attrs["class"] = klass.split()
    return {"name": tag_name, "attrs": attrs}


def get_text(
    separator: str = "", strip: bool = False
) -> Callable[[Union[Tag, Any]], Union[str, Any]]:
    """get text from bs4.Tag

    :param separator: separator. default ""
    :param strip: strip flag. default False
    :return:
    """

    def wrapper(tag: Union[Tag, Any]) -> Union[str, Any]:
        if isinstance(tag, Tag):
            return tag.get_text(separator=separator, strip=strip)
        return tag

    return wrapper


def get_attr(
    tag_name: str, default: Any = ...
) -> Callable[[Union[Tag, Any]], Union[str, Any]]:
    """get tag from element

    :param tag_name: tag name
    :param default: default value, if attr not founded
    :return:
    """

    def wrapper(tag: Union[Tag, Any]) -> Union[str, Any]:
        if isinstance(tag, Tag):
            if default == Ellipsis:
                return tag.get(tag_name)
            return tag.get(tag_name, default=default)
        return tag

    return wrapper


def crop_by_tag_all(
    element: Union[str, Dict[str, Any]], features: str = "html.parser", **soup_config
) -> Callable[[str], List[str]]:
    """crop markup document to string chunks by soup element

    :param element: html element or any dict of kwargs for soup.find_all method
    :param features: BeautifulSoup parser. default `html.parser`
    :param soup_config: any BeautifulSoup kwargs config
    """
    if isinstance(element, str):
        element = element_to_dict(element)

    def wrapper(markup: Union[str, BeautifulSoup]) -> List[str]:
        if isinstance(markup, BeautifulSoup):
            return [str(tag) for tag in markup.find_all(**element)]
        soup = BeautifulSoup(markup, features=features, **soup_config)
        return [str(tag) for tag in soup.find_all(**element)]

    return wrapper


def crop_by_tag(
    element: Union[str, Dict[str, Any]], features: str = "html.parser", **soup_config
) -> Callable[[str], str]:
    """crop markup document to string chunk by soup element

    :param element: html element or any dict of kwargs for soup.find method
    :param features: BeautifulSoup parser. default `html.parser`
    :param soup_config: any BeautifulSoup kwargs config
    """
    if isinstance(element, str):
        element = element_to_dict(element)

    def wrapper(markup: Union[str, BeautifulSoup]) -> str:
        if isinstance(markup, BeautifulSoup):
            return str(markup.find(**element))
        soup = BeautifulSoup(markup, features=features, **soup_config)
        return str(soup.find(**element))

    return wrapper


def crop_by_selector(
    selector: str,
    namespaces: Optional[Dict[str, Any]] = None,
    features: str = "html.parser",
    **soup_config,
) -> Callable[[str], str]:
    """crop markup document to string chunk by soup selector

    :param selector: css selector for soup.select_one method
    :param namespaces: A dictionary mapping namespace prefixes used
    in the CSS selector to namespace URIs. By default,
    Beautiful Soup will use the prefixes it encountered while parsing the document.
    :param features: BeautifulSoup parser. default `html.parser`
    :param soup_config: any BeautifulSoup kwargs config
    """

    def wrapper(markup: str) -> str:
        soup = BeautifulSoup(markup, features=features, **soup_config)
        return str(soup.select_one(selector, namespaces))

    return wrapper


def crop_by_selector_all(
    selector: str,
    namespaces: Optional[Dict[str, Any]] = None,
    features: str = "html.parser",
    **soup_config,
) -> Callable[[str], List[str]]:
    """crop markup document to string chunks by soup selector

    :param selector: css selector for soup.select method
    :param namespaces: A dictionary mapping namespace prefixes used
    in the CSS selector to namespace URIs. By default,
    Beautiful Soup will use the prefixes it encountered while parsing the document.
    :param features: BeautifulSoup parser. default `html.parser`
    :param soup_config: any BeautifulSoup kwargs config
    """

    def wrapper(markup: Union[str, BeautifulSoup]) -> List[str]:
        if isinstance(markup, BeautifulSoup):
            return [str(tag) for tag in markup.select(selector, namespaces)]
        soup = BeautifulSoup(markup, features=features, **soup_config)
        return [str(tag) for tag in soup.select(selector, namespaces)]

    return wrapper
