from typing import Any, Optional, Type, get_args

from scrape_schema2._typing import get_origin
from scrape_schema2.base import BaseField, BaseSchema


class Nested(BaseField):
    def __init__(
        self,
        field: BaseField,
        *,
        type_: Optional[Type] = None,
        markup_parser: Type = type(None),
    ):
        super().__init__()
        self.auto_type = False
        self.type_ = type_
        self._crop_field = field
        self.Config.instance = markup_parser

    def sc_parse(self, markup) -> Any:
        if not self.type_:
            raise AttributeError("Nested required annotation")
        elif get_origin(self.type_) is list and (
            len(get_args(self.type_)) != 0
            and issubclass(get_args(self.type_)[0], BaseSchema)
        ):
            pass
        elif not issubclass(self.type_, BaseSchema):
            raise AttributeError(
                f"type should be List[BaseSchema] or BaseSchema, not {self.type_}"
            )

        # self.Config = self._crop_field.Config
        # markup = self._prepare_markup(markup)

        if len(get_args(self.type_)) != 0 and issubclass(
            get_args(self.type_)[0], BaseSchema
        ):
            cls_schema = get_args(self.type_)[0]
        else:
            cls_schema = self.type_

        chunks = self._crop_field.sc_parse(markup)
        if get_origin(self.type_) is list:
            return [cls_schema(chunk) for chunk in chunks]
        return cls_schema(chunks)
