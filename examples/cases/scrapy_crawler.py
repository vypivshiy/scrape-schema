"""example how to usage scrape-schema in scrapy

usage: `scrapy runspider scrapy_crawler.py -o books.json`
"""
from typing import TYPE_CHECKING

# Note: create new venv and install scrapy and scrape-schema
import scrapy  # pip install scrapy
from schema import MainPage

if TYPE_CHECKING:
    from scrapy.http import HtmlResponse


class BookToScrapeSpider(scrapy.Spider):
    name = "books.to_scape"
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: HtmlResponse, **kwargs):
        # TODO implement adapter
        yield MainPage(response.selector).dict()
