# A hackernews schema parser https://news.ycombinator.com
import re
from typing import Annotated

from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.callbacks.soup import get_attr, replace_text
from scrape_schema.fields.nested import NestedList
from scrape_schema.fields.regex import ReMatch
from scrape_schema.fields.soup import SoupFind, SoupSelect


class Post(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    @staticmethod
    def _concat_href(path: str) -> str:
        """custom factory for concatenate path url with netloc"""
        return f"https://news.ycombinator.com{path}"

    id: Annotated[int, SoupFind('<tr class="athing">', callback=get_attr("id"))]
    rank: Annotated[
        int, SoupFind('<span class="rank">', callback=replace_text(".", ""))
    ]
    vote_up: Annotated[
        str,
        SoupFind(
            {"name": "a", "id": re.compile(r"^up_\d+")},
            callback=get_attr("href"),
            factory=_concat_href,
        ),
    ]
    source: Annotated[
        str, SoupSelect("td.title > span.titleline > a", callback=get_attr("href"))
    ]
    title: Annotated[str, SoupSelect("td.title > span.titleline > a")]
    source_netloc: Annotated[str, SoupFind('<span class="sitebit comhead">')]
    score: Annotated[
        int,
        SoupFind(
            '<span class="score">', callback=replace_text(" points", ""), default=0
        ),
    ]
    author: Annotated[str, SoupFind('<a class="hnuser">')]
    author_url: Annotated[
        str,
        SoupFind('<a class="hnuser">', callback=get_attr("href"), factory=_concat_href),
    ]
    date: Annotated[str, SoupFind('<span class="age">', callback=get_attr("title"))]
    time_ago: Annotated[str, SoupSelect("span.age > a")]
    comments: Annotated[int, ReMatch(r"(\d+)\s+comments", default=0)]
    post_url: Annotated[
        str,
        SoupFind(
            {"name": "a", "href": re.compile(r"^item\?id=\d+")},
            callback=get_attr("href"),
            factory=_concat_href,
        ),
    ]


class HackerNewsSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    @staticmethod
    def _crop_posts(markup: str) -> list[str]:
        """a crop rule for hackenews schema"""
        soup = BeautifulSoup(markup, "html.parser")
        # get main news table
        table = soup.find("tr", class_="athing").parent
        elements: list[str] = []
        first_tag: str = ""
        # get two 'tr' tags and concatenate, skip <tr class='spacer'>

        for tr in table.find_all("tr"):
            # <tr class="athing">
            if tr.attrs.get("class") and "athing" in tr.attrs.get("class"):
                first_tag = str(tr)
            # <tr>
            elif not tr.attrs:
                elements.append(first_tag + "\n" + str(tr))
                first_tag = ""
            # <tr class="morespace"> END page, stop iteration
            elif tr.attrs.get("class") and "morespace" in tr.attrs.get("class"):
                break
        return elements

    posts: Annotated[list[Post], NestedList(Post, crop_rule=_crop_posts)]
