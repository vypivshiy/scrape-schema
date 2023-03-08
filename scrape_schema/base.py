from __future__ import annotations

import warnings
from abc import ABC, abstractmethod
import copy
from types import NoneType, GenericAlias, UnionType
from typing import Type, Any, Optional, Callable, get_type_hints, get_args

from .exceptions import ParseFailAttemptsError


class ABCSchema(ABC):

    @classmethod
    @abstractmethod
    def parse(cls, markup):
        ...

    @classmethod
    @abstractmethod
    def parse_many(cls, markups):
        ...


class ABCField(ABC):
    @abstractmethod
    def parse(self, instance: BaseSchema, name: str, markup):
        ...

    @abstractmethod
    def _validate(self, value) -> bool:
        ...

    @abstractmethod
    def _filter(self, value) -> bool:
        ...

    @abstractmethod
    def _factory(self, value):
        ...


class BaseField(ABCField):
    __MARKUP_PARSER__: Optional[Type | Callable[[str, ...], Any]] = None

    def __init__(self, *,
                 default: Optional[Any] = None,
                 validator: Optional[Callable[[Any], bool]] = None,
                 filter_: Optional[Callable[[Any], bool]] = None,
                 factory: Optional[Callable[[Any], Any]] = None,
                 **kwargs):
        self.default = default
        self.validator = validator
        self.filter_ = filter_
        self.factory = factory

    @abstractmethod
    def parse(self, instance: BaseSchema, name: str, markup):
        pass

    def _validate(self, value) -> bool:
        return bool(not self.validator or self.validator(value))

    def _filter(self, value) -> bool:
        return bool(not self.filter_ or self.filter_(value))

    def _factory(self, value):
        return self.factory(value) if self.factory else value

    def _raise_validator(self, instance: BaseSchema, name: str, value) -> None:
        if instance.__VALIDATE__ and not self._validate(value):
            raise ParseFailAttemptsError(
                f"Validate {instance.__class__.__name__}.{name} failing. "
                f"Value passed: `{value}`")

    @staticmethod
    def _get_type(instance: BaseSchema, name: str) -> Optional[Type]:
        if type_ := get_type_hints(instance).get(name):
            if isinstance(type_, NoneType):
                return None
            elif isinstance(type_, (GenericAlias, UnionType)):
                # get first type like list[str]
                type_ = get_args(type_)[0]
            # handle Optional[...] type
            elif (optional_type := get_args(type_)) and optional_type:
                type_ = optional_type[0]
            # ignore if type is dict or list
            try:
                return None if issubclass(type_, (dict, list)) else type_
            except TypeError:
                warnings.warn(
                    f"Failed get types from `{type_}` for {instance.__class__.__name__}.{name}, "
                    f"return None",
                    stacklevel=2, category=RuntimeWarning
                )
                return None
        return None

    def __call__(self, instance: BaseSchema, name: str, markup):
        return self.parse(instance, name, markup)

    def __deepcopy__(self, _):
        return copy.copy(self)


class BaseSchema(ABCSchema):
    __MARKUP_PARSERS__: dict[Type[Any], dict[str, Any]] = {}
    __AUTO_TYPING__: bool = True
    __VALIDATE__: bool = False
    __MAX_FAILS_COUNTER__: int = -1

    @staticmethod
    def _is_dunder(name: str) -> bool:
        return name.startswith("__") and name.endswith("__")

    @staticmethod
    def _is_field(obj) -> bool:
        return isinstance(obj, BaseField)

    @classmethod
    def _get_fields(cls) -> dict[str, BaseField]:
        return {
            name: field for name, field in cls.__dict__.items()
            if not cls._is_dunder(name) and cls._is_field(field)
        }

    def __init__(self, markup: str):
        _init_markups = {
            cls_type: cls_type(markup, **params)
            for cls_type, params in self.__MARKUP_PARSERS__.items()
        }
        self.__fields__ = copy.deepcopy(self._get_fields())

        _fails = 0
        for name, field in self.__fields__.items():
            if not field.__MARKUP_PARSER__:
                value = field(self, name, markup)
            elif parser := _init_markups.get(field.__MARKUP_PARSER__):
                value = field(self, name, parser)
            else:
                raise TypeError(f"{field.__MARKUP_PARSER__.__name__} not found in __MARKUP_PARSERS__")
            # calc failed parsed rows
            if self.__MAX_FAILS_COUNTER__ >= 0:
                if hasattr(field, "default") and value == field.default:
                    _fails += 1
                if _fails >= self.__MAX_FAILS_COUNTER__:
                    raise RuntimeError(f"{self.__MAX_FAILS_COUNTER__} of {len(self.__fields__.keys())} "
                                       "field failed parse")
            setattr(self, name, value)

    @classmethod
    def parse(cls, markup):
        return cls(markup)

    @classmethod
    def parse_many(cls, markups):
        return [cls(markup) for markup in markups]

    @staticmethod
    def _to_dict(value):
        if isinstance(value, BaseSchema):
            return value.dict()

        elif isinstance(value, list):
            if all(isinstance(val, BaseSchema) for val in value):
                return [val.dict() for val in value]

        elif isinstance(value, dict):
            if all(isinstance(val, BaseSchema) for val in value.values()):
                return {k: v.dict() for k, v in value.items()}
        return value

    def dict(self) -> dict[str, Any]:
        return {
            k: self._to_dict(v)
            for k, v in self.__dict__.items()
            if not self._is_dunder(k)
        }

    def __bool__(self):
        return all(list(self.dict().values()))

    def __repr__(self):
        rpr = f"{self.__class__.__name__}("
        rpr += (
                ", ".join(
                    [
                        f"{k}<{type(v).__name__}>={v}"
                        for k, v in self.__dict__.items()
                        if not self._is_dunder(k)
                    ]
                )
                + ")"
        )
        return rpr
