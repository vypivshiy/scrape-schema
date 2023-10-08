from scrape_schema import BaseSchema, Parsel, sc_param
from scrape_schema.field import DictField


class Schema(BaseSchema):
    # extract all elements
    urls: dict[str, str] = DictField().dict(
        Parsel().css("a ::text").getall(),  # key
        Parsel().css("a ::attr(href)").getall(),  # value
    )
    # extract one element
    url: dict[str, str] = DictField().dict_one(
        Parsel().css("a ::text").get(), Parsel().css("a ::attr(href)").get()
    )


class SchemaOld(BaseSchema):
    """same solution, but without Dict field"""

    @sc_param
    def urls(self):
        return dict(
            zip(
                self.__selector__.css("a ::text").getall(),
                self.__selector__.css("a ::attr(href)").getall(),
            )
        )

    @sc_param
    def url(self):
        return {
            self.__selector__.css("a ::text")
            .get(): self.__selector__.css("a ::attr(href)")
            .get()
        }


if __name__ == "__main__":
    HTML = """
    <a href="/foo">Foo</a>
    <a href="/bar">Baaaar</a>
    <a href="/baz">Bazed!</a>
    <a href="/secret"></a>
    """
    # <a href="/secret"></a>  secret tag will be ignored - text is not contains in attribute
    print(Schema(HTML).dict())
    # {'urls': {'Foo': '/foo', 'Baaaar': '/bar', 'Bazed!': '/baz'}, 'url': {'Foo': '/foo'}}
    print(SchemaOld(HTML).dict())
    # {'urls': {'Foo': '/foo', 'Baaaar': '/bar', 'Bazed!': '/baz'}, 'url': {'Foo': '/foo'}}
    assert Schema(HTML).dict() == SchemaOld(HTML).dict()  # Passed
