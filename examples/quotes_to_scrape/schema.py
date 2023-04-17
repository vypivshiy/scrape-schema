# required requests or any http lib
from typing import Annotated
from collections import Counter
import json

import requests
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect
from scrape_schema.fields.nested import NestedList
from scrape_schema.callbacks.soup import crop_by_tag_all, get_attr


def top_10(lst: list[str]) -> list[str]:
    """get 10 most common tags"""
    return [v[0] for v in Counter(lst).most_common(10)]


class Quote(BaseSchema):
    # <div class="quote">
    class Meta(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    text: Annotated[str, SoupFind('<span class="text">')]
    author: Annotated[str, SoupFind('<small class="author">')]
    about: Annotated[str, SoupFind(
        {"name": "a", "string": "(about)"}, callback=get_attr("href"))]
    tags: Annotated[list[str], SoupFindList('<a class="tag">')]


class QuotePage(BaseSchema):
    # https://quotes.toscrape.com/page/{} document
    # set usage parsers backends
    class Meta(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    title: Annotated[str, SoupSelect('head > title')]
    # wrote just example, recommended write properties or methods in this class
    title_len: Annotated[int, SoupFind("<title>", factory=len)]
    title_upper: Annotated[str, SoupFind("<title>", factory=lambda t: t.upper())]

    quotes: Annotated[list[Quote], NestedList(Quote, crop_rule=crop_by_tag_all({"name": "div", "class_": "quote"},
                                                                               features="html.parser"))]
    top_10_tags: Annotated[list[str], SoupFindList('<a class="tag">',
                                                   factory=top_10)]
    top_tags_5_len: Annotated[list[str], SoupFindList('<a class="tag">',
                                                      filter_=lambda el: len(el.get_text()) <= 5,
                                                      factory=top_10)]


if __name__ == '__main__':
    resp = requests.get("https://quotes.toscrape.com/page/1/").text
    schema = QuotePage(resp)
    print(schema.title)
    print(schema.title_upper)
    print(schema.title_len)
    print(schema.top_10_tags)
    print(schema.top_tags_5_len)
    print(schema.quotes[0].text, schema.quotes[0].about)
    print(json.dumps(schema.dict(), indent=4))  # pretty print
    # parse many responses
    # NOTE: recommend usage selectolax backend for increase speed
    responses = [requests.get(f"https://quotes.toscrape.com/page/{i}/").text
                 for i in range(1, 3)]
    schemas = QuotePage.init_list(responses)
    print(*schemas, sep="\n---\n")
    # Quotes to Scrape
    # QUOTES TO SCRAPE
    # 16
    # ['inspirational', 'life', 'humor', 'books', 'love', 'simile', 'change', 'deep-thoughts', 'thinking', 'world']
    # ['life', 'humor', 'books', 'love', 'world', 'live', 'value', 'truth']
    # “The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.” /author/Albert-Einstein
    # {
    #     "title": "Quotes to Scrape",
    #     "title_len": 16,
    #     "title_upper": "QUOTES TO SCRAPE",
    #     "quotes": [
    #         {
    #             "text": "\u201cThe world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.\u201d",
    #             "author": "Albert Einstein",
    #             "about": "/author/Albert-Einstein",
    #             "tags": [
    #                 "change",
    #                 "deep-thoughts",
    #                 "thinking",
    #                 "world"
    #             ]
    #         },
    #         {
    #             "text": "\u201cIt is our choices, Harry, that show what we truly are, far more than our abilities.\u201d",
    #             "author": "J.K. Rowling",
    #             "about": "/author/J-K-Rowling",
    #             "tags": [
    #                 "abilities",
    #                 "choices"
    #             ]
    #         },
    #         {
    #             "text": "\u201cThere are only two ways to live your life. One is as though nothing is a miracle. The other is as though everything is a miracle.\u201d",
    #             "author": "Albert Einstein",
    #             "about": "/author/Albert-Einstein",
    #             "tags": [
    #                 "inspirational",
    #                 "life",
    #                 "live",
    #                 "miracle",
    #                 "miracles"
    #             ]
    #         },
    #         {
    #             "text": "\u201cThe person, be it gentleman or lady, who has not pleasure in a good novel, must be intolerably stupid.\u201d",
    #             "author": "Jane Austen",
    #             "about": "/author/Jane-Austen",
    #             "tags": [
    #                 "aliteracy",
    #                 "books",
    #                 "classic",
    #                 "humor"
    #             ]
    #         },
    #         {
    #             "text": "\u201cImperfection is beauty, madness is genius and it's better to be absolutely ridiculous than absolutely boring.\u201d",
    #             "author": "Marilyn Monroe",
    #             "about": "/author/Marilyn-Monroe",
    #             "tags": [
    #                 "be-yourself",
    #                 "inspirational"
    #             ]
    #         },
    #         {
    #             "text": "\u201cTry not to become a man of success. Rather become a man of value.\u201d",
    #             "author": "Albert Einstein",
    #             "about": "/author/Albert-Einstein",
    #             "tags": [
    #                 "adulthood",
    #                 "success",
    #                 "value"
    #             ]
    #         },
    #         {
    #             "text": "\u201cIt is better to be hated for what you are than to be loved for what you are not.\u201d",
    #             "author": "Andr\u00e9 Gide",
    #             "about": "/author/Andre-Gide",
    #             "tags": [
    #                 "life",
    #                 "love"
    #             ]
    #         },
    #         {
    #             "text": "\u201cI have not failed. I've just found 10,000 ways that won't work.\u201d",
    #             "author": "Thomas A. Edison",
    #             "about": "/author/Thomas-A-Edison",
    #             "tags": [
    #                 "edison",
    #                 "failure",
    #                 "inspirational",
    #                 "paraphrased"
    #             ]
    #         },
    #         {
    #             "text": "\u201cA woman is like a tea bag; you never know how strong it is until it's in hot water.\u201d",
    #             "author": "Eleanor Roosevelt",
    #             "about": "/author/Eleanor-Roosevelt",
    #             "tags": [
    #                 "misattributed-eleanor-roosevelt"
    #             ]
    #         },
    #         {
    #             "text": "\u201cA day without sunshine is like, you know, night.\u201d",
    #             "author": "Steve Martin",
    #             "about": "/author/Steve-Martin",
    #             "tags": [
    #                 "humor",
    #                 "obvious",
    #                 "simile"
    #             ]
    #         }
    #     ],
    #     "top_10_tags": [
    #         "inspirational",
    #         "life",
    #         "humor",
    #         "books",
    #         "love",
    #         "simile",
    #         "change",
    #         "deep-thoughts",
    #         "thinking",
    #         "world"
    #     ],
    #     "top_tags_5_len": [
    #         "life",
    #         "humor",
    #         "books",
    #         "love",
    #         "world",
    #         "live",
    #         "value",
    #         "truth"
    #     ]
    # }
    # QuotePage(title<str>=Quotes to Scrape, title_len<int>=16, title_upper<str>=QUOTES TO SCRAPE, quotes<list>=[Quote(...
    # ---
    # QuotePage(title<str>=Quotes to Scrape, title_len<int>=16, title_upper<str>=QUOTES TO SCRAPE, quotes<list>=[Quote(...
