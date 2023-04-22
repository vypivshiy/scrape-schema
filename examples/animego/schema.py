from typing import Annotated

from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.callbacks.soup import (
    crop_by_tag_all,
    get_attr,
    get_text,
    replace_text,
)
from scrape_schema.fields.nested import NestedList
from scrape_schema.fields.soup import SoupFind, SoupSelect, SoupSelectList


class SchemaConfig(BaseSchema):
    """schema config"""

    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}


# schemas
class AnimeSeason(SchemaConfig):
    # <div class="item"> -> <div class="media-body">
    url: Annotated[str, SoupFind('<a class="text-nowrap">', callback=get_attr("href"))]
    name: Annotated[str, SoupFind('<a class="text-nowrap">')]
    image: Annotated[
        str,
        SoupFind(
            {"name": "div", "class_": "tns-lazy-img"}, callback=get_attr("data-src")
        ),
    ]
    rating: Annotated[
        float,
        SoupFind(
            '<div class="p-rate-flag__text">',
            default="0",
            callback=replace_text(",", ".", strip=True),
        ),
    ]


class ScheduleItem(SchemaConfig):
    # <div class="list-group">[1] -> <div class="media-body">
    title: Annotated[str, SoupFind('<span class="last-update-title">')]
    episode: Annotated[
        int,
        SoupFind('<div class="font-weight-600">', callback=replace_text(" серия", "")),
    ]
    time: Annotated[str, SoupFind('<div class="text-gray-dark-6">')]


class Ongoing(SchemaConfig):
    # <div class="list-group">[0] -> <div class="last-update-item">
    title: Annotated[str, SoupFind('<span class="last-update-title">')]
    episode: Annotated[
        int,
        SoupFind('<div class="text-truncate">', callback=replace_text(" серия", "")),
    ]
    dub: Annotated[str, SoupFind('<div class="text-gray-dark-6">')]


class NewAnime(SchemaConfig):
    image: Annotated[
        str,
        SoupFind('<div class="anime-list-lazy">', callback=get_attr("data-original")),
    ]
    url: Annotated[str, SoupSelect("div.h5 > a", callback=get_attr("href"))]
    rating: Annotated[
        float,
        SoupFind(
            '<div class="p-rate-flag__text">',
            default="0",
            callback=replace_text(",", "."),
        ),
    ]
    title: Annotated[str, SoupFind('<div class="h5">')]
    title_orig: Annotated[str, SoupSelect("div.text-gray-dark-6.small.mb-2 > div")]
    type: Annotated[str, SoupSelect("span > a.text-link-gray")]
    year: Annotated[int, SoupSelect("span.anime-year > a")]
    genres: Annotated[
        list[str], SoupSelectList("span.anime-genre > a", callback=get_attr("title"))
    ]
    description: Annotated[
        str, SoupFind('<div class="description">', callback=get_text(strip=True))
    ]


class AnimegoSchema(SchemaConfig):
    @staticmethod
    def _crop_new_anime(markup: str) -> list[str]:
        soup = BeautifulSoup(markup, "html.parser")
        tags = soup.select_one("#content > div:nth-child(2)").find_all(
            "div", class_="animes-list-item media"
        )
        return [str(tag) for tag in tags]

    @staticmethod
    def _crop_ongoing(markup: str) -> list[str]:
        soup = BeautifulSoup(markup, "html.parser")
        tags = soup.find_all("div", class_="list-group")[0].find_all(
            "div", class_="last-update-item"
        )
        return [str(tag) for tag in tags]

    @staticmethod
    def _crop_schedule(markup: str) -> list[str]:
        soup = BeautifulSoup(markup, "html.parser")
        tags = soup.find_all("div", class_="list-group")[1].find_all(
            "div", class_="media-body"
        )
        return [str(tag) for tag in tags]

    title: Annotated[str, SoupFind("<title>")]
    lang: Annotated[str, SoupFind("<html>", callback=get_attr("lang"))]
    anime_seasons: Annotated[
        list[AnimeSeason],
        NestedList(AnimeSeason, crop_rule=crop_by_tag_all('<div class="item">')),
    ]
    schedule: Annotated[
        list[ScheduleItem], NestedList(ScheduleItem, crop_rule=_crop_schedule)
    ]
    ongoings: Annotated[list[Ongoing], NestedList(Ongoing, crop_rule=_crop_ongoing)]
    new_anime: Annotated[
        list[NewAnime], NestedList(NewAnime, crop_rule=_crop_new_anime)
    ]

    @property
    def ongoings_count(self):
        return len(self.ongoings)

    @property
    def new_anime_count(self):
        return len(self.new_anime)

    @property
    def schedule_count(self):
        return len(self.schedule)
