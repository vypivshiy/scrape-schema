# Code comparison
## html

parsel:

```python
from parsel import Selector
import pprint
import requests


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
        available = book_sel.xpath('//div[@class="product_price"]/p[@class="instock availability"]/i').attrib.get('class')
        available = ('icon-ok' in available)
        rating = book_sel.xpath('//p[contains(@class, "star-rating")]').attrib.get('class')
        rating = __RATINGS.get(rating.split()[-1], 0)
        data['books'].append(dict(url=url, image=image, price=price, name=name, available=available, rating=rating))
    return data


if __name__ == '__main__':
    response = requests.get("https://books.toscrape.com/catalogue/page-2.html").text
    pprint.pprint(original_parsel(response), compact=True)
```

scrape_schema:

```python
from typing import List
import pprint
import requests
from scrape_schema import BaseSchema, Sc, Nested, sc_param, Parsel


class Book(BaseSchema):
    __RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    url: Sc[str, (Parsel()
                  .xpath('//div[@class="image_container"]/a/@href')
                  .get()
                  .concat_l("https://books.toscrape.com/catalogue/"))]
    image: Sc[str, (Parsel()
                    .xpath('//div[@class="image_container"]/a/img/@src')
                    .get()[2:]
                    .concat_l("https://books.toscrape.com"))]
    price: Sc[float, (Parsel(default=.0)
                      .xpath('//div[@class="product_price"]/p[@class="price_color"]/text()')
                      .get()[2:])]
    name: Sc[str, Parsel().xpath("//h3/a/@title").get()]
    available: Sc[bool, (Parsel()
                         .xpath('//div[@class="product_price"]/p[@class="instock availability"]/i')
                         .attrib['class']
                         .fn(lambda s: s == 'icon-ok')  # check available tag
                         )]
    _rating: Sc[str, Parsel().xpath('//p[contains(@class, "star-rating")]').attrib.get(key='class')]

    @sc_param
    def rating(self) -> int:
        return self.__RATINGS.get(self._rating.split()[-1], 0)


class MainPage(BaseSchema):
    books: Sc[List[Book], Nested(Parsel().xpath(".//section/div/ol[@class='row']/li").getall())]


if __name__ == '__main__':
    response = requests.get("https://books.toscrape.com/catalogue/page-2.html").text
    pprint.pprint(MainPage(response).dict(), compact=True)
```

## raw text

original re:

```python
import re
import pprint

TEXT = """
banana potato BANANA POTATO
-foo:10
-bar:20
lorem upsum dolor
192.168.0.1
"""


def parse_text(text: str) -> dict:
    if match := re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", text):
        ipv4 = match[1]
    else:
        ipv4 = None

    if matches := re.findall(r"(\d+)", text):
        max_digit = max(int(i) for i in matches)
    else:
        max_digit = None

    failed_value = bool(re.search(r"(ora)", text))

    if matches := re.findall(r"(\d+)", text):
        digits = [int(i) for i in matches]
        digits_float = [float(f'{i}.5') for i in matches]
    else:
        digits = None
        digits_float = None
    words_lower = matches if (matches := re.findall(r"([a-z]+)", text)) else None
    words_upper = matches if (matches := re.findall(r"([A-Z]+)", text)) else None

    return dict(ipv4=ipv4, max_digit=max_digit, failed_value=failed_value,
                digits=digits, digits_float=digits_float,
                words_lower=words_lower, words_upper=words_upper)


if __name__ == '__main__':
    pprint.pprint(parse_text(TEXT), width=48, compact=True)
    # {'digits': [10, 20, 192, 168, 0, 1],
    #  'digits_float': [10.5, 20.5, 192.5, 168.5, 0.5,
    #                   1.5],
    #  'failed_value': False,
    #  'ip_v4': '192.168.0.1',
    #  'max_digit': 192,
    #  'words_lower': ['banana', 'potato', 'foo',
    #                  'bar', 'lorem', 'upsum',
    #                  'dolor'],
    #  'words_upper': ['BANANA', 'POTATO']}
```

scrape_schema:

```python
from typing import List  # if you usage python3.8. If python3.9 - use build-in list
import pprint
from scrape_schema import Text, BaseSchema, Sc, sc_param

# Note: `Sc` is shortcut typing.Annotated

TEXT = """
banana potato BANANA POTATO
-foo:10
-bar:20
lorem upsum dolor
192.168.0.1
"""


class MySchema(BaseSchema):
    ipv4: Sc[str, Text().re_search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")[1]]
    failed_value: Sc[bool, Text(default=False).re_search(r"(ora)")[1]]
    digits: Sc[List[int], Text().re_findall(r"(\d+)")]
    digits_float: Sc[List[float], Text().re_findall(r"(\d+)").fn(lambda lst: [f"{s}.5" for s in lst])]
    words_lower: Sc[List[str], Text().re_findall("([a-z]+)")]
    words_upper: Sc[List[str], Text().re_findall(r"([A-Z]+)")]

    @sc_param
    def sum(self):
        return sum(self.digits)

    @sc_param
    def max_digit(self):
        return max(self.digits)

    @sc_param
    def all_words(self):
        return self.words_lower + self.words_upper


if __name__ == '__main__':
    pprint.pprint(MySchema(TEXT).dict(), compact=True)
# {'all_words': ['banana', 'potato', 'foo', 'bar', 'lorem', 'upsum', 'dolor',
#                'BANANA', 'POTATO'],
#  'digits': [10, 20, 192, 168, 0, 1],
#  'digits_float': [10.5, 20.5, 192.5, 168.5, 0.5, 1.5],
#  'failed_value': False,
#  'ipv4': '192.168.0.1',
#  'max_digit': 192,
#  'sum': 391,
#  'words_lower': ['banana', 'potato', 'foo', 'bar', 'lorem', 'upsum', 'dolor'],
#  'words_upper': ['BANANA', 'POTATO']}
```
