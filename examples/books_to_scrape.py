from typing import List  # or usage buildin list in python3.9+ versions
import pprint
import requests  # or any lib
from scrape_schema2 import BaseSchema, Sc, Nested, sc_param
from scrape_schema2 import Parsel as F  # type: ignore


class Book(BaseSchema):
    __RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}  # dict for convert str to int
    url: Sc[str, (F()
                  .xpath('//div[@class="image_container"]/a/@href')
                  .get()
                  .concat_l("https://books.toscrape.com/catalogue/"))]

    image: Sc[str, (F()
              .xpath('//div[@class="image_container"]/a/img/@src')
              .get()[2:]
              .concat_l("https://books.toscrape.com"))]
    price: Sc[float, (F()
                      .xpath('//div[@class="product_price"]/p[@class="price_color"]/text()').get()[2:])]
    name: Sc[str, F().xpath("//h3/a/@title").get()]
    available: Sc[bool, (F()
                         .xpath('//div[@class="product_price"]/p[@class="instock availability"]/i')
                         .attrib['class']
                         .fn(lambda s: s == 'icon-ok')  # check available tag
                         )]

    def __init__(self, markup):
        super().__init__(markup)
        self._is_downloaded_image = False

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
    books: Sc[List[Book], Nested(F().css("section > div > ol.row > li").getall())]

    def download_all_images(self):
        for book in self.books:
            book.download_image()


if __name__ == '__main__':
    response = requests.get("https://books.toscrape.com/catalogue/page-2.html").text
    result = MainPage(response)
    print(result.books[0].is_downloaded_image)  # False
    result.books[0].download_image()  # True
    print(result.books[0].is_downloaded_image)
    print(result.books[1].is_downloaded_image)
    pprint.pprint(result.dict(), compact=True)
