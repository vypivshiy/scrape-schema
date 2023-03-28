from typing import Annotated
from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, MetaSchema
from scrape_schema.fields.soup import SoupFind, SoupSelect, SoupSelectList
from scrape_schema.fields.nested import NestedList
from scrape_schema.callbacks.soup import get_attr, crop_by_tag_all, get_text, replace_text

from callbacks import crop_schedule, crop_ongoing, crop_new_anime


class BaseMeta(MetaSchema):
    parsers_config = {BeautifulSoup: {"features": "html.parser"}}


class SchemaConfig(BaseSchema):
    """schema config"""
    class Meta(BaseMeta):
        pass


# schemas
class AnimeSeason(SchemaConfig):
    # <div class="item"> -> <div class="media-body">
    url: Annotated[str, SoupFind('<a class="text-nowrap">', callback=get_attr("href"))]
    name: Annotated[str, SoupFind('<a class="text-nowrap">')]
    image: Annotated[str, SoupFind({"name": "div", "class_": "tns-lazy-img"},
                                   callback=get_attr("data-src"))]
    rating: Annotated[float, SoupFind('<div class="p-rate-flag__text">',
                                      callback=replace_text(',', '.', strip=True))]


class ScheduleItem(SchemaConfig):
    # <div class="list-group">[1] -> <div class="media-body">
    title: Annotated[str, SoupFind('<span class="last-update-title">')]
    episode: Annotated[int, SoupFind('<div class="font-weight-600">', callback=replace_text(' серия', ''))]
    time: Annotated[str, SoupFind('<div class="text-gray-dark-6">')]


class Ongoing(SchemaConfig):
    # <div class="list-group">[0] -> <div class="last-update-item">
    title: Annotated[str, SoupFind('<span class="last-update-title">')]
    episode: Annotated[int, SoupFind('<div class="text-truncate">', callback=replace_text(' серия', ''))]
    dub: Annotated[str, SoupFind('<div class="text-gray-dark-6">')]


class NewAnime(SchemaConfig):
    image: Annotated[str, SoupFind('<div class="anime-list-lazy">', callback=get_attr('data-original'))]
    url: Annotated[str, SoupSelect('div.h5 > a', callback=get_attr('href'))]
    rating: Annotated[float, SoupFind('<div class="p-rate-flag__text">',
                                      default='0',
                                      callback=replace_text(',', '.'))]
    title: Annotated[str, SoupFind('<div class="h5">')]
    title_orig: Annotated[str, SoupSelect('div.text-gray-dark-6.small.mb-2 > div')]
    type: Annotated[str, SoupSelect('span > a.text-link-gray')]
    year: Annotated[int, SoupSelect('span.anime-year > a')]
    genres: Annotated[list[str], SoupSelectList('span.anime-genre > a', callback=get_attr('title'))]
    description: Annotated[str, SoupFind('<div class="description">',
                                         callback=get_text(strip=True))]


class AnimegoSchema(SchemaConfig):
    title: Annotated[str, SoupFind("<title>")]
    lang: Annotated[str, SoupFind("<html>", callback=get_attr("lang"))]
    anime_seasons: Annotated[list[AnimeSeason], NestedList(AnimeSeason,
                                                           crop_rule=crop_by_tag_all('<div class="item">'))]
    schedule: Annotated[list[ScheduleItem], NestedList(ScheduleItem,
                                                       crop_rule=crop_schedule)]
    ongoings: Annotated[list[Ongoing], NestedList(Ongoing, crop_rule=crop_ongoing)]
    new_anime: Annotated[list[NewAnime], NestedList(NewAnime, crop_rule=crop_new_anime)]

    @property
    def ongoings_count(self):
        return len(self.ongoings)

    @property
    def new_anime_count(self):
        return len(self.new_anime)

    @property
    def schedule_count(self):
        return len(self.schedule)
