from __future__ import annotations

import logging
import warnings
from abc import ABC, abstractmethod
from types import NoneType
from typing import (
    Any,
    ByteString,
    Callable,
    ClassVar,
    Iterable,
    Optional,
    Type,
    TypeAlias,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

# python < 3.9
try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

# python < 3.11
try:
    from typing import Self  # type: ignore
except ImportError:
    from typing_extensions import Self  # type: ignore

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
        return issubclass(value_type, Iterable) and not issubclass(
            value_type, (ByteString, str)
        )

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
            logger.debug(
                "`%s` value `%s` has same type, skip cast",
                self.__class__.__name__,
                value,
            )
            return value

        logger.debug(
            "`%s` Cast type start. `value[%s]=%s`, type_annotation=%s, `type_origin=%s`, `args=%s`",
            self.__class__.__name__,
            value_type.__name__,
            value,
            type_annotation,
            type_origin,
            type_args,
        )

        # Optional
        if type_origin is Union and NoneType in type_args:
            # get optional type, set
            if value:
                logger.debug(
                    "`%s` Cast Optional type `%s(%s)`",
                    self.__class__.__name__,
                    value,
                    type_args[0],
                )
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
                logger.debug(
                    "`%s` Cast Optional type, value `%s` is False",
                    self.__class__.__name__,
                    value,
                )
                return value

        # dict, list
        elif type_origin:
            if issubclass(type_origin, dict) and isinstance(value, dict):
                logger.debug(
                    "`%s` Cast dict type: `%s(key)`, `%s(value)`",
                    self.__class__.__name__,
                    type_args[0],
                    type_args[1],
                )
                # get dict set
                return {type_args[0](k): type_args[1](v) for k, v in value.items()}

            elif self._is_iterable_and_not_string_type(type_origin) and isinstance(
                value, list
            ):
                logger.debug(
                    "`%s` Cast list items to `%s(item)`",
                    self.__class__.__name__,
                    type_args[0],
                )
                # get list, set
                return [type_args[0](i) for i in value]

        else:
            # single type
            logger.debug(
                "Cast `%s` `%s(%s)`",
                self.__class__.__name__,
                type_annotation.__name__,
                value,
            )
            return type_annotation(value)


class BaseConfigField:
    """BaseField configuration class:

    * parser: Optional[Type[Any]] - parser backend object. If value None - work with python str
    """

    parser: ClassVar[Optional[Type[Any]]] = None


class BaseField(ABCField, TypeCaster):
    class Config(BaseConfigField):
        pass

    def __init__(
        self,
        *,
        default: Optional[Any] = None,
        filter_: Optional[Callable[[T], bool]] = None,
        callback: Optional[Callable[..., T]] = None,
        factory: Optional[Callable[..., T]] = None,
        **kwargs,
    ):
        """BaseField object.

        :param default: default value if parser return None or empty value. Default None
        :param filter_: (for iterables only) filter value by function. If None - ignore
        :param callback: function for evaluate parsed value
        :param factory: function for evaluate result value. If passed - **ignore auto-typing feature**
        :param kwargs: any params for create fields
        """
        self.factory = factory
        self.callback = callback
        self.filter_ = filter_
        self.default = default

    @abstractmethod
    def _parse(self, markup: MARKUP_TYPE) -> Any:
        """first parser entrypoint

        :param markup: parser class object or string. this value can be config in Config class
        :return: first parsed value
        """
        ...

    def __call__(self, instance: BaseSchema, name: str, markup: MARKUP_TYPE) -> Any:
        logger.info(
            "`%s.%s[%s]`. Field attrs: factory=%s, callback=%s, filter_=%s, default=%s",
            instance.__class__.__name__,
            name,
            self.Config.parser or "str",
            getattr(self.factory, "__name__", None),
            getattr(self.callback, "__name__", None),
            getattr(self.filter_, "__name__", None),
            self.default,
        )
        value = self._parse(markup)
        if not value:
            logger.debug(
                "`%s.%s` value not found, set default `%s` value",
                instance.__class__.__name__,
                name,
                self.default,
            )
            value = self.default
        else:
            logger.debug(
                "`%s.%s = %s` raw value(s)", instance.__class__.__name__, name, value
            )

        if self._is_iterable_and_not_string_value(value):
            value = self._filter(value)
            if self.filter_:
                logger.debug(
                    "filter_ `%s.%s = %s`", instance.__class__.__name__, name, value
                )

        value = self._callback(value)
        if self.callback:
            logger.debug(
                "callback `%s.%s = %s`", instance.__class__.__name__, name, value
            )

        if self.factory:
            value = self._factory(value)
            logger.debug(
                "factory `%s.%s = %s`", instance.__class__.__name__, name, value
            )
        else:
            value = self._typing(instance, name, value)
        return value

    def _filter(self, value: T) -> Any:
        """filter parsed value by filter_ function, if it passed

        :param value: list or dict value. dict filter by values
        :return: filtered value
        """
        if self.filter_:
            if isinstance(value, list):
                return list(filter(self.filter_, value))
            elif isinstance(value, dict):
                return {k: v for k, v in value.items() if self.filter_(v)}
        return value

    def _factory(self, value: T) -> Any:
        """factory result value entrypoint

        :param value: parsed value
        :return:
        """
        return self.factory(value) if self.factory else value

    def _callback(self, value: T) -> Any:
        """eval value by callback function

        :param value:
        :return:
        """
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
        """auto type-cast method

        :param instance: BaseSchema instance
        :param name: field name
        :param value: field value
        :return: typed value
        """
        if instance.Config.type_cast:
            if type_annotation := instance.__fields_annotations__.get(name):
                value = self._cast_type(type_annotation, value)
        return value


class BaseSchemaConfig:
    """Schema configuration for BaseSchema

    parsers_config: dict[Type[Any], dict[str, Any]] parser classes for usage backend

    type_cast: bool usage type casting feature. default True

    fails_attempt: int - fields parse success counter checker. default -1 disable

    fails_attempt < 0   - disable checker (default)

    fails_attempt == 0  - if _first_ field return `default` value - throw `ParseFailAttemptsError`

    fails_attempt = n, fails_attempt > 0 - print *n* warnings messages if field return `default` value.
    if `n` msgs - throw `ParseFailAttemptsError`
    """

    parsers_config: ClassVar[dict[Type[Any], dict[str, Any]]] = {}
    type_cast: ClassVar[bool] = True
    fails_attempt: ClassVar[int] = -1


class BaseSchema:
    class Config(BaseSchemaConfig):
        pass

    @staticmethod
    def _is_annotated_field(attr: Type):
        return get_origin(attr) is Annotated and isinstance(
            get_args(attr)[-1], BaseField
        )

    @staticmethod
    def _is_annotated_tuple_fields(attr: Type):
        return (
            get_origin(attr) is Annotated
            and isinstance(get_args(attr)[-1], tuple)
            and all(isinstance(fld, BaseField) for fld in get_args(attr)[-1])
        )

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

    def _parse_field_value(
        self,
        cached_parsers: dict[Type[Any], Any],
        name: str,
        fields: BaseField | tuple[BaseField, ...],
        markup: str,
    ) -> Any:
        value: Any = None
        if not isinstance(fields, tuple):
            fields = (fields,)

        for field in fields:
            field_parser = field.Config.parser
            # parser is not defined in field.Config.parser
            if not field_parser:
                value = field(self, name, markup)

            elif self.Config.parsers_config.get(field_parser, None) is None:
                try:
                    raise MarkupNotFoundError(
                        f"{field.__class__.__name__} required "
                        f"{field_parser.__class__.__name__} configuration"
                    )
                except MarkupNotFoundError as e:
                    logger.exception(e)
                    raise e

            else:
                # cache markup parser like BeautifulSoup, HTMLParser, and thing instances
                if not cached_parsers.get(field_parser):
                    parser_kwargs = self.Config.parsers_config.get(field_parser)
                    cached_parsers[field_parser] = field_parser(markup, **parser_kwargs)

                value = field(self, name, cached_parsers[field_parser])

            if (
                hasattr(field, "default")
                and value != field.default
                or value == field.default
                or not value
            ):
                continue
            else:
                return value
        return value

    def _parse_markup_to_fields(self, markup: str) -> None:
        """
        :param str markup: text target
        """
        self.__fields_annotations__: dict[str, Type] = {}

        _fields = self._get_fields()
        _parsers: dict[Type[Any], Any] = {}
        _fails_counter = 0
        logger.info(
            "Start parse `%s`. Fields count: %i",
            self.__class__.__name__,
            len(_fields.keys()),
        )

        for name, field in _fields.items():
            value = self._parse_field_value(
                cached_parsers=_parsers, name=name, fields=field, markup=markup
            )

            # calculate fails - compare by default value
            if (
                self.Config.fails_attempt >= 0
                and hasattr(field, "default")
                and value == field.default
            ):
                _fails_counter += 1
                warnings.warn(
                    f"[{_fails_counter}] Failed parse `{self.__class__.__name__}.{name}` "
                    f"by {field.__class__.__name__} field, set `{value}`.",
                    stacklevel=2,
                    category=RuntimeWarning,
                )

                logger.warning(
                    "[%i] Failed parse `%s.%s` by `%s`, set `%s`",
                    _fails_counter,
                    self.__class__.__name__,
                    name,
                    field.__class__.__name__,
                    value,
                )

                if _fails_counter > self.Config.fails_attempt:
                    raise ParseFailAttemptsError(
                        f"{_fails_counter} of {len(_fields.keys())} "
                        "fields failed parse."
                    )
            logger.debug(
                "`%s.%s[%s] = %s`",
                self.__class__.__name__,
                name,
                field.__class__.__name__,
                value,
            )
            setattr(self, name, value)
        logger.debug(
            "%s done! Fields fails: %i", self.__class__.__name__, _fails_counter
        )

    def __init__(self, markup: str, *, parse_markup: bool = True, **kwargs):
        """
        :param markup: markup string target
        :param parse_markup: parse field markups. Default True
        :param kwargs: any kwargs attrs
        """
        # TODO rewrite init constructor
        if parse_markup:
            self._parse_markup_to_fields(markup)

        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def init_list(cls, markups: Iterable[str]) -> list[Self]:
        """Init list of schemas by markups sequence

        :param markups: - iterable markups sequence
        """
        warnings.warn(
            "This method deprecated, usage `from_list`",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return cls.from_list(markups)

    @classmethod
    def from_list(cls, markups: Iterable[str], **kwargs) -> list[Self]:
        """Init list of schemas by markups sequence

        :param markups: iterable markups sequence
        :param kwargs: any attrs
        """
        return [cls(markup, parse_markup=True, **kwargs) for markup in markups]

    @classmethod
    def from_crop_rule_list(
        cls, markup: str, *, crop_rule: Callable[[str], Iterable[str]], **kwargs
    ) -> list[Self]:
        """Init list of schemas by crop_rule

        :param markup: markup string
        :param crop_rule: crop rule function to *parts*
        """
        return cls.from_list(crop_rule(markup), **kwargs)

    @classmethod
    def from_crop_rule(
        cls, markup: str, *, crop_rule: Callable[[str], str], **kwargs
    ) -> Self:
        """Init single schema by crop_rule

        :param markup: markup string
        :param crop_rule: crop rule function to *part*.
        """
        return cls(crop_rule(markup), parse_markup=True, **kwargs)

    @classmethod
    def from_markup(cls, markup: str, **kwargs) -> Self:
        return cls(markup, parse_markup=True, **kwargs)

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
            if not k.startswith("_") and k != "Config"
        }

    def __repr_args__(self) -> list[str]:
        return [
            f"{k}={repr(v)}"
            if isinstance(v, BaseSchema)
            else f"{k}:{type(v).__name__}={repr(v)}"
            for k, v in self.__dict__.items()
            if not k.startswith("_") and k != "Config"
        ]

    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join(self.__repr_args__())})'
