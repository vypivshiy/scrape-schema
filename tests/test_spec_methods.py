import pytest
from tests.fixtures import HTML, HTML_SCRIPT

from scrape_schema import Parsel


def test_fn():
    assert (
        Parsel().xpath("//body/h1/text()").get().fn(lambda s: s.upper()).sc_parse(HTML)
        == "HELLO, PARSEL!"
    )


def test_concat_l():
    assert (
        Parsel().xpath("//body/h1/text()").get().concat_l("+").sc_parse(HTML)
        == "+Hello, Parsel!"
    )


def test_concat_r():
    assert (
        Parsel().xpath("//body/h1/text()").get().concat_r("+").sc_parse(HTML)
        == "Hello, Parsel!+"
    )


def test_re_search():
    assert (
        Parsel().xpath("//body/h1/text()").get().re_search(r"(Hello)")[0].sc_parse(HTML)
        == "Hello"
    )


def test_re_search_groupdict():
    assert (
        Parsel()
        .xpath("//body/h1/text()")
        .get()
        .re_search(r"(?P<hello>Hello)", groupdict=True)
        .sc_parse(HTML)
    ) == {"hello": "Hello"}


def test_re_search_fail():
    with pytest.raises(TypeError):
        _ = (
            Parsel()
            .xpath("//body/h1/text()")
            .get()
            .re_search(r"(Hello)", groupdict=True)
            .sc_parse(HTML)
        ) == {"hello": "Hello"}


def test_re_findall():
    assert Parsel().xpath("//body/h1/text()").get().re_findall(r"(\w+)").sc_parse(
        HTML
    ) == ["Hello", "Parsel"]


def test_re_findall_groupdict():
    assert Parsel().xpath("//body/h1/text()").get().re_findall(
        r"(?P<word>\w+)", groupdict=True
    ).sc_parse(HTML) == [{"word": "Hello"}, {"word": "Parsel"}]


def test_re_findall_groupdict_fail():
    with pytest.raises(TypeError):
        Parsel().xpath("//body/h1/text()").get().re_findall(
            r"(\w+)", groupdict=True
        ).sc_parse(HTML)


def test_replace():
    # print(Parsel().xpath("//body/h1/text()").get().sc_replace("Hello,", "").sc_parse(HTML))
    assert (
        Parsel().xpath("//body/h1/text()").get().sc_replace("Hello", "").sc_parse(HTML)
        == ", Parsel!"
    )


def test_replace_list():
    assert Parsel().xpath("//li/a/@href").getall().sc_replace("http://", "").sc_parse(
        HTML
    ) == ["example.com", "scrapy.org"]


def test_concat_l_list():
    assert Parsel().xpath("//li/a/@href").getall().concat_l("=").sc_parse(HTML) == [
        "=http://example.com",
        "=http://scrapy.org",
    ]


def test_concat_r_list():
    assert Parsel().xpath("//li/a/@href").getall().concat_r("=").sc_parse(HTML) == [
        "http://example.com=",
        "http://scrapy.org=",
    ]


def test_chompjs():
    assert Parsel().xpath("//script/text()").get().chomp_js_parse().sc_parse(
        HTML_SCRIPT
    ) == {
        "key": "spam",
        "values": [1, 2, 3, 4, 5],
        "layer1": {"layer2": {"layer3": [None, None, True, False]}},
    }


def test_chompjs_all():
    assert list(
        Parsel()
        .xpath("//script/text()")
        .get()
        .chomp_js_parse_all()
        .sc_parse(HTML_SCRIPT)
    ) == [
        {
            "key": "spam",
            "values": [1, 2, 3, 4, 5],
            "layer1": {"layer2": {"layer3": [None, None, True, False]}},
        }
    ]
