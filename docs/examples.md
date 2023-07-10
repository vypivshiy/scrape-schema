# Cases

This section will show examples of using scrape_schema in different situations.

To demonstrate the universality of reuse, a parser will be implemented
under [books.toscrape](https://books.toscrape.com) store

> schema.py
```python
import logging
from typing import List

from scrape_schema import BaseSchema, sc_param, Parsel, Sc, Nested


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
```
>> further classes will be imported from the `schema.py` module

## scrapy
You can easily reuse this scheme in scrapy.Crawler's

>> It is recommended to create a new virtual environment, then install scrapy and scrape-schema

```python
import scrapy  # pip install scrapy
from schema import MainPage


class BookToScrapeSpider(scrapy.Spider):
    name = "books.to_scape"
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response, **kwargs):
        yield MainPage(response.selector).dict()
```

## Stdin adapter
Also, you can write an adapter to convert stdin to json:

> stdin_adapter.py

```python
import json
import sys

from schema import MainPage

if __name__ == "__main__":
    data = sys.stdin.read()
    print(json.dumps(MainPage(data).dict()))
    exit(0)
```
### curl

Dump parsed json to books.json file:

```shell
curl -s https://books.toscrape.com/catalogue/page-4.html | python stdin_adapter.py >> books.json
```

### any program languages

>> You can use any programming language that has a http client and can execute commands in the shell.

```go
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os/exec"
)

type Book struct {
	Available bool     `json:"available"`
	Image     string   `json:"image"`
	Name      string   `json:"name"`
	Price     float32  `json:"price"`
	Rating    byte     `json:"rating"`
	Url       string   `json:"url"`
	Urls      []string `json:"urls"`
}

type MainPage struct {
	Books []Book `json:"books"`
}

func main() {
	// Send HTTP request and read response body
	response, err := http.Get("https://books.toscrape.com/catalogue/page-3.html")
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	defer response.Body.Close()

	body, err := ioutil.ReadAll(response.Body)
	if err != nil {
		panic(err)
	}
    // send html body to scrape-schema script
	cmd := exec.Command("python3", "stdin_adapter.py")
	cmd.Stdin = bytes.NewBuffer(body)
	output, err := cmd.Output()
	if err != nil {
		panic(err)
	}

	var data MainPage

	err = json.Unmarshal(output, &data)
	if err != nil {
		panic(err)
	}
    fmt.Println(data.Books[0])
    fmt.Println(data.Books[1])
}
```

## rest-api adapter

A simple rest-api adapter written in flask. Just send a POST request and get json:

> restapi-adapter.py
```python
from flask import Flask, request, jsonify
from schema import MainPage

app = Flask(__name__)


@app.route('/parse_html', methods=['POST'])
def parse_html():
    html_doc = request.data  # Assuming the HTML document is sent in the request body
    # Parse the HTML document using BeautifulSoup
    data = MainPage(html_doc.decode('utf8')).dict()

    response = {'status': 200, 'data': data}
    return jsonify(response)


if __name__ == '__main__':
    app.run()

```

Usage:

```shell
curl -X POST -H "Content-Type: text/html" -d "$(curl -s https://books.toscrape.com/catalogue/page-4.html)" http://localhost:5000/parse_html
```