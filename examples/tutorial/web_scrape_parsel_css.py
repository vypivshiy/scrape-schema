from typing import Generator, Optional, List
from time import sleep
import pprint

import requests
from parsel import Selector

from scrape_schema.hooks import HooksStorage
from scrape_schema import BaseSchema, ScField, BaseSchemaConfig
from scrape_schema.fields.parsel import ParselSelect
from scrape_schema.fields.nested import NestedList
from scrape_schema.callbacks.parsel import crop_by_selector_all, get_attr, get_text

hooks = HooksStorage()


def request_pagination(start: int = 1, end: int = 50) -> Generator[str, None, None]:
    """requests pagination generator"""
    for page in range(start, end + 1):
        yield requests.get(f"https://books.toscrape.com/catalogue/page-{page}.html").text
        sleep(0.3)


class MainSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {Selector: {}}


@hooks.on_callback("Book.image")
def _concat_image(sel: Selector) -> str:
    # remove `..` symbols and concat url
    return "https://books.toscrape.com" + sel.attrib.get("src")[2:]


@hooks.on_callback("Book.rating")
def _rating_callback(sel: Selector) -> Optional[int]:
    # create dict table for convert string to integer
    ratings = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    rating_key = sel.attrib.get("class").split()[-1]
    return ratings.get(rating_key)


@hooks.on_callback("Book.price")
def _price_callback(sel: Selector) -> str:
    # remove 2 chars and return string digit value
    # (it's automatically converted to float)
    return sel.css("::text").get()[2:]


@hooks.on_callback("Book.url")
def _url_concat(sel: Selector) -> str:
    return f"https://books.toscrape.com/catalogue/{sel.attrib.get('href')}"


class BookInfo(MainSchema):
    ...


class Book(MainSchema):
    url: ScField[str, ParselSelect("div.image_container > a")]
    image: ScField[str, ParselSelect("div.image_container > a > img")]
    rating: ScField[int, ParselSelect('p.star-rating')]
    name: ScField[str, ParselSelect("h3 > a", callback=get_attr("title"))]
    price: ScField[float, ParselSelect("div.product_price > p.price_color")]
    available: ScField[str, ParselSelect("div.product_price > p.instock.availability",
                                         callback=get_text(deep=True, strip=True))]

    @property
    def about(self):
        # you can go to book url page and collect extra information,
        # you can follow the link and parse more information like this construction,
        # this tutorial will not implement
        response = requests.get(self.url).text
        return BookInfo(response)


class CataloguePage(MainSchema):
    books: ScField[List[Book],
                   NestedList(Book,
                              crop_rule=crop_by_selector_all(
                                  "section > div > ol.row > li",
                              ))]


for resp in request_pagination():
    pprint.pprint(CataloguePage(resp).dict(), compact=True)
    sleep(1)
# {'books': [{'available': 'In stock',
#             'image': 'https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg',
#             'name': 'A Light in the Attic',
#             'price': 51.77,
#             'rating': 3,
#             'url': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'},
#            {'available': 'In stock',
#             'image': 'https://books.toscrape.com/media/cache/26/0c/260c6ae16bce31c8f8c95daddd9f4a1c.jpg',
#             'name': 'Tipping the Velvet',
#             'price': 53.74,
#             'rating': 1,
#             'url': 'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'},
# ...
