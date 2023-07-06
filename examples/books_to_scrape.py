import logging

from typing import List  # or usage buildin list in python3.9+ versions
import pprint
import requests  # or any http lib
from scrape_schema import BaseSchema, Sc, Nested, sc_param
from scrape_schema import Parsel as F  # type: ignore
from parsel import Selector


class Book(BaseSchema):
    """Entrypoint https://books.toscrape.com/catalogue/page-\d+.html
    """
    __RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}  # dict for convert str to int
    url: Sc[str, (F()
                  .xpath('//div[@class="image_container"]/a/@href')
                  .get()
                  .concat_l("https://books.toscrape.com/catalogue/"))]

    image: Sc[str, (F()
                    .xpath('//div[@class="image_container"]/a/img/@src')
                    .get()[2:]
                    .concat_l("https://books.toscrape.com"))]
    price: Sc[float, (F(default=.0)
                      .xpath('//div[@class="product_price"]/p[@class="price_color"]/text()').get()[2:])]
    name: Sc[str, F().xpath("//h3/a/@title").get()]
    available: Sc[bool, (F()
                         .xpath('//div[@class="product_price"]/p[@class="instock availability"]/i')
                         .attrib['class']
                         .fn(lambda s: s == 'icon-ok')  # check available tag
                         )]
    _rating: Sc[str, F().xpath('//p[contains(@class, "star-rating")]').attrib.get(key='class')]

    def __init__(self, markup):
        super().__init__(markup)
        self._is_downloaded_image = False

    @sc_param
    def rating(self) -> int:
        return self.__RATINGS.get(self._rating.split()[-1], 0)

    @sc_param
    def urls(self) -> List[str]:
        return [self.url, self.image]

    # you can provide any methods, properties in class
    def download_image(self):
        if not self.is_downloaded_image:
            resp = requests.get(self.image)
            img_name = self.image.split("/")[-1]
            with open(f"imgs/{img_name}", "wb") as f:
                f.write(resp.content)
            self._is_downloaded_image = True

    @property
    def is_downloaded_image(self):
        return self._is_downloaded_image


class MainPage(BaseSchema):
    """https://books.toscrape.com/catalogue/page-\d+.html"""
    books: Sc[List[Book], Nested(F().xpath(".//section/div/ol[@class='row']/li").getall())]

    def download_all_images(self):
        for book in self.books:
            book.download_image()


def original_parsel(resp: str):
    sel = Selector(resp)
    __RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    data: dict[str, list[dict]] = {"books": []}
    for book_sel in sel.xpath(".//section/div/ol[@class='row']/li"):
        if url := book_sel.xpath('//div[@class="image_container"]/a/@href').get():
            url = f"https://books.toscrape.com/catalogue/{url}"
        if image := book_sel.xpath('//div[@class="image_container"]/a/img/@src').get():
            image = f"https://books.toscrape.com{image[2:]}"
        if price := book_sel.xpath('//div[@class="product_price"]/p[@class="price_color"]/text()').get():
            price = float(price[2:])
        else:
            price = .0
        name = book_sel.xpath("//h3/a/@title").get()
        available = book_sel.xpath('//div[@class="product_price"]/p[@class="instock availability"]/i').attrib.get(
            'class')
        available = ('icon-ok' in available)
        rating = book_sel.xpath('//p[contains(@class, "star-rating")]').attrib.get('class')
        rating = __RATINGS.get(rating.split()[-1], 0)
        data['books'].append(dict(url=url, image=image, price=price, name=name, available=available, rating=rating))
    return data


if __name__ == '__main__':
    # optional logging configuration
    logger = logging.getLogger('scrape_schema')
    # logger.setLevel(logging.INFO)
    response = requests.get("https://books.toscrape.com/catalogue/page-2.html").text
    result = MainPage(response)
    # pseudo custom API example
    print(result.books[0].is_downloaded_image)  # False
    result.books[0].download_image()  # True
    print(result.books[0].is_downloaded_image)
    print(result.books[1].is_downloaded_image)
    pprint.pprint(result.dict(), compact=True)
