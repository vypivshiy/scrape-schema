import pytest
from parsel import Selector

from scrape_schema.callbacks.parsel import (
    crop_by_selector,
    crop_by_selector_all,
    crop_by_xpath,
    crop_by_xpath_all,
    get_attr,
    get_text,
    replace_text,
)


def test_get_text():
    sel = Selector(text="<p>  Hello, world!  </p>")
    assert get_text()(sel) == "  Hello, world!  "
    assert get_text(strip=True)(sel) == "Hello, world!"
    assert get_text()(5) == 5


def test_get_text_deep():
    sel = Selector(text="<p>  Hello, <a>world!  </a></p>")
    assert get_text(deep=True)(sel) == '  Hello, world!  '
    assert get_text(deep=True, strip=True)(sel) == 'Hello, world!'


def test_replace_text():
    sel = Selector(text="<p>Hello, world!</p>")
    assert replace_text("world", "Earth")(sel) == "Hello, Earth!"
    assert replace_text("world", "Earth", 0)(sel) == "Hello, world!"
    assert replace_text("o", "O")(5) == 5


def test_get_attr():
    sel = Selector(text='<a id="1" class="thing"></a>').css("a")
    assert get_attr("id")(sel) == "1"
    assert get_attr("class")(sel) == "thing"
    assert get_attr("href")(5) == 5


def test_crop_by_selector():
    markup = """
    <html>
        <head></head>
        <body>
            <div id="content">
                <p>First paragraph.</p>
                <p>Second paragraph.</p>
            </div>
        </body>
    </html>
    """
    assert crop_by_selector("p")(markup) == "<p>First paragraph.</p>"
    assert (
        crop_by_selector("#content")(markup)
        == '<div id="content">\n                <p>First paragraph.</p>\n                <p>Second paragraph.</p>\n            </div>'
    )


def test_crop_by_selector_all():
    markup = """
    <html>
        <head></head>
        <body>
            <div id="content">
                <p>First paragraph.</p>
                <p>Second paragraph.</p>
            </div>
        </body>
    </html>
    """
    assert crop_by_selector_all("p")(markup) == [
        "<p>First paragraph.</p>",
        "<p>Second paragraph.</p>",
    ]


def test_crop_by_xpath():
    markup = """
    <html>
        <head></head>
        <body>
            <div id="content">
                <p>First paragraph.</p>
                <p>Second paragraph.</p>
            </div>
        </body>
    </html>
    """
    assert crop_by_xpath("//p")(markup) == "<p>First paragraph.</p>"
    assert (
        crop_by_xpath("//*[@id='content']")(markup)
        == '<div id="content">\n                <p>First paragraph.</p>\n                <p>Second paragraph.</p>\n            </div>'
    )


def test_crop_by_xpath_all():
    markup = """
    <html>
        <head></head>
        <body>
            <div id="content">
                <p>First paragraph.</p>
                <p>Second paragraph.</p>
            </div>
        </body>
    </html>
    """
    assert crop_by_xpath_all("//p")(markup) == [
        "<p>First paragraph.</p>",
        "<p>Second paragraph.</p>",
    ]


def test_fail_crop_by_selector():
    with pytest.raises(AttributeError):
        assert crop_by_selector("a")("<p>First paragraph.</p>")


def test_fail_crop_by_xpath():
    with pytest.raises(AttributeError):
        assert crop_by_xpath("//a")("<p>First paragraph.</p>")
