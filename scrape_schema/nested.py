from typing import TYPE_CHECKING, Any, List, Optional, Type, Union, get_args

from parsel import Selector, SelectorList

from scrape_schema._typing import get_origin
from scrape_schema.base import BaseField, BaseSchema

if TYPE_CHECKING:
    from scrape_schema._protocols import SpecialMethodsProtocol


class Nested(BaseField):
    """Allows you to nest a Schema inside a field.

    Example:

    """

    # dirty hack for guarantee detect Nested fields in Schema class
    __I_AM_NESTED_FIELD__: bool = True

    def __init__(
        self,
        # Special method protocol for avoid typing errors
        field: Union[BaseField, "SpecialMethodsProtocol"],
        *,
        type_: Optional[Union[Type[BaseSchema], Type[List[BaseSchema]]]] = None,
    ):
        """Nested field

        :param field: Field method provide crop documents to parts logic
        :param type_: Schema type. Auto set if this field in BaseSchema class scope
        """
        super().__init__()
        self.auto_type = False
        self.type_ = type_
        self._crop_field = field

    def _prepare_markup(self, markup):
        raise NotImplementedError(
            "`_prepare_markup` method not allowed in Nested class"
        )  # pragma: no cover

    def sc_parse(self, markup) -> Any:
        if not self.type_:
            raise TypeError("Nested required annotation in schema or `type_` param")
        elif get_origin(self.type_) is list and (
            len(get_args(self.type_)) != 0
            and issubclass(get_args(self.type_)[0], BaseSchema)
        ):
            pass
        elif not issubclass(self.type_, BaseSchema):
            raise TypeError(
                f"Type should be `list[BaseSchema]` or `BaseSchema`, not {self.type_}"
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
