import pprint
from time import sleep
from typing import Generator, List, Optional

import requests
from selectolax.parser import HTMLParser, Node

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.callbacks.slax import crop_by_slax_all, get_attr, get_text
from scrape_schema.fields.nested import NestedList
from scrape_schema.fields.slax import SlaxSelect
from scrape_schema.hooks import HooksStorage

hooks = HooksStorage()


def request_pagination(start: int = 1, end: int = 50) -> Generator[str, None, None]:
    """requests pagination generator"""
    for page in range(start, end + 1):
        yield requests.get(
            f"https://books.toscrape.com/catalogue/page-{page}.html"
        ).text
        sleep(0.3)


class MainSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}


@hooks.on_callback("Book.image")
def _concat_image(node: Node) -> str:
    # remove `..` symbols and concat url
    return "https://books.toscrape.com" + node.attrs.get("src")[2:]


@hooks.on_callback("Book.rating")
def _rating_callback(node: Node) -> Optional[int]:
    # create dict table for convert string to integer
    ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    rating_key = node.attrs.get("class").split()[-1]
    return ratings.get(rating_key)


@hooks.on_callback("Book.price")
def _price_callback(node: Node) -> str:
    # remove 2 chars and return string digit value
    # (it's automatically converted to float)
    return node.text(deep=False)[2:]


@hooks.on_callback("Book.url")
def _url_concat(node: Node) -> str:
    return f"https://books.toscrape.com/catalogue/{node.attrs.get('href')}"


class BookInfo(MainSchema):
    ...


class Book(MainSchema):
    url: ScField[str, SlaxSelect("div.image_container > a")]
    image: ScField[str, SlaxSelect("div.image_container > a > img")]
    rating: ScField[int, SlaxSelect("p.star-rating")]
    name: ScField[str, SlaxSelect("h3 > a", callback=get_attr("title"))]
    price: ScField[float, SlaxSelect("div.product_price > p.price_color")]
    available: ScField[
        str,
        SlaxSelect(
            "div.product_price > p.instock.availability", callback=get_text(strip=True)
        ),
    ]

    @property
    def about(self):
        # you can go to book url page and collect extra information,
        # you can follow the link and parse more information like this construction,
        # this tutorial will not implement
        response = requests.get(self.url).text
        return BookInfo(response)


class CataloguePage(MainSchema):
    books: ScField[
        List[Book],
        NestedList(
            Book,
            crop_rule=crop_by_slax_all(
                "section > div > ol.row > li",
            ),
        ),
    ]


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
