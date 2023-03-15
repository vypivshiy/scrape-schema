from typing import Optional, Callable, Type, Iterable, Any
from ..base import BaseField, BaseSchema

__all__ = ["Nested", "NestedList"]


class Nested(BaseField):
    def __init__(
        self,
        schema: Type[BaseSchema],
        *,
        crop_rule: Callable[[str], str],
        default: Optional[Any] = None,
        factory: Optional[Callable[[BaseSchema], Any]] = None,
    ):
        """A "glue" for BaseSchema objects. return one parsed BaseSchema object

        :param schema: BaseSchema type
        :param default: default value if parse is failed. Default NOne
        :param crop_rule: crop rule
        :param factory: factory function
        """
        super().__init__(factory=factory, default=default)

        self.schema = schema
        self.crop_rule = crop_rule
        self.factory = factory

    def parse(self, instance: BaseSchema, name: str, markup):
        new_markup = self.crop_rule(markup)
        if not isinstance(new_markup, str):
            new_markup = str(new_markup)
        if schema := self.schema(new_markup):
            return self._factory(schema)
        else:
            return self.default


class NestedList(BaseField):
    def __init__(
        self,
        schema: Type[BaseSchema],
        *,
        crop_rule: Callable[[str], Iterable[str]],
        default: Optional[Any] = None,
        factory: Optional[Callable[[list[BaseSchema]], Any]] = None,
    ):
        """A "glue" for BaseSchema objects. return list of parsed BaseSchema objects

        :param schema: BaseSchema type
        :param default: default value if parse is failed. Default NOne
        :param crop_rule: crop rule
        :param factory: factory function
        """
        super().__init__(default=default)
        self.schema = schema
        self.factory = factory
        self.crop_rule = crop_rule

    def parse(self, instance: BaseSchema, name: str, markup) -> list[BaseSchema]:
        new_markups = self.crop_rule(markup)
        schemas: list[BaseSchema] = [self.schema(n_mk) for n_mk in new_markups]
        return self._factory(schemas) if all(schemas) else self.default
