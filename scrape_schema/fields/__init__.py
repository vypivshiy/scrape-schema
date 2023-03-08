from typing import Optional, Any, Callable, Iterable

from ..base import BaseSchema, BaseField


class ParsedField(BaseField):
    def __init__(self,
                 field_attr_name: str,
                 *,
                 factory: Optional[Callable[[Any], Any]] = None,
                 **kwargs):
        super().__init__(factory=factory, **kwargs)
        self.attr_name = field_attr_name

    def parse(self, instance: BaseSchema, name: str, markup):
        value = getattr(instance, self.attr_name)
        if self.factory:
            value = self.factory(value)
        elif type_ := self._get_type(instance, name):
            value = type_(value)
        return value


class ParsedFieldList(ParsedField):
    def __init__(self,
                 field_attr_name: str,
                 *,
                 factory: Optional[Callable[[Any], Any]] = None,
                 **kwargs):
        super().__init__(factory=factory, **kwargs)
        self.attr_name = field_attr_name

    def parse(self, instance: BaseSchema, name: str, markup):
        values = getattr(instance, self.attr_name)
        if self.factory:
            values = self.factory(values)
        elif type_ := self._get_type(instance, name):
            values = [type_(val) for val in values]
        return values

