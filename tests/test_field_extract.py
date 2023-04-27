from __future__ import annotations

from typing import Type

import pytest
from bs4 import BeautifulSoup

from scrape_schema import BaseField
from scrape_schema.callbacks.soup import get_attr
from scrape_schema.fields.regex import ReMatch, ReMatchList
from scrape_schema.fields.soup import SoupFind, SoupFindList


@pytest.mark.parametrize(
    "field,string,type_,result",
    [
        (ReMatch(r"(\d+)"), "100", int, 100),
        (ReMatch(r"(\d+)", callback=lambda s: f"{s}.5"), "100", float, 100.5),
        (ReMatch(r"(\d+)", callback=lambda s: f"{s}.5", default=0), "NaN", float, 0.5),
        (ReMatchList(r"(\d+)", callback=int, factory=sum), "1 2 3 4 5", None, 15),
        (ReMatchList(r"(\d+)"), "1 2 3 5", list[int], [1, 2, 3, 5]),
        (ReMatchList(r"(\d+)"), "1 2 3 5", None, ["1", "2", "3", "5"]),
    ],
)
def test_extract_regex(field: BaseField, string: str, type_: Type, result):
    assert field.extract(string, type_=type_) == result


@pytest.mark.parametrize(
    "field,string,type_,result",
    [
        (
            SoupFind("<a>", callback=get_attr("href")),
            '<a href="spam">egg</a>',
            None,
            "spam",
        ),
        (SoupFind("<a>"), '<a href="spam">egg</a>', None, "egg"),
        (SoupFind("<p>"), "<p>100</p>", int, 100),
        (SoupFindList("<p>"), "<p>1</p>\n<p>2</p>\n<p>3</p>\n", list[int], [1, 2, 3]),
        (
            SoupFindList("<p>", factory=lambda lst: sum(int(i) for i in lst)),
            "<p>1</p>\n<p>2</p>\n<p>3</p>\n",
            None,
            6,
        ),
    ],
)
def test_extract_soup(field: BaseField, string: str, type_: Type, result):
    assert field.extract(BeautifulSoup(string, "html.parser"), type_=type_) == result


def test_raise_error():
    with pytest.raises(TypeError):
        SoupFind("<a>").extract("<a href='spam'>")
