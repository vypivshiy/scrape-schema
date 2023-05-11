"""Nested fields for create BaseSchema objects"""
from typing import Any, Callable, List, Optional, Type, Union

from scrape_schema._logger import logger

from ..base import BaseField, BaseSchema  # type: ignore

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
    ) -> Union[BaseSchema, Any]:
        logger.info(
            "{}.{} start extract value. Field attrs: schema={}, crop_rule={}, factory={}",
            instance.__schema_name__,
            self.__class__.__name__,
            self._schema.__name__,
            self.crop_rule,
            self.factory,
        )
        markup = self._parse(markup)
        value = self._schema.from_crop_rule(markup, crop_rule=self.crop_rule)
        logger.debug("{}.{} create schema: {}", instance.__schema_name__, name, value)
        return self._factory(value)

    def extract(self, markup: Any, *, type_: Optional[Type] = None) -> None:
        raise NotImplementedError("Method `extract` not allowed in Nested field")


class NestedList(BaseNested):
    def __init__(
        self,
        schema: Type[BaseSchema],
        *,
        crop_rule: Callable[[str], List[str]],
        factory: Optional[Callable[[List[BaseSchema]], Any]] = None,
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
    ) -> Union[List[BaseSchema], Any]:
        logger.info(
            "{}.{} start extract value. Field attrs: schema={}, crop_rule={}, factory={}",
            instance.__schema_name__,
            self.__class__.__name__,
            self._schema.__name__,
            self.crop_rule,
            self.factory,
        )
        markup = self._parse(markup)
        value = self._schema.from_crop_rule_list(markup, crop_rule=self.crop_rule)
        logger.debug("{}.{} create schemas: {}", instance.__schema_name__, name, value)
        return self._factory(value)

    def extract(self, markup: Any, *, type_: Optional[Type] = None) -> None:
        raise NotImplementedError("Method `extract` not allowed in NestedList field")
