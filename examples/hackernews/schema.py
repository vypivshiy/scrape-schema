# A hackernews schema parser https://news.ycombinator.com
from typing import Annotated
import re

from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.fields.soup import SoupFind, SoupSelect
from scrape_schema.fields.nested import NestedList
from scrape_schema.fields.regex import ReMatch
from scrape_schema.callbacks.soup import get_attr, replace_text

from callbacks import crop_posts, concat_href


class Post(BaseSchema):
    class Meta(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    id: Annotated[int, SoupFind('<tr class="athing">', callback=get_attr('id'))]
    rank: Annotated[int, SoupFind('<span class="rank">', callback=replace_text('.', ''))]
    vote_up: Annotated[str, SoupFind({'name': 'a', 'id': re.compile(r'^up_\d+')},
                                     callback=get_attr('href'), factory=concat_href)]
    source: Annotated[str, SoupSelect('td.title > span.titleline > a', callback=get_attr('href'))]
    title: Annotated[str, SoupSelect('td.title > span.titleline > a')]
    source_netloc: Annotated[str, SoupFind('<span class="sitebit comhead">')]
    score: Annotated[int, SoupFind('<span class="score">', callback=replace_text(' points', ''), default=0)]
    author: Annotated[str, SoupFind('<a class="hnuser">')]
    author_url: Annotated[str, SoupFind('<a class="hnuser">', callback=get_attr('href'), factory=concat_href)]
    date: Annotated[str, SoupFind('<span class="age">', callback=get_attr('title'))]
    time_ago: Annotated[str, SoupSelect('span.age > a')]
    comments: Annotated[int, ReMatch(r'(\d+)\s+comments', default=0)]
    post_url: Annotated[str, SoupFind({'name': 'a', 'href': re.compile(r'^item\?id=\d+')}, callback=get_attr('href'),
                                      factory=concat_href)]


class HackerNewsSchema(BaseSchema):
    class Meta(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    posts: Annotated[list[Post], NestedList(Post, crop_rule=crop_posts)]
