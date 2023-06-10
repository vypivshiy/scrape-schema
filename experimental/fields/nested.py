
from experimental.base import BaseField, BaseSchema, SpecialMethods

from typing import get_args, List, Type, Optional, Any, Union
from experimental._typing import get_origin


class Nested(BaseField):
    def __init__(self, field: BaseField, markup_parser: Type = type(None)):
        self._crop_field = field
        self.Config.instance = markup_parser

    def parse(self, markup, type_: Optional[Type] = None) -> Any:
        if not type_:
            raise AttributeError("Nested required annotation")
        elif get_origin(type_) is list and (len(get_args(type_)) != 0 and issubclass(get_args(type_)[0], BaseSchema)):
            pass
        elif not issubclass(type_, BaseSchema):
            raise AttributeError(
                f"type should be List[BaseSchema] or BaseSchema, not {type_}"
            )

        markup = self._prepare_markup(markup)

        if len(get_args(type_)) != 0 and issubclass(get_args(type_)[0], BaseSchema):
            cls_schema = get_args(type_)[0]
        else:
            cls_schema = type_

        chunks = self._crop_field.parse(markup)
        if get_origin(type_) is list:
            return [cls_schema(chunk) for chunk in chunks]
        return cls_schema(chunks)


if __name__ == '__main__':
    from experimental.fields.soup import Soup, BeautifulSoup
    from experimental import Sc


    class NSchema(BaseSchema):
        class Config:
            parsers = {BeautifulSoup: {"features": "html.parser"}}
        a: Sc[float, Soup().find("a").get_text()]


    class Schema(BaseSchema):
        class Config:
            parsers = {BeautifulSoup: {"features": "html.parser"}}

        a_tag: Sc[NSchema, Nested(
            Soup().find("div").html(),
            BeautifulSoup
        )]
        a_tags: Sc[List[NSchema], Nested(Soup().find_all('a').html(), BeautifulSoup)]

    html = "<div><a>1</a></div>\n<a>2</a>\n<a>3</a>"
    print(Schema(html))
