from __future__ import annotations
import warnings
from abc import ABC, abstractmethod
import copy
from types import NoneType, GenericAlias, UnionType
from typing import Type, Any, Optional, Callable, get_type_hints, get_args, Iterable, Sequence
import logging

from .exceptions import ParseFailAttemptsError, ValidationError

logger = logging.getLogger("scrape_schema")
logger.setLevel(logging.WARNING)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)


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

    @abstractmethod
    def _callback(self, value):
        ...


class BaseField(ABCField):
    __MARKUP_PARSER__: Optional[Type | Callable[[str, ...], Any]] = None

    def __init__(self, *,
                 default: Optional[Any] = None,
                 callback: Optional[Callable[[Any], ...]] = None,
                 validator: Optional[Callable[[Any], bool]] = None,
                 filter_: Optional[Callable[[Any], bool]] = None,
                 factory: Optional[Callable[[Any], Any]] = None,
                 **kwargs):
        self.callback = callback
        self.default = default
        self.validator = validator
        self.filter_ = filter_
        self.factory = factory

    @abstractmethod
    def parse(self, instance: BaseSchema, name: str, markup):
        pass

    def _validate(self, value) -> bool:
        if self.validator:
            logger.debug("Validate `%s` by %s[%s]", value, self.validator.__name__, type(self.validator).__name__)
            return self.validator(value)
        return True

    def _filter(self, value) -> bool:
        if self.filter_:
            logger.debug("Filter `%s` by %s[%s]", value, self.filter_.__name__, type(self.filter_).__name__)
            return self.filter_(value)
        return True

    def _filter_process(self, values):
        if isinstance(values, Sequence) and not isinstance(values, str):
            return list(filter(self._filter, values))
        return values

    def _factory(self, value):
        if self.factory:
            logger.debug("Factory `%s` by %s[%s]", value, self.factory.__name__, type(self.factory).__name__)
            return self.factory(value)
        return value

    def _raise_validator(self, instance: BaseSchema, name: str, value) -> None:
        if instance.__VALIDATE__ and not self._validate(value):
            logger.error("Opps! Failing validate %s.%s=%s", instance.__class__.__name__, name, value)
            raise ValidationError(
                f"Validate {instance.__class__.__name__}.{name} failing. "
                f"Value passed: `{value}`")

    def _typing(self, instance: BaseSchema, name: str, value):
        if instance.__AUTO_TYPING__ and not self.factory and (types_ := self._get_type(instance, name)):
            # NoneType
            if value in (None, [], {}, "", 0):
                return None if type(None) in types_ else types_[0](value)
            elif isinstance(value, Iterable) and not isinstance(value, str):
                # get first type TODO write more smart algoritm
                type_ = types_[0]
                value = [type_(val) for val in value]
            else:
                value = types_[0](value)
        return value

    def _callback(self, value):
        if isinstance(value, Sequence) and not isinstance(value, str):
            value = [self.callback(val) for val in value]
        else:
            value = self.callback(value)
        return value

    @staticmethod
    def _get_type(instance: BaseSchema, name: str) -> Optional[tuple[Type, ...]]:
        if not (types_ := get_type_hints(instance).get(name)):
            return None
        logger.debug("Get first type: %s", types_.__name__)
        if isinstance(types_, NoneType):
            return None
        elif isinstance(types_, (GenericAlias, UnionType)):
            types_ = get_args(types_)
            logger.debug("Extract types: %s", [t.__name__ for t in types_])
        elif (optional_types := get_args(types_)) and optional_types:
            types_ = optional_types
            logger.debug("Extract OPTIONAL type: %s", [t.__name__ for t in types_])
        if not isinstance(types_, tuple):
            types_ = (types_, )
        return types_

    def __call__(self, instance: BaseSchema, name: str, markup):
        logger.debug("Parse `%s.%s`: markup[%s]",
                     instance.__class__.__name__,
                     name,
                     markup.__class__.__name__)
        value = self.parse(instance, name, markup)
        logger.debug("`%s.%s: %s = %s`", instance.__class__.__name__, name, type(value).__name__, str(value))
        return value

    def __deepcopy__(self, _):
        return copy.copy(self)


class BaseSchema(ABCSchema):
    """The base class of field processing.


    Attributes:
        __MARKUP_PARSERS__: dict[Type, dict[str, Any]] - dict of a markup parsers classes. Default empty dict
        key - Type (not initialized class) parser. - value - dict of kwargs params

        Example: __MARKUP_PARSERS__ = {BeautifulSoap: {"features": "lxml"}}


        __AUTO_TYPING__: bool - usage typing from annotations. Default True


        __VALIDATE__: bool - usage validator rules in fields. Default False


        __MAX_FAILS_COUNTER__: int - Limit of unsuccessfully parsed fields (checks against the default value) . Default -1

        If the value is negative - this feature is disabled.

        If it is 0 - at the first error it causes an error

        If equal to 1 - with two errors causes an error

        If equal to N - at N errors causes an error

    """
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
        """

        :param markup: any string text
        """
        logger.info("%s start parse", self.__class__.__name__)
        _init_markups = {
            cls_type: cls_type(markup, **params)
            for cls_type, params in self.__MARKUP_PARSERS__.items()
        }
        self.__fields__ = copy.deepcopy(self._get_fields())
        logger.info("Get %i fields", len(self.__fields__.keys()))
        _fails = 0
        for name, field in self.__fields__.items():
            if not field.__MARKUP_PARSER__:
                value = field(self, name, markup)
            elif parser := _init_markups.get(field.__MARKUP_PARSER__):
                value = field(self, name, parser)
            else:
                try:
                    raise TypeError(f"{field.__MARKUP_PARSER__.__name__} not found in "
                                    f"{self.__class__.__name__}.__MARKUP_PARSERS__.")
                except TypeError as e:
                    logger.exception(e)
                    raise e
            logger.info("%s.%s[%s] = %s", self.__class__.__name__, name, field.__class__.__name__, value)
            # calc failed parsed rows
            if self.__MAX_FAILS_COUNTER__ >= 0 and hasattr(field, "default") and value == field.default:
                _fails += 1
                logger.warning("[%i] Failed parse `%s.%s` by `%s`, set `%s`",
                               _fails, self.__class__.__name__, name, field.__class__.__name__, value)
                warnings.warn(f"[{_fails}] Failed parse `{self.__class__.__name__}.{name}` "
                              f"by {field.__class__.__name__} field, set `{value}`.",
                              stacklevel=2,
                              category=RuntimeWarning)
                if _fails > self.__MAX_FAILS_COUNTER__:
                    raise ParseFailAttemptsError(f"{_fails} of {len(self.__fields__.keys())} "
                                                 "field failed parse.")
            setattr(self, name, value)
        logger.info("%s done! Fields fails: %i", self.__class__.__name__, _fails)

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
        """convert schema object to python dict"""
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
