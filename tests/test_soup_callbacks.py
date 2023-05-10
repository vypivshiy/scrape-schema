import pytest
from bs4 import Tag

from scrape_schema.callbacks.soup import (
    crop_by_selector,
    crop_by_selector_all,
    crop_by_tag,
    crop_by_tag_all,
    element_to_dict,
    get_attr,
    get_text,
    replace_text,
)


def test_element_to_dict():
    assert element_to_dict("<p>") == {"name": "p", "attrs": {}}
    assert element_to_dict('<a id="1" class="thing">') == {
        "name": "a",
        "attrs": {"id": "1", "class": "thing"},
    }


def test_crop_class_attr():
    assert element_to_dict('<div class="spam egg">') == {"name": "div", "attrs": {"class": ["spam", "egg"]}}


def test_raise_element_to_dict():
    with pytest.raises(TypeError):
        element_to_dict("#content > p")


def test_replace_text():
    tag = Tag(name="p")
    tag.string = "Hello, world!"

    assert replace_text("world", "Earth")(tag) == "Hello, Earth!"
    assert replace_text("world", "Earth", 0)(tag) == "Hello, world!"
    assert replace_text("o", "O")(5) == 5


def test_get_text():
    tag = Tag(name="p")
    tag.string = "  Hello, world!  "

    tag_2 = Tag(name="p")
    assert get_text()(tag) == "  Hello, world!  "
    assert get_text(strip=True)(tag) == "Hello, world!"
    assert get_text(separator=" ")(5) == 5


def test_get_attr():
    tag = Tag(name="a", attrs={"id": "1", "class": "thing"})
    assert get_attr("id")(tag) == "1"
    assert get_attr("class")(tag) == "thing"
    assert get_attr("href", default=None)(tag) is None
    assert get_attr("href")(5) == 5


def test_crop_by_tag():
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
    assert crop_by_tag("<p>")(markup) == "<p>First paragraph.</p>"
    assert crop_by_tag({"name": "p"})(markup) == "<p>First paragraph.</p>"
    assert (
        crop_by_tag({"name": "div", "attrs": {"id": "content"}})(markup)
        == '<div id="content">\n<p>First paragraph.</p>\n<p>Second paragraph.</p>\n</div>'
    )


def test_crop_by_tag_all():
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
    assert crop_by_tag_all("<p>")(markup) == [
        "<p>First paragraph.</p>",
        "<p>Second paragraph.</p>",
    ]
    assert crop_by_tag_all({"name": "p"})(markup) == [
        "<p>First paragraph.</p>",
        "<p>Second paragraph.</p>",
    ]


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
        == '<div id="content">\n<p>First paragraph.</p>\n<p>Second paragraph.</p>\n</div>'
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
    assert crop_by_selector_all("#content")(markup) == [
        '<div id="content">\n'
        "<p>First paragraph.</p>\n"
        "<p>Second paragraph.</p>\n"
        "</div>"
    ]
