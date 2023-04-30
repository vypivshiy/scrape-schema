# required requests or any http lib
import json
from collections import Counter
from typing import List  # python38 support

import requests
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.callbacks.soup import crop_by_tag_all, get_attr
from scrape_schema.fields.nested import NestedList
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect


def top_10(lst: List[str]) -> List[str]:
    """get 10 most common tags"""
    return [v[0] for v in Counter(lst).most_common(10)]


class Quote(BaseSchema):
    # <div class="quote">
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    text: ScField[str, SoupFind('<span class="text">')]
    author: ScField[str, SoupFind('<small class="author">')]
    about: ScField[
        str, SoupFind({"name": "a", "string": "(about)"}, callback=get_attr("href"))
    ]
    tags: ScField[List[str], SoupFindList('<a class="tag">')]


class QuotePage(BaseSchema):
    # https://quotes.toscrape.com/page/{} document
    # set usage parsers backends
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    title: ScField[str, SoupSelect("head > title")]
    # wrote just example, recommended write properties or methods in this class
    title_len: ScField[int, SoupFind("<title>", factory=len)]
    title_upper: ScField[str, SoupFind("<title>", factory=lambda t: t.upper())]

    quotes: ScField[
        List[Quote],
        NestedList(
            Quote,
            crop_rule=crop_by_tag_all(
                {"name": "div", "class_": "quote"}, features="html.parser"
            ),
        ),
    ]
    top_10_tags: ScField[List[str], SoupFindList('<a class="tag">', factory=top_10)]
    top_tags_5_len: ScField[
        List[str],
        SoupFindList(
            '<a class="tag">',
            filter_=lambda el: len(el.get_text()) <= 5,
            factory=top_10,
        ),
    ]


def parse_many():
    # parse many responses
    # NOTE: recommend usage selectolax backend for increase speed
    responses = [
        requests.get(f"https://quotes.toscrape.com/page/{i}/").text for i in range(1, 3)
    ]
    schemas = QuotePage.from_list(responses)
    print(*schemas, sep="\n---\n")
    # QuotePage(title<str>=Quotes to Scrape, title_len<int>=16, title_upper<str>=QUOTES TO SCRAPE, quotes<list>=[Quote(...
    # ---
    # QuotePage(title<str>=Quotes to Scrape, title_len<int>=16, title_upper<str>=QUOTES TO SCRAPE, quotes<list>=[Quote(...


def parse_first():
    resp = requests.get("https://quotes.toscrape.com/page/1/").text
    schema = QuotePage(resp)
    print(schema.title)
    print(schema.title_upper)
    print(schema.title_len)
    print(schema.top_10_tags)
    print(schema.top_tags_5_len)
    print(schema.quotes[0].text, schema.quotes[0].about)
    print(json.dumps(schema.dict(), indent=4))  # pretty print


if __name__ == "__main__":
    parse_first()
    parse_many()
