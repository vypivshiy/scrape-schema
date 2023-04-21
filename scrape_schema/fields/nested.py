"""Nested fields for create BaseSchema objects"""

from typing import Any, Callable, Optional, Type

from ..base import BaseField, BaseSchema

__all__ = ["BaseNested", "Nested", "NestedList"]


class BaseNested(BaseField):
    def _parse(self, _: str) -> str:
        return _


class Nested(BaseNested):
    def __init__(
        self,
        schema: Type[BaseSchema],
        *,
        crop_rule: Callable[[str], str],
        factory: Optional[Callable[[BaseSchema], Any]] = None,
    ):
        """Nested - serialise markup part to `schema` object

        :param schema: schema class type
        :param crop_rule: function for crop markdown to part
        :param factory: function for convert to another type. Default convert to `schema`
        """
        super().__init__(factory=factory)
        self._schema = schema
        self.crop_rule = crop_rule

    def __call__(
        self, instance: BaseSchema, name: str, markup: str
    ) -> BaseSchema | Any:
        markup = self._parse(markup)
        value = self._schema.from_crop_rule(markup, crop_rule=self.crop_rule)
        return self._factory(value)


class NestedList(BaseNested):
    def __init__(
        self,
        schema: Type[BaseSchema],
        *,
        crop_rule: Callable[[str], list[str]],
        factory: Optional[Callable[[list[BaseSchema]], Any]] = None,
    ):
        """NestedList - convert markup parts to list of `schema` objects

        :param schema: BaseSchema type
        :param crop_rule: function for crop markup to parts
        :param factory: function for convert to another type. Default convert to `schema`
        """
        super().__init__(factory=factory)
        self.crop_rule = crop_rule
        self._schema = schema
        self.crop_rule = crop_rule

    def __call__(
        self, instance: BaseSchema, name: str, markup: str
    ) -> list[BaseSchema] | Any:
        markup = self._parse(markup)
        value = self._schema.from_crop_rule_list(markup, crop_rule=self.crop_rule)
        return self._factory(value)
