from scrape_schema import Parsel

HTML = """
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


def test_stack():
    p = Parsel()
    assert len(p._stack_methods) == 0
    p.xpath("//a").css("c > b")
    assert len(p._stack_methods) == 2


def test_xpath_raw_tag():
    html = "<div> test case </div>"
    assert Parsel().xpath("//div").get().sc_parse(html) == "<div> test case </div>"


def test_raw_text():
    TEXT = "test123"
    text_1 = Parsel(raw=True).sc_parse(TEXT)
    text_2 = Parsel().raw_text.sc_parse(TEXT)
    text_3 = Parsel().xpath("//body/p/text()").get().sc_parse(TEXT)
    text_4 = Parsel().css("body > p::text").get().sc_parse(TEXT)
    assert text_1 == text_2 == text_3 == text_4
