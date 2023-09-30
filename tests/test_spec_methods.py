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


def test_split():
    assert Parsel(raw=True).split().sc_parse("test 123") == ["test", "123"]


def test_split_fail():
    with pytest.raises(TypeError):
        Parsel(raw=True).split().split().sc_parse("test 123 567")


def test_upper():
    assert Parsel(raw=True).upper().sc_parse("hello") == "HELLO"


def test_upper_list():
    assert Parsel(raw=True).split().upper().sc_parse("hello world") == [
        "HELLO",
        "WORLD",
    ]


def test_lower():
    assert Parsel(raw=True).lower().sc_parse("HELLO") == "hello"


def test_lower_list():
    assert Parsel(raw=True).split().lower().sc_parse("HELLO WORLD") == [
        "hello",
        "world",
    ]


def test_capitalize():
    assert Parsel(raw=True).capitalize().sc_parse("hello") == "Hello"


def test_capitalize_list():
    assert Parsel(raw=True).split().capitalize().sc_parse("hello world") == [
        "Hello",
        "World",
    ]


def test_count():
    assert Parsel(raw=True).count().sc_parse("hello") == 1


def test_count_list():
    assert Parsel(raw=True).split().count().sc_parse("hello world 123") == 3


def test_join():
    assert Parsel(raw=True).split().join(", ").sc_parse("test 123") == "test, 123"


def test_join_fail():
    with pytest.warns(RuntimeWarning):
        assert Parsel(raw=True).join(", ").sc_parse("test 123")


def test_strip():
    assert Parsel(raw=True).strip().sc_parse("  test 123  ") == "test 123"


def test_strip_list():
    assert Parsel(raw=True).split(",").strip().sc_parse("  test 123  ,  456  ") == [
        "test 123",
        "456",
    ]


def test_rstrip():
    assert Parsel(raw=True).rstrip().sc_parse("test 123  ") == "test 123"


def test_rstrip_list():
    assert Parsel(raw=True).split(",").rstrip().sc_parse("  test 123  ,  456  ") == [
        "test 123",
        "  456",
    ]


def test_lstrip():
    assert Parsel(raw=True).lstrip().sc_parse("  \n\ttest 123") == "test 123"


def test_lstrip_list():
    assert Parsel(raw=True).split(",").lstrip().sc_parse(",  test 123  ,  456  ") == [
        "",
        "test 123  ",
        "456",
    ]


def test_replace():
    assert Parsel(raw=True).replace("t", "").sc_parse("test123") == "es123"


def test_replace_one():
    assert Parsel(raw=True).replace("t", "", 1).sc_parse("test123") == "est123"


def test_replace_list():
    assert Parsel(raw=True).split().replace("t", "").sc_parse("test123 tta") == [
        "es123",
        "a",
    ]


def test_re_search():
    assert Parsel(raw=True).re_search(r"\d+")[0].sc_parse("test 123") == "123"


def test_re_search_groupdict():
    assert Parsel(raw=True).re_search(r"(?P<digit>\d+)", groupdict=True).sc_parse(
        "test 123"
    ) == {"digit": "123"}


def test_re_search_groupdict_fail():
    with pytest.raises(TypeError):
        Parsel(raw=True).re_search(r"\d+", groupdict=True)[0].sc_parse("test 123")


def test_re_search_list_fail():
    # expected string or bytes-like object
    with pytest.raises(TypeError):
        Parsel(raw=True).split(",").re_search(r"\d+")[0].sc_parse("test 123, some 44")


def test_re_findall():
    assert Parsel(raw=True).re_findall(r"\d+").sc_parse("test 100 120") == [
        "100",
        "120",
    ]


def test_re_findall_group():
    assert Parsel(raw=True).re_findall(r"(?P<digit>\d+)", groupdict=True).sc_parse(
        "test 100 120"
    ) == [{"digit": "100"}, {"digit": "120"}]


def test_re_findall_group_fail():
    with pytest.raises(TypeError):
        Parsel(raw=True).re_findall(r"\d+", groupdict=True).sc_parse("test 100 120")


def test_re_findall_value_fail():
    with pytest.raises(TypeError):
        Parsel(raw=True).split().re_findall(r"\d+").sc_parse("test 100 120")
