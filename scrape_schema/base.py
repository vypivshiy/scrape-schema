from __future__ import annotations

import sys
import warnings
from abc import abstractmethod, ABC
from typing import Any, Type, ByteString, Iterable, TypeVar, get_type_hints, get_args, get_origin, Optional, Union, \
    Callable, TypeAlias, ClassVar
from types import NoneType
import logging

# python < 3.10
try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

# python < 3.11
try:
    from typing import Self  # type: ignore
except ImportError:
    try:
        from typing_extensions import Self  # type: ignore
    except ImportError:
        # very old python
        Self: TypeAlias = 'BaseSchema'  # type: ignore

from scrape_schema.exceptions import MarkupNotFoundError, ParseFailAttemptsError

logger = logging.getLogger("scrape_schema")
logger.setLevel(logging.DEBUG)
_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_stdout_handler = logging.StreamHandler()
_stdout_handler.setFormatter(_formatter)
logger.addHandler(_stdout_handler)

T = TypeVar("T")
MARKUP_TYPE: TypeAlias = str | Any


class ABCField(ABC):
    @abstractmethod
    def _parse(self, markup: MARKUP_TYPE) -> Any:
        ...

    @abstractmethod
    def _filter(self, value: T) -> bool:
        ...

    @abstractmethod
    def _factory(self, value: T) -> T:
        ...

    @abstractmethod
    def _callback(self, value: T) -> T:
        ...

    @abstractmethod
    def _typing(self, instance: BaseSchema, name: str, value: T) -> T:
        ...


class TypeCaster:
    @staticmethod
    def _is_iterable_and_not_string_type(value_type: Type) -> bool:
        return (issubclass(value_type, Iterable)
                and not issubclass(value_type, (ByteString, str)))

    @staticmethod
    def _is_iterable_and_not_string_value(value: T) -> bool:
        return isinstance(value, Iterable) and not (
            isinstance(value, (ByteString, str))
        )

    def _cast_type(self, type_annotation: Type, value: Any) -> Any:
        value_type = type(value)
        type_origin = get_origin(type_annotation)
        type_args = get_args(type_annotation)

        # skip if value type is annotated correct or is missing
        if value_type is type_annotation:
            logger.debug("`%s` value `%s` has same type, skip cast",
                         self.__class__.__name__, value)
            return value

        logger.debug("`%s` Cast type start. Origin: `%s[%s]`, Annotation `%s` with args `%s`",
                     self.__class__.__name__, value, value_type.__name__, type_origin, type_args)

        # Optional
        if type_origin is Union and NoneType in type_args:
            # get optional type, set
            if value:
                logger.debug('`%s` Cast Optional type `%s(%s)`',
                             self.__class__.__name__, value, type_args[0])
                if optional_args := get_args(type_args[0]):
                    # Optional[list[T]]
                    if isinstance(value, list):
                        return [optional_args[0](v) for v in value]
                    # Optional[dict[K, V]]
                    elif isinstance(value, dict):
                        k_type, v_type = optional_args
                        return {k_type(k): v_type(v) for k, v in value.items()}
                return type_args[0](value)
            else:
                logger.debug('`%s` Cast Optional type, value `%s` is False',
                             self.__class__.__name__, value)
                return value

        # dict, list
        elif type_origin:
            if issubclass(type_origin, dict) and isinstance(value, dict):
                logger.debug("`%s` Cast dict type: `%s(key)`, `%s(value)`",
                             self.__class__.__name__, type_args[0], type_args[1])
                # get dict set
                return {type_args[0](k): type_args[1](v) for k, v in value.items()}

            elif self._is_iterable_and_not_string_type(type_origin) and isinstance(value, list):
                logger.debug("`%s` Cast list items to `%s(item)`",
                             self.__class__.__name__, type_args[0])
                # get list, set
                return [type_args[0](i) for i in value]

        else:
            # single type
            logger.debug('Cast `%s`  `%s(%s)`', self.__class__.__name__, type_annotation.__name__, value)
            return type_annotation(value)


class MetaField:
    parser: ClassVar[Optional[Type[Any]]] = None


class BaseField(ABCField, TypeCaster):
    class Meta(MetaField):
        pass

    def __init__(self, *,
                 default: Optional[Any] = None,
                 filter_: Optional[Callable[[T], bool]] = None,
                 callback: Optional[Callable[..., T]] = None,
                 factory: Optional[Callable[..., T]] = None,
                 **kwargs
                 ):
        self.factory = factory
        self.callback = callback
        self.filter_ = filter_
        self.default = default

    @abstractmethod
    def _parse(self, markup: MARKUP_TYPE) -> Any:
        ...

    def __call__(self, instance: BaseSchema, name: str, markup: MARKUP_TYPE) -> Any:
        logger.debug("%s.%s[%s] Start parse",
                     instance.__class__.__name__, name, self.Meta.parser or 'str')
        value = self._parse(markup)
        logger.debug("`%s.%s = %s` raw value(s)", instance.__class__.__name__, name, value)
        if not value:
            logger.debug("`%s.%s` value not found, set default `%s` value",
                         instance.__class__.__name__, name, self.default)
            value = self.default

        if self._is_iterable_and_not_string_value(value):
            value = self._filter(value)
            logger.debug('`%s.%s = %s` filter result list',
                         instance.__class__.__name__, name, value)

        value = self._callback(value)
        if self.callback:
            logger.debug('`%s.%s = %s` callback', instance.__class__.__name__, name, value)
        if self.factory:
            value = self._factory(value)
            logger.debug('`%s.%s = %s` factory value',
                         instance.__class__.__name__, name, value)
        else:
            value = self._typing(instance, name, value)
            logger.debug('`%s.%s = %s` cast typing value',
                         instance.__class__.__name__, name, value)
        return value

    def _filter(self, value: T) -> Any:
        if self.filter_:
            if isinstance(value, list):
                return list(filter(self.filter_, value))
            elif isinstance(value, dict):
                return {k: v for k, v in value.items() if self.filter_(v)}
        return value

    def _factory(self, value: T) -> Any:
        return self.factory(value) if self.factory else value

    def _callback(self, value: T) -> Any:
        if not self.callback:
            return value
        if not self._is_iterable_and_not_string_value(value):
            return self.callback(value)
        if isinstance(value, list):
            return [self.callback(i) for i in value]
        elif isinstance(value, dict):
            return {k: self.callback(v) for k, v in value}
        return self.callback(value)

    def _typing(self, instance: BaseSchema, name: str, value: T) -> Any:
        if instance.Meta.type_cast:
            if type_annotation := instance.__fields_annotations__.get(name):
                value = self._cast_type(type_annotation, value)
        return value


