import pytest
from selectolax.parser import HTMLParser, Node

from scrape_schema.callbacks.slax import (
    crop_by_slax,
    crop_by_slax_all,
    get_attr,
    get_text,
    replace_text,
)


def test_crop_by_slax():
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
    assert crop_by_slax("p")(markup) == "<p>First paragraph.</p>"
    assert (
        crop_by_slax("#content")(markup)
        == '<div id="content">\n                <p>First paragraph.</p>\n                <p>Second paragraph.</p>\n            </div>'
    )


def test_crop_by_slax_all():
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
    assert crop_by_slax_all("p")(markup) == [
        "<p>First paragraph.</p>",
        "<p>Second paragraph.</p>",
    ]


def test_get_attr():
    node = HTMLParser('<a id="1" class="thing"></a>').css_first("a")

    assert get_attr("id")(node) == "1"
    assert get_attr("class")(node) == "thing"
    assert get_attr("href", default=None)(node) is None
    assert get_attr("href")(5) == 5


def test_replace_text():
    node = HTMLParser("<p>Hello, world!</p>").css_first("p")
    assert replace_text("world", "Earth")(node) == "Hello, Earth!"
    assert replace_text("world", "Earth", 0)(node) == "Hello, world!"
    assert replace_text("o", "O")(5) == 5


def test_get_text():
    node = HTMLParser("  <p>  Hello, world!  </p>  ").css_first("p")
    assert get_text()(node) == "  Hello, world!  "
    assert get_text(strip=True)(node) == "Hello, world!"
    assert get_text(separator=" ")(5) == 5
