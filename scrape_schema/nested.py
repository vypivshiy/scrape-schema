from typing import Any, Optional, Type, get_args

from parsel import Selector, SelectorList

from scrape_schema._typing import get_origin
from scrape_schema.base import BaseField, BaseSchema


class Nested(BaseField):
    def __init__(
        self,
        field: BaseField,
        *,
        type_: Optional[Type] = None,
    ):
        super().__init__()
        self.auto_type = False
        self.type_ = type_
        self._crop_field = field

    def _prepare_markup(self, markup):
        raise NotImplementedError(
            "_prepare_markup not allowed in Nested"
        )  # pragma: no cover

    def sc_parse(self, markup) -> Any:
        if not self.type_:
            raise TypeError("Nested required annotation or `type_` param")
        elif get_origin(self.type_) is list and (
            len(get_args(self.type_)) != 0
            and issubclass(get_args(self.type_)[0], BaseSchema)
        ):
            pass
        elif not issubclass(self.type_, BaseSchema):
            raise TypeError(
                f"type should be List[BaseSchema] or BaseSchema, not {self.type_}"
            )

        if len(get_args(self.type_)) != 0 and issubclass(
            get_args(self.type_)[0], BaseSchema
        ):
            cls_schema = get_args(self.type_)[0]
        else:
            cls_schema = self.type_

        chunks = self._crop_field.sc_parse(markup)
        if isinstance(chunks, SelectorList) and get_origin(self.type_) is list:
            return [cls_schema(chunk.get()) for chunk in chunks]
        elif get_origin(self.type_) is list:
            return [cls_schema(chunk) for chunk in chunks]  # pragma: no cover
        elif isinstance(chunks, Selector) and get_origin(self.type_) is not list:
            return cls_schema(chunks.get())
        return cls_schema(chunks)  # pragma: no cover
