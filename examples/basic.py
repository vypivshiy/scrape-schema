from scrape_schema import BaseSchema, Parsel, Sc


class Schema(BaseSchema):
    text: Sc[str, Parsel().css("h1::text").get()]
    words: Sc[list[str], Parsel().xpath("//h1/text()").re(r"\w+")]
    urls: Sc[list[str], Parsel().css("ul > li").xpath(".//@href").getall()]
    sample_jmespath_1: Sc[str, Parsel().css("script::text").jmespath("a").get()]
    sample_jmespath_2: Sc[
        list[str], Parsel().css("script::text").jmespath("a").getall()
    ]


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
# {'text': 'Hello, Parsel!',
# 'words': ['Hello', 'Parsel'],
# 'urls': ['http://example.com', 'http://scrapy.org'],
# 'sample_jmespath_1': 'b',
# 'sample_jmespath_2': ['b', 'c']}
