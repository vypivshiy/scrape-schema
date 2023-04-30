from typing import List, Optional

import pytest
from parsel import Selector
from tests.fixtures import HTML

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.callbacks.parsel import (
    crop_by_selector,
    crop_by_selector_all,
    crop_by_xpath,
    crop_by_xpath_all,
    get_attr,
)
from scrape_schema.fields.parsel import (
    ParselSelect,
    ParselSelectList,
    ParselXPath,
    ParselXPathList,
)


class ParselSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {Selector: {}}

    lang: ScField[str, ParselSelect("html", callback=get_attr("lang"))]
    charset: ScField[
        str,
        ParselSelect(
            "meta", callback=get_attr("charset"), factory=lambda s: s.replace("-", "")
        ),
    ]
    title: ScField[str, ParselXPath("//title")]
    title_lower: ScField[
        str, ParselSelect("head > title", factory=lambda text: text.lower())
    ]
    body_string: ScField[str, ParselSelect("p.body-string")]
    body_string_chars: ScField[List[str], ParselSelect("p.body-string", factory=list)]
    body_string_flag: ScField[bool, ParselSelect("body > p.body-string")]
    body_int: ScField[int, ParselSelect("p.body-int")]
    body_float: ScField[float, ParselXPath('//body/p[@class="body-int"]')]
    body_int_x10: ScField[
        int, ParselXPath('//body/p[@class="body-int"]', factory=lambda el: int(el) * 10)
    ]

    fail_value_1: ScField[Optional[str], ParselSelect("spam")]
    fail_value_2: ScField[bool, ParselXPath("//spam/egg")]
    fail_value_3: ScField[str, ParselSelect("body > spam.egg", default="spam")]

    # SoupList
    body_int_list: ScField[List[int], ParselXPathList('//body/a[@class="body-list"]')]
    body_float_list: ScField[List[float], ParselSelectList("body > a.body-list")]
    max_body_list: ScField[
        int,
        ParselXPathList(
            '//a[@class="body-list"]',
            factory=lambda els: max(int(i) for i in els),
        ),
    ]
    body_float_flag: ScField[bool, ParselSelectList("body > a.body-list")]

    fail_list_1: ScField[Optional[List[int]], ParselXPathList("//spam")]
    fail_list_2: ScField[bool, ParselSelectList("body > spam.egg")]
    fail_list_3: ScField[
        List[str], ParselXPathList('//spam[@class="egg"]', default=["spam", "egg"])
    ]


PARSEL_SCHEMA = ParselSchema(HTML)


@pytest.mark.parametrize(
    "field, html, result",
    [
        (ParselSelect("div > a"), "<div><a>test</a></div>", "test"),
        (ParselSelect("div > a", factory=int), "<div><a>1</a></div>", 1),
        (ParselSelect("div > a", factory=float), "<div><a>1.5</a></div>", 1.5),
        (
            ParselSelect("div > a", callback=get_attr("href")),
            '<div><a href="example.com"></a></div>',
            "example.com",
        ),
        (
            ParselSelectList("div > a"),
            "<div><a>test1</a></div>\n<div><a>test2</a></div>",
            ["test1", "test2"],
        ),
        (
            ParselSelectList(
                "div > a", filter_=lambda sel: sel.css("::text").get().endswith("2")
            ),  # type: ignore
            "<div><a>test1</a></div>\n<div><a>test2</a></div>",
            ["test2"],
        ),
        (
            ParselSelectList("div > a", callback=get_attr("href")),
            '<div><a href="1">test1</a></div>\n<div><a href="2">test2</a></div>',
            ["1", "2"],
        ),
        (
            ParselSelectList(
                "div > a",
                callback=get_attr("href"),
                factory=lambda lst: [int(i) for i in lst],
            ),
            '<div><a href="1">test1</a></div>\n<div><a href="2">test2</a></div>',
            [1, 2],
        ),
    ],
)
def test_extract_single_select_field(field, html, result):
    assert field.extract(Selector(text=html)) == result


@pytest.mark.parametrize(
    "field,html,result",
    [
        (ParselXPath("//a"), "<div><a>test</a></div>", "test"),
        (ParselXPath("//a", factory=int), "<div><a>1</a></div>", 1),
        (
            ParselXPath("//div/a", callback=get_attr("href")),
            '<div><a href="1"></a></div>',
            "1",
        ),
        (
            ParselXPath("//div/a", callback=get_attr("href"), factory=int),
            '<div><a href="1"></a></div>',
            1,
        ),
        (
            ParselXPathList("//div/a"),
            '"<div><a>test1</a></div>\n<div><a>test2</a></div>"',
            ["test1", "test2"],
        ),
        (
            ParselXPathList("//div/a", filter_=lambda p: p.css("::text").get().endswith("2")),  # type: ignore
            '"<div><a>test1</a></div>\n<div><a>test2</a></div>"',
            ["test2"],
        ),
        (
            ParselXPathList("//div/a", callback=get_attr("href")),
            '<div><a href="1">test1</a></div>\n<div><a href="2">test2</a></div>',
            ["1", "2"],
        ),
        (
            ParselXPathList(
                "//div/a",
                callback=get_attr("href"),
                factory=lambda lst: [int(i) for i in lst],
            ),
            '<div><a href="1">test1</a></div>\n<div><a href="2">test2</a></div>',
            [1, 2],
        ),
    ],
)
def test_extract_single_xpath_field(field, html, result):
    assert field.extract(Selector(text=html)) == result


def test_crop_by_selector():
    markup = "<div><p>Hello, World!</p></div>"
    assert crop_by_selector("p")(markup) == "<p>Hello, World!</p>"


def test_crop_by_selector_all():
    markup = "<ul><li>One</li><li>Two</li><li>Three</li></ul>"
    assert crop_by_selector_all("li")(markup) == [
        "<li>One</li>",
        "<li>Two</li>",
        "<li>Three</li>",
    ]


def test_crop_by_xpath():
    markup = "<div><p>Hello, World!</p></div>"
    assert crop_by_xpath("//p")(markup) == "<p>Hello, World!</p>"


def test_crop_by_xpath_all():
    markup = "<ul><li>One</li><li>Two</li><li>Three</li></ul>"
    assert crop_by_xpath_all("//li")(markup) == [
        "<li>One</li>",
        "<li>Two</li>",
        "<li>Three</li>",
    ]


@pytest.mark.parametrize(
    "attr,result",
    [
        ("lang", "en"),
        ("charset", "UTF8"),
        ("title", "TEST PAGE"),
        ("title_lower", "test page"),
        ("body_string", "test-string"),
        ("body_string_chars", ["t", "e", "s", "t", "-", "s", "t", "r", "i", "n", "g"]),
        ("body_string_flag", True),
        ("body_int", 555),
        ("body_float", 555.0),
        ("body_int_x10", 5550),
        ("fail_value_1", None),
        ("fail_value_2", False),
        ("fail_value_3", "spam"),
        ("body_int_list", [666, 777, 888]),
        ("body_float_list", [666.0, 777.0, 888.0]),
        ("max_body_list", 888),
        ("body_float_flag", True),
        ("fail_list_1", None),
        ("fail_list_2", False),
        ("fail_list_3", ["spam", "egg"]),
    ],
)
def test_parsel_parse(attr, result):
    value = getattr(PARSEL_SCHEMA, attr)
    assert value == result
