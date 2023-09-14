# Quickstart

The fields interface is similar to the original [parsel](https://parsel.readthedocs.io/en/latest/) API


=== "Annotated style"

    ```python
    from scrape_schema import BaseSchema, Parsel, Sc


    class Schema(BaseSchema):
        h1: Sc[str, Parsel().css('h1::text').get()]
        words: Sc[list[str], Parsel().xpath('//h1/text()').re(r'\w+')]
        urls: Sc[list[str], Parsel().css('ul > li').xpath('.//@href').getall()]
        sample_jmespath_1: Sc[str, Parsel().css(
            'script::text').jmespath("a").get()]
        sample_jmespath_2: Sc[list[str], Parsel().css(
            'script::text').jmespath("a").getall()]


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
    # {'h1': 'Hello, Parsel!',
    # 'words': ['Hello', 'Parsel'],
    # 'urls': ['http://example.com', 'http://scrapy.org'],
    # 'sample_jmespath_1': 'b',
    # 'sample_jmespath_2': ['b', 'c']}
    ```

=== "Attribute style"

    ```python
    # mypy: disable-error-code="assignment"
    from scrape_schema import BaseSchema, Parsel


    class Schema(BaseSchema):
        h1: str = Parsel().css('h1::text').get()
        words: list[str] = Parsel().xpath('//h1/text()').re(r'\w+')
        urls: list[str] = Parsel().css('ul > li').xpath('.//@href').getall()
        sample_jmespath_1: str = Parsel().css(
            'script::text').jmespath("a").get()
        sample_jmespath_2: list[str] = Parsel().css(
            'script::text').jmespath("a").getall()


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
    # {'h1': 'Hello, Parsel!',
    # 'words': ['Hello', 'Parsel'],
    # 'urls': ['http://example.com', 'http://scrapy.org'],
    # 'sample_jmespath_1': 'b',
    # 'sample_jmespath_2': ['b', 'c']}
    ```

=== "Original parsel"

    ```python
    from parsel import Selector


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
    selector = Selector(text=text)
    # Hello, Parsel!
    print(selector.css('h1::text').get())
    # ['Hello', 'Parsel']
    print(selector.xpath('//h1/text()').re(r'\w+'))

    # http://example.com
    # http://scrapy.org
    for li in selector.css('ul > li'):
        print(li.xpath('.//@href').get())
    # b
    print(selector.css('script::text').jmespath("a").get())
    # ['b', 'c']
    print(selector.css('script::text').jmespath("a").getall())
    ```
