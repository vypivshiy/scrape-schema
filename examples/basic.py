# mypy: disable-error-code="assignment"
from datetime import datetime
from uuid import uuid4

from scrape_schema import BaseSchema, Callback, Parsel, sc_param


class Schema(BaseSchema):
    # invoke simple functions to fields output
    id: str = Callback(lambda: str(uuid4()))
    date: str = Callback(lambda: str(datetime.today()))

    h1: str = Parsel().css("h1::text").get()
    # convert to upper case
    h1_upper: str = Parsel().css("h1::text").get().upper()
    # convert to lower case
    h1_lower: str = Parsel().css("h1::text").get().lower()

    words: list[str] = Parsel().xpath("//h1/text()").re(r"\w+")
    # alt solution split words
    words_2: list[str] = Parsel().xpath("//h1/text()").get().split()
    # join result by ' - ' string
    words_join: str = Parsel().xpath("//h1/text()").re(r"\w+").join(" AND ")
    urls: list[str] = Parsel().css("ul > li").xpath(".//@href").getall()
    # replace http protocol to https
    urls_https: list[str] = (
        Parsel()
        .css("ul > li")
        .xpath(".//@href")
        .getall()
        .replace("http://", "https://")
    )
    # you can modify output keys
    sample_jmespath_1: str = (
        Parsel(alias="jsn1").css("script::text").jmespath("a").get()
    )
    sample_jmespath_2: list[str] = (
        Parsel(alias="class").css("script::text").jmespath("a").getall()
    )

    # or calc json count values
    jsn_len: int = (
        Parsel(auto_type=False).css("script::text").jmespath("a").getall().count()
    )

    # or create fields with custom rule
    @sc_param
    def custom(self) -> str:
        return "hello world!"

    # you can add extra methods!
    def parse_urls(self):
        for url in self.urls:
            print(f"parse {url}")


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

schema = Schema(text)
# invoke custom method
schema.parse_urls()
# parse http://example.com
# parse http://scrapy.org
print(schema.dict())

# !!!field from @sc_param decorator!!!
#   vvvvvvvvvvvvvvvvvvvvvv
# {'custom': 'hello world!',
#  !!!simple functions callbacks output!!!
#  vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
# 'id': '6b66de7b-5b5f-445a-b8a7-3b17332c1ff5',
# 'date': '2023-09-29 18:47:03.638941',
# 'h1': 'Hello, Parsel!', 'h1_upper': 'HELLO, PARSEL!', 'h1_lower': 'hello, parsel!',
# 'words': ['Hello', 'Parsel'], 'words_2': ['Hello,', 'Parsel!'],
# 'words_join': 'Hello AND Parsel',
# 'urls': ['http://example.com', 'http://scrapy.org'],
# 'urls_https': ['https://example.com', 'https://scrapy.org'],
#         !!!changed key alias 'sample_jmespath_2' TO 'class'!!!
#               vvvvvvvvvvvvvvvvv
# 'jsn1': 'b', 'class': ['b', 'c'], 'jsn_len': 2}
