# Note: you can combine CSS and XPath selectors
import pprint
from typing import Generator, List

import requests
from parsel import Selector

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.callbacks.parsel import crop_by_selector_all, get_attr, get_text
from scrape_schema.fields.nested import NestedList
from scrape_schema.fields.parsel import ParselXPath


def request_pagination(start: int = 1, end: int = 50) -> Generator[str, None, None]:
    """requests pagination generator"""
    for page in range(start, end + 1):
        yield requests.get(
            f"https://books.toscrape.com/catalogue/page-{page}.html"
        ).text


class MainSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        # base schema configuration might be reused
        parsers_config = {Selector: {}}


class Book(MainSchema):
    # convert class attr to int
    __RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    _url_path: ScField[
        str, ParselXPath('//div[@class="image_container"]/a', callback=get_attr("href"))
    ]
    _image_path: ScField[
        str,
        ParselXPath('//div[@class="image_container"]/a/img', callback=get_attr("src")),
    ]
    _rating: ScField[
        str,
        ParselXPath(
            '//p[contains(@class, "star-rating")]',
            callback=lambda css: css.attrib.get("class").split()[-1],
        ),
    ]
    _price: ScField[
        str, ParselXPath('//div[@class="product_price"]/p[@class="price_color"]')
    ]
    name: ScField[str, ParselXPath("//h3/a", callback=get_attr("title"))]
    available: ScField[
        str,
        ParselXPath(
            '//div[@class="product_price"]/p[@class="instock availability"]',
            callback=get_text(strip=True, deep=True),
        ),
    ]

    @property
    def url(self) -> str:
        return f"https://books.toscrape.com/catalogue/{self._url_path}"

    @property
    def image(self) -> str:
        return f"https://books.toscrape.com{self._image_path[2:]}"

    @property
    def price(self) -> float:
        return float(self._price[2:])

    @property
    def currency(self) -> str:
        return self._price[1:2]

    @property
    def rating(self) -> int:
        return self.__RATING.get(self._rating, 0)


class CataloguePage(MainSchema):
    books: ScField[
        List[Book],
        NestedList(Book, crop_rule=crop_by_selector_all("section > div > ol.row > li")),
    ]


for resp in request_pagination():
    pprint.pprint(CataloguePage(resp).dict(), compact=True)
    break
    # {'books': [{'available': 'In stock',
    #             'currency': '£',
    #             'image': 'https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg',
    #             'name': 'A Light in the Attic',
    #             'price': 51.77,
    #             'rating': 3,
    #             'url': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'},
    #            {'available': 'In stock',
    #             'currency': '£',
    #             'image': 'https://books.toscrape.com/media/cache/26/0c/260c6ae16bce31c8f8c95daddd9f4a1c.jpg',
    #             'name': 'Tipping the Velvet',
    #             'price': 53.74,
    #             'rating': 1,
    #             'url': 'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'},
    # ...