class MetaSchema:
    parsers_config: ClassVar[dict[Type[Any], dict[str, Any]]] = {}
    type_cast: ClassVar[bool] = True
    fails_attempt: ClassVar[int] = -1


class BaseSchema:
    class Meta(MetaSchema):
        pass

    @staticmethod
    def _is_annotated_field(attr: Type):
        return get_origin(attr) is Annotated and isinstance(get_args(attr)[-1], BaseField)

    @staticmethod
    def _is_annotated_tuple_fields(attr: Type):
        return get_origin(attr) is Annotated \
            and isinstance(get_args(attr)[-1], tuple) \
            and all(isinstance(fld, BaseField) for fld in get_args(attr)[-1])

    def _get_fields(self) -> dict[str, BaseField | tuple[BaseField, ...]]:
        _fields: dict[str, BaseField | tuple[BaseField, ...]] = {}

        for name, attr in get_type_hints(self.__class__, include_extras=True).items():
            # get fields from Annotated[Type, Field(..) ]
            if self._is_annotated_field(attr):
                _type, _field = get_args(attr)
                self.__fields_annotations__[name] = _type
                _fields[name] = _field
            # get field from Annotated[Type, (Field(..), Field(..), ...)]
            elif self._is_annotated_tuple_fields(attr):
                _type, _tuple_fields = get_args(attr)
                self.__fields_annotations__[name] = _type
                _fields[name] = _tuple_fields

        # get non-typed fields
        for name, attr in self.__class__.__dict__.items():
            if not name.startswith("__") and isinstance(attr, BaseField):
                _fields[name] = attr
        return _fields

    def _parse_field_value(self,
                           cached_parsers: dict[Type[Any], Any],
                           name: str,
                           fields: BaseField | tuple[BaseField, ...],
                           markup: str) -> Any:
        value: Any = None
        if not isinstance(fields, tuple):
            fields = (fields, )

        for field in fields:
            field_parser = field.Meta.parser
            # parser is not defined in field.Meta.parser
            if not field_parser:
                value = field(self, name, markup)

            elif self.Meta.parsers_config.get(field_parser, None) is None:
                try:
                    raise MarkupNotFoundError(f"{field.__class__.__name__} required "
                                              f"{field_parser.__class__.__name__} configuration")
                except MarkupNotFoundError as e:
                    logger.exception(e)
                    raise e

            else:
                # cache markup parser like BeautifulSoup, HTMLParser, and thing instances
                if not cached_parsers.get(field_parser):
                    parser_kwargs = self.Meta.parsers_config.get(field_parser)
                    cached_parsers[field_parser] = field_parser(markup, **parser_kwargs)

                value = field(self, name, cached_parsers[field_parser])

            if hasattr(field, "default") and value != field.default or value == field.default or not value:
                continue
            else:
                return value
        return value

    def __init__(self, markup: str):
        self.__fields_annotations__: dict[str, Type] = {}

        _fields = self._get_fields()
        _parsers: dict[Type[Any], Any] = {}
        _fails_counter = 0
        logger.debug("Start serialise `%s`. Fields count: %i", self.__class__.__name__, len(_fields.keys()))

        for name, field in _fields.items():
            value = self._parse_field_value(
                cached_parsers=_parsers,
                name=name,
                fields=field,
                markup=markup
            )

            # calculate fails - compare by default value
            if self.Meta.fails_attempt >= 0 and hasattr(field, "default") and value == field.default:
                _fails_counter += 1
                warnings.warn(f"[{_fails_counter}] Failed parse `{self.__class__.__name__}.{name}` "
                              f"by {field.__class__.__name__} field, set `{value}`.",
                              stacklevel=2,
                              category=RuntimeWarning)

                logger.warning("[%i] Failed parse `%s.%s` by `%s`, set `%s`",
                               _fails_counter, self.__class__.__name__, name, field.__class__.__name__, value)

                if _fails_counter > self.Meta.fails_attempt:
                    raise ParseFailAttemptsError(f"{_fails_counter} of {len(_fields.keys())} "
                                                 "fields failed parse.")
            logger.debug("Setattr `%s.%s[%s] = %s`",
                         self.__class__.__name__, name, field.__class__.__name__, value)
            setattr(self, name, value)
        logger.debug("%s done! Fields fails: %i", self.__class__.__name__, _fails_counter)

    @classmethod
    def init_list(cls, markups: list[str]) -> list[Self]:
        return [cls(markup) for markup in markups]

    @staticmethod
    def _to_dict(value: BaseSchema | list | dict):
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
            if not k.startswith("__") and k != "Meta"
        }

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"{', '.join(f'{k}: {type(v).__name__} = {v}' for k, v in self.dict().items())})"
