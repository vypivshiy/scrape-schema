from scrape_schema import BaseSchema, Parsel
from scrape_schema.field import DictField


class DictSchema(BaseSchema):
    urls: dict[str, str] = DictField().dict(
        Parsel().css("a ::text").getall(),  # key
        Parsel().css("a ::attr(href)").getall(),  # value
    )
    url: dict[str, str] = DictField().dict_one(
        Parsel().css("a ::text").get(), Parsel().css("a ::attr(href)").get()
    )


def test_dict_schema():
    HTML = """
    <a href="/foo">Foo</a>
    <a href="/bar">Baaaar</a>
    <a href="/baz">Bazed!</a>
    """
    assert DictSchema(HTML).dict() == {
        "urls": {"Foo": "/foo", "Baaaar": "/bar", "Bazed!": "/baz"},
        "url": {"Foo": "/foo"},
    }
