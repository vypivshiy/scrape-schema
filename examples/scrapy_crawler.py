"""example how to usage scrape-schema in scrapy

usage: `scrapy runspider scrapy_crawler.py -o books.json`
"""

from typing import List

import scrapy
from scrapy.http import HtmlResponse
from scrape_schema import BaseSchema, sc_param, Parsel, Sc, Nested
import logging

_logger = logging.getLogger("scrape_schema")
_logger.setLevel(logging.ERROR)


class Book(BaseSchema):
    __RATINGS = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }  # dict for convert str to int
    url: Sc[
        str,
        (
            Parsel()
            .xpath('//div[@class="image_container"]/a/@href')
            .get()
            .concat_l("https://books.toscrape.com/catalogue/")
        ),
    ]

    image: Sc[
        str,
        (
            Parsel()
            .xpath('//div[@class="image_container"]/a/img/@src')
            .get()[2:]
            .concat_l("https://books.toscrape.com")
        ),
    ]
    price: Sc[
        float,
        (
            Parsel(default=.0)
            .xpath('//div[@class="product_price"]/p[@class="price_color"]/text()')
            .get()[2:]
        ),
    ]
    name: Sc[str, Parsel().xpath("//h3/a/@title").get()]
    available: Sc[
        bool,
        (
            Parsel()
            .xpath('//div[@class="product_price"]/p[@class="instock availability"]/i')
            .attrib["class"]
            .fn(lambda s: s == "icon-ok")  # check available tag
        ),
    ]
    _rating: Sc[
        str, Parsel().xpath('//p[contains(@class, "star-rating")]').attrib.get(key="class")
    ]

    def __init__(self, markup):
        super().__init__(markup)
        self._is_downloaded_image = False

    @sc_param
    def rating(self) -> int:
        return self.__RATINGS.get(self._rating.split()[-1], 0)

    @sc_param
    def urls(self) -> List[str]:
        return [self.url, self.image]


class MainPage(BaseSchema):
    """https://books.toscrape.com/catalogue/page-\d+.html"""

    books: Sc[
        List[Book], Nested(Parsel().xpath(".//section/div/ol[@class='row']/li"))
    ]


class BookToScrapeSpider(scrapy.Spider):
    name = "books.to_scape"
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: HtmlResponse, **kwargs):
        # TODO implement adapter
        yield MainPage(response.selector).dict()
