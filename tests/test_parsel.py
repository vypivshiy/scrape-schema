import pytest

from tests.fixtures import HTML

from scrape_schema import Parsel


def test_stack():
    p = Parsel()
    assert len(p._stack_methods) == 0
    p.xpath("//a").css("c > b")
    assert len(p._stack_methods) == 2


def test_xpath():
    assert Parsel().xpath("//h1").get().sc_parse(HTML) == "<h1>Hello, Parsel!</h1>"


def test_raw_text():
    TEXT = "test123"
    text_1 = Parsel(raw=True).sc_parse(TEXT)
    text_2 = Parsel().raw_text.sc_parse(TEXT)
    text_3 = Parsel().xpath("//body/p/text()").get().sc_parse(TEXT)
    text_4 = Parsel().css("body > p::text").get().sc_parse(TEXT)
    assert text_1 == text_2 == text_3 == text_4


def test_css():
    assert Parsel().css("body > h1").get().sc_parse(HTML) == "<h1>Hello, Parsel!</h1>"


def test_attrib_get():
    assert (
        Parsel().xpath("//li/a").attrib.get("href").sc_parse(HTML)
        == "http://example.com"
    )


def test_attrib_keys():
    assert list(Parsel().xpath("//li/a").attrib.keys().sc_parse(HTML))[0] == "href"


def test_attrib_values():
    assert (
        list(Parsel().xpath("//li/a").attrib.values().sc_parse(HTML))[0]
        == "http://example.com"
    )


def test_attrib_items():
    # print(list(Parsel().xpath("//li/a").attrib.items().sc_parse(HTML)))
    assert list(Parsel().xpath("//li/a").attrib.items().sc_parse(HTML)) == [
        ("href", "http://example.com")
    ]


def test_re():
    assert Parsel().xpath("//li/a").re(r'[a-zA-Z]+').sc_parse(HTML) == [
        'a', 'href', 'http', 'example', 'com', 'Link', 'a', 'a', 'href', 'http', 'scrapy', 'org', 'Link', 'a']


def test_getall():
    assert Parsel().xpath("//li/a/@href").getall().sc_parse(HTML) == ['http://example.com', 'http://scrapy.org']


def test_jmespath():
    assert Parsel().css('script::text').jmespath("a").getall().sc_parse(HTML) == ['b', 'c']


def test_failed_attrib():
    with pytest.raises(TypeError):
        Parsel().xpath("//li/a").get(key="href")


def test_failed_get():
    with pytest.raises(TypeError):
        Parsel().xpath("//li/a").get(key="href", default=0)