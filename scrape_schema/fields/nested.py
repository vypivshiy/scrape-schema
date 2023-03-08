from typing import Optional, Any, Callable, Type, Iterable

from ..base import BaseField, BaseSchema

__all__ = [
    "Nested",
    "NestedList"
]


class Nested(BaseField):
    def __init__(self,
                 schema: Type[BaseSchema],
                 *,
                 default: Optional[Any] = None,
                 crop_rule: Callable[[str], str] = ...,
                 factory: Optional[Callable[[BaseSchema], Any]] = None
                 ):
        super().__init__(factory=factory, default=default)
        self.schema = schema
        self.crop_rule = crop_rule
        self.factory = factory

    def parse(self, instance: BaseSchema, name: str, markup):
        new_markup = self.crop_rule(markup)
        if not isinstance(new_markup, str):
            new_markup = str(new_markup)
        if schema := self.schema(new_markup):
            return self.factory(schema) if self.factory else schema
        else:
            return self.default


class NestedList(Nested):
    def __init__(self,
                 schema: Type[BaseSchema],
                 *,
                 default: Optional[Any] = None,
                 crop_rule: Callable[[str], Iterable[str]] = ...,
                 factory: Optional[Callable[[list[BaseSchema]], Any]] = None
                 ):
        super().__init__(schema=schema, default=default)
        self.factory = factory
        self.crop_rule = crop_rule

    def parse(self, instance: BaseSchema, name: str, markup) -> list[BaseSchema]:
        new_markups = self.crop_rule(markup)
        schemas: list[BaseSchema] = [self.schema(n_mk) for n_mk in new_markups]
        if not all(schemas):
            return self.default
        return self.factory(schemas) if self.factory else schemas
