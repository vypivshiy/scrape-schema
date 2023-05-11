import re
from typing import List, Optional

from bs4 import BeautifulSoup

from scrape_schema import ScField, BaseSchema, BaseSchemaConfig
from scrape_schema.fields.soup import SoupSelect, SoupSelectList
from scrape_schema.callbacks.soup import get_attr, get_text
from scrape_schema.callbacks.soup import crop_by_selector_all as cbsa
from scrape_schema.fields.nested import NestedList


from _http import send_request

__all__ = ["IS_REFER", "PageRefer", "PageContent"]


IS_REFER = re.compile(r'.*? may refer to:')


class SchemaConfig(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "lxml"}}


class Referer(SchemaConfig):
    _path_href: ScField[str, SoupSelect("a",
                                        callback=get_attr("href"))]
    name: ScField[str, SoupSelect("a", callback=get_attr("title"))]
    description: ScField[str, SoupSelect("a")]

    @property
    def url(self):
        return f"https://en.wikipedia.org{self._path_href}"

    def view(self):
        return f"{self.name} {self.description} ({self.url})"

    def get_page(self) -> "PageContent":
        return PageContent(send_request(self.url))


class PageRefer(SchemaConfig):
    categories: ScField[List[Referer], NestedList(Referer,
                                                  crop_rule=cbsa("#mw-normal-catlinks > ul > li"))]
    referrers: ScField[List[Referer], NestedList(Referer,
                                                 crop_rule=cbsa('#mw-content-text > div.mw-parser-output > ul > li'))]

    def _render_ref(self):
        return '\n'.join([f"{i} {ref.view()}" for i, ref in enumerate(self.referrers, 1)])

    def _render_cat(self):
        return '\n'.join([f"{i} {cat.view()}" for i, cat in enumerate(self.categories, 1)])

    def view(self):
        return f"""
referrences:
{self._render_ref()}

categories:
{self._render_cat()}

"""


class PageThumbnail(SchemaConfig):
    _thumb_path: ScField[str, SoupSelect('div.thumbinner > a', callback=get_attr("href"))]
    description: ScField[str, SoupSelect('div.thumbinner > div.thumbcaption', callback=get_text(strip=True))]

    @property
    def url(self):
        return f"https://en.wikipedia.org/wiki/{self._thumb_path}"

    def view(self):
        return f"{self.url}\n{self.description}"


class PageReference(SchemaConfig):
    ref_id: ScField[str, SoupSelect('li', callback=get_attr('id'))]
    _href_paths: ScField[List[str], SoupSelectList('span.mw-cite-backlink > a', callback=get_attr('href'), default=[])]
    text: ScField[str, SoupSelect('span.reference-text > cite', callback=get_text(separator=" ", strip=True))]

    @property
    def urls(self) -> List[str]:
        return [f"https://en.wikipedia.org/wiki/{p}" for p in self._href_paths]

    def view(self):
        return f"""
"""


class PageContent(SchemaConfig):
    title: ScField[str, SoupSelect("h1#firstHeading")]
    note: ScField[Optional[str], SoupSelect("div.hatnote.navigation-not-searchable")]
    _note_href: ScField[Optional[str], SoupSelect("div.hatnote.navigation-not-searchable > a",
                                                  callback=get_attr("href"))]
    _text_chunks: ScField[List[str], SoupSelectList("#mw-content-text > div.mw-parser-output > p")]
    thumbnails: ScField[List[PageThumbnail], NestedList(PageThumbnail, crop_rule=cbsa('div.thumbinner'))]
    references: ScField[List[PageReference], NestedList(PageReference, crop_rule=cbsa('div.reflist > div > ol > li'))]

    @property
    def note_url(self):
        return f"https://en.wikipedia.org/wiki/{self._note_href}"

    @property
    def text(self):
        return "".join(self._text_chunks)

    def _render_thumbnails(self):
        return "\n\n".join([t.view() for t in self.thumbnails])

    def _render_references(self):
        return '\n'.join([f"{i} {ref.text} {' '.join(ref.urls)}" for i, ref in enumerate(self.references, 1)])

    def view(self) -> str:
        return f"""{self.title}
        
{self.note} ({self.note_url})
        
thumbnails:
{self._render_thumbnails()}
Text:

{self.text}

References:
{self._render_references()}
"""
