# Note: bs4 is not recommended: you will lose performance and core library functions!
from typing import Any

from bs4 import BeautifulSoup

from scrape_schema import BaseSchema, sc_param


class Schema(BaseSchema):
    def __init__(self, markup: Any):
        super().__init__(markup)
        self.soup = BeautifulSoup(markup, "lxml")

    @sc_param
    def h1(self):
        return self.soup.find("h1").text

    @sc_param
    def urls(self):
        return [li.find("a").get("href") for li in self.soup.find_all("li")]

    # I'm too lazy to write more :D


if __name__ == "__main__":
    text = """
            <html>
                <body>
                    <h1>Hello, Parsel!</h1>
                    <ul>
                        <li><a href="http://example.com">Link 1</a></li>
                        <li><a href="http://scrapy.org">Link 2</a></li>
                    </ul>
                    <script type="application/json">{"a": ["b", "c"]}</script>
                </body>
            </html>"""
    print(Schema(text).dict())
    # {'h1': 'Hello, Parsel!', 'urls': ['http://example.com', 'http://scrapy.org']}
