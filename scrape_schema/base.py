import sys
import warnings
from abc import ABC, abstractmethod
from typing import (
    Any,
    ByteString,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

if sys.version_info >= (3, 10):
    from typing import TypeAlias, get_args, get_origin, get_type_hints
else:
    from typing_extensions import TypeAlias, get_args, get_origin, get_type_hints

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from scrape_schema._base_configs import BaseFieldConfig, BaseSchemaConfig
from scrape_schema._logger import logger
from scrape_schema._type_caster import TypeCaster
from scrape_schema.exceptions import MarkupNotFoundError, ParseFailAttemptsError

T = TypeVar("T")
MARKUP_TYPE: TypeAlias = Any


def extract_fields(markup: MARKUP_TYPE, **fields: "BaseField") -> Dict[str, Any]:
    return {key: field.extract(markup) for key, field in fields.items()}


class ABCField(ABC):
    @abstractmethod
    def _parse(self, markup: MARKUP_TYPE) -> Any:
        pass

    @abstractmethod
    def _filter(
        self,
        value: T,
        *,
        schema_instance: Optional["BaseSchema"] = None,
        name: Optional[str] = None,
    ) -> bool:
        pass

    @abstractmethod
    def _factory(
        self,
        value: T,
        *,
        schema_instance: Optional["BaseSchema"] = None,
        name: Optional[str] = None,
    ) -> T:
        pass

    @abstractmethod
    def _callback(
        self,
        value: T,
        *,
        schema_instance: Optional["BaseSchema"] = None,
        name: Optional[str] = None,
    ) -> T:
        pass

    @abstractmethod
    def _typing(self, instance: "BaseSchema", name: str, value: T) -> T:
        pass


class BaseField(ABCField):
    class Config(BaseFieldConfig):
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
        self._type_caster = TypeCaster()

    @abstractmethod
    def _parse(self, markup: MARKUP_TYPE) -> Any:
        """first parser entrypoint

        :param markup: parser class object or string. this value can be config in Config class
        :return: first parsed value
        """
        ...

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

    def extract(self, markup: MARKUP_TYPE, *, type_: Optional[Type] = None) -> Any:
        """parse markup without BaseSchema Instance

        :param markup: string target
        :param type_: optional type for type-casting
        """
        logger.info(
            "{}[{}] start extract value. Field attrs: factory={}, callback={}, filter_={}, default={}",
            self.__class__.__name__,
            self.Config.parser or "str",
            repr(self.factory),
            repr(self.callback),
            repr(self.filter_),
            self.default,
        )
        if self.Config.parser and not isinstance(markup, self.Config.parser):
            raise TypeError(
                f"markup argument excepted {self.Config.parser.__name__} "
                f"not {type(markup).__name__}"
            )
        value = self._parse(markup)
        if not value:
            logger.debug(
                "{}.extract value not found, set default `{}` value",
                self.__class__.__name__,
                self.default,
            )
            value = self.default
        if self._is_iterable_and_not_string_value(value):
            if self.filter_:
                logger.debug("{}.extract `filter_({})`", self.__class__.__name__, value)
            value = self._filter(value)
        if self.callback:
            logger.debug("{}.extract `callback({})`", self.__class__.__name__, value)
            value = self._callback(value)
        if self.factory:
            logger.debug("{}.extract `factory({})`", self.__class__.__name__, value)
            value = self._factory(value)
        elif type_:
            value = self._type_caster.cast(type_, value)
        logger.info(
            "{}.extract return `{}[{}]`",
            self.__class__.__name__,
            value,
            type(value).__name__,
        )
        return value

    def __call__(self, instance: "BaseSchema", name: str, markup: MARKUP_TYPE) -> Any:
        """parser entrypoint inside a BaseSchema object"""
        logger.info(
            "{}.{}[{}]: Field attrs: factory={}, callback={}, filter_={}, default={}",
            instance.__schema_name__,
            name,
            self.Config.parser or "str",
            repr(self.factory),
            repr(self.callback),
            repr(self.filter_),
            self.default,
        )
        value = self._parse(markup)
        if not value:
            logger.debug(
                "{}.{}: value is {}, set default `{}`",
                instance.__schema_name__,
                name,
                value,
                self.default,
            )
            value = self.default
        else:
            logger.debug(
                "{}.{} := {} raw value(s)", instance.__schema_name__, name, value
            )

        value = self._filter(value, schema_instance=instance, name=name)
        value = self._callback(value, schema_instance=instance, name=name)
        if self.factory:
            value = self._factory(value, schema_instance=instance, name=name)
        else:
            value = self._typing(instance, name, value)
        logger.info("{}.{} = `{}` Done", instance.__class__.__name__, name, value)
        return value

    def _filter(
        self,
        value: T,
        *,
        schema_instance: Optional["BaseSchema"] = None,
        name: Optional[str] = None,
    ) -> Any:
        """filter parsed value by filter_ function, if it passed

        :param value: list or dict value. dict filter by values
        :return: filtered value
        """
        filter_ = self.filter_

        if filter_ and self._is_iterable_and_not_string_value(value):
            logger.debug(
                "{}.{} := filter_({})",
                schema_instance.__schema_name__
                if schema_instance
                else self.__class__.__name__,
                name or "extract",
                value,
            )
            if isinstance(value, list):
                return list(filter(filter_, value))
            elif isinstance(value, dict):
                return {k: v for k, v in value.items() if filter_(v)}
        return value

    def _factory(
        self,
        value: T,
        *,
        schema_instance: Optional["BaseSchema"] = None,
        name: Optional[str] = None,
    ) -> Any:
        """factory result value entrypoint

        :param value: parsed value
        :return:
        """
        factory = self.factory
        if factory:
            logger.debug(
                "{}.{} := factory({})",
                schema_instance.__schema_name__
                if schema_instance
                else self.__class__.__name__,
                name or "extract",
                value,
            )
        return factory(value) if factory else value

    def _callback(
        self,
        value: T,
        *,
        schema_instance: Optional["BaseSchema"] = None,
        name: Optional[str] = None,
    ) -> Any:
        """eval value by callback function

        :param value:
        :return:
        """
        callback = self.callback

        if not callback:
            return value
        logger.debug(
            "{}.{} := callback({})",
            schema_instance.__schema_name__
            if schema_instance
            else self.__class__.__name__,
            name or "extract",
            value,
        )
        if not self._is_iterable_and_not_string_value(value):
            return callback(value)
        if isinstance(value, list):
            return [callback(i) for i in value]
        elif isinstance(value, dict):
            return {k: callback(v) for k, v in value}
        return callback(value)

    def _typing(self, instance: "BaseSchema", name: str, value: T) -> Any:
        """auto type-cast method

        :param instance: BaseSchema instance
        :param name: field name
        :param value: field value
        :return: typed value
        """
        if instance.Config.type_cast:
            if type_annotation := instance.__schema_annotations__.get(name):
                value = self._type_caster.cast(type_annotation, value)
        return value

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(default={self.default}, callback={self.callback}, "
            f"filter_={self.filter_}, factory={self.factory})"
        )


class SchemaMetaClass(type):
    @staticmethod
    def _is_type_field(attr: Type) -> bool:
        return get_origin(attr) is Annotated and all(
            isinstance(arg, BaseField) for arg in get_args(attr)[1:]
        )

    @staticmethod
    def _extract_annotated(attr: Type) -> Tuple[Type, Tuple[BaseField, ...]]:
        args = get_args(attr)
        return args[0], tuple(arg for arg in args[1:] if isinstance(arg, BaseField))

    def __new__(mcs, name, bases, attrs):
        __schema_fields__: Dict[str, Tuple[BaseField, ...]] = {}  # type: ignore
        __schema_annotations__: Dict[str, Type] = {}  # type: ignore
        cls_schema = super().__new__(mcs, name, bases, attrs)
        if cls_schema.__name__ == "BaseSchema":
            return cls_schema

        # localns={} kwarg avoid TypeError 'function' object is not subscriptable
        for name, value in get_type_hints(
            cls_schema, localns={}, include_extras=True
        ).items():
            if name in ("__schema_fields__", "__schema_annotations__"):
                continue
            if mcs._is_type_field(value):
                field_type, fields = mcs._extract_annotated(value)
                __schema_fields__[name] = fields
                __schema_annotations__[name] = field_type
        setattr(cls_schema, "__schema_fields__", __schema_fields__)
        setattr(cls_schema, "__schema_annotations__", __schema_annotations__)

        return cls_schema


class BaseSchema(metaclass=SchemaMetaClass):
    __schema_fields__: Dict[str, Tuple[BaseField, ...]]
    __schema_annotations__: Dict[str, Type]

    class Config(BaseSchemaConfig):
        pass

    def _get_parser(self, field_parser_class: Type) -> Optional[Dict[str, Any]]:
        return self.Config.parsers_config.get(field_parser_class, None)

    @property
    def cache_parsers(self) -> Dict[Type, Any]:
        return self._cache_parsers

    def clear_cache(self):
        self._cache_parsers.clear()

    def _check_parser_config(self, field: BaseField, field_parser: Type) -> bool:
        if self._get_parser(field_parser) is None:
            try:
                raise MarkupNotFoundError(
                    f"{field.__class__.__name__} required {type(field_parser).__name__} configuration"
                )
            except MarkupNotFoundError as e:
                logger.exception("{}", e)
                raise
        return True

    @staticmethod
    def _success_field_parse(field: BaseField, value) -> bool:
        return (
            hasattr(field, "default")
            and value != field.default
            or value == field.default
            or not value
        )

    def _parse_field_value(
        self,
        name: str,
        _fields: Tuple[BaseField, ...],
        markup: str,
    ) -> Tuple[BaseField, Any]:
        value: Any = None
        for field in _fields:
            if field_parser := field.Config.parser:
                self._check_parser_config(field=field, field_parser=field_parser)
                if self._cache_parsers.get(field_parser, None) is None:
                    parser_kwargs = self.Config.parsers_config.get(field_parser)
                    self._cache_parsers[field_parser] = field_parser(
                        markup, **parser_kwargs
                    )
                value = field(self, name, self._cache_parsers[field_parser])
            else:
                value = field(self, name, markup)
            # get next field if this return default value
            if self._success_field_parse(field, value):
                continue
            else:
                return field, value
        return _fields[-1], value

    def _is_attempt_fail(self, field: BaseField, value: Any) -> bool:
        return (
            self.Config.fails_attempt >= 0
            and hasattr(field, "default")
            and value == field.default
        )

    def _calculate_attempt_parse_errors(
        self,
        *,
        fails_counter: int,
        field: BaseField,
        attr_name: str,
        value: Any,
    ) -> int:
        # calculate fails - compare by default value
        if self._is_attempt_fail(field, value):
            fails_counter += 1
            warnings.warn(
                f"[{fails_counter}] Failed parse `{self.__class__.__name__}.{attr_name}` "
                f"by {field.__class__.__name__} field, set `{value}`.",
                stacklevel=2,
                category=RuntimeWarning,
            )

            logger.warning(
                "[{}] Failed parse `{}.{}` by `{}`, set `{}`",
                fails_counter,
                self.__class__.__name__,
                attr_name,
                field.__class__.__name__,
                value,
            )

            if fails_counter > self.Config.fails_attempt:
                raise ParseFailAttemptsError(
                    f"{fails_counter} of {len(self.__schema_fields__.keys())} "
                    "fields failed parse."
                )
        logger.debug(
            "`{}.{}[{}] = {}`",
            self.__class__.__name__,
            attr_name,
            field.__class__.__name__,
            value,
        )
        return fails_counter

    def __init_fields__(self, markup: str) -> None:
        """
        :param str markup: text target
        """
        _fails_counter = 0
        logger.info(
            "Start parse `{}`. Fields count: {}",
            self.__schema_name__,
            len(self.__schema_fields__.keys()),
        )

        for name, fields in self.__schema_fields__.items():
            field, value = self._parse_field_value(
                name=name, _fields=fields, markup=markup
            )
            _fails_counter = self._calculate_attempt_parse_errors(
                fails_counter=_fails_counter, field=field, attr_name=name, value=value
            )
            setattr(self, name, value)
        logger.debug("{} done! Fields fails: {}", self.__schema_name__, _fails_counter)

    def __init__(self, markup: str, *, parse_markup: bool = True, **kwargs):
        """
        :param markup: markup string target
        :param parse_markup: parse field markups. Default True
        :param kwargs: any kwargs attrs
        """
        # TODO rewrite init constructor
        self._cache_parsers: Dict[Type, Any] = {
            parser: parser(markup, **kw)
            for parser, kw in self.Config.parsers_config.items()
        }
        if parse_markup:
            self.__init_fields__(markup)

        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_list(cls, markups: Iterable[str], **kwargs) -> List[Self]:
        """Init list of schemas by markups sequence

        :param markups: iterable markups sequence
        :param kwargs: any attrs
        """
        return [cls(markup, parse_markup=True, **kwargs) for markup in markups]

    @classmethod
    def from_crop_rule_list(
        cls, markup: str, *, crop_rule: Callable[[str], Iterable[str]], **kwargs
    ) -> List[Self]:
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

    @classmethod
    def from_kwargs(cls, **kwargs) -> Self:
        """Create new class without parse markup and fields

        :param kwargs: any keyword arguments
        """
        if kwargs.get("parse_markup"):
            kwargs.pop("parse_markup")

        return cls("", parse_markup=False, **kwargs)

    @staticmethod
    def _to_dict(value: Union["BaseSchema", List, Dict, Any]):
        if isinstance(value, BaseSchema):
            return value.dict()

        elif isinstance(value, list):
            if all(isinstance(val, BaseSchema) for val in value):
                return [val.dict() for val in value]
        return value

    def raw_dict(self) -> Dict[str, Any]:
        """convert schema object to python dict"""
        return {
            k: self._to_dict(v)
            for k, v in self.__dict__.items()
            if k not in ("Config", "_cache_parsers")
        }

    def dict(self) -> Dict[str, Any]:
        # parse properties
        result: Dict[str, Any] = {
            k: getattr(self, k)
            for k, v in self.__class__.__dict__.items()
            if isinstance(v, property)
        }
        # parse public field keys
        for k, v in self.__dict__.items():
            if not k.startswith("_") and self.__schema_fields__.get(k):
                result[k] = self._to_dict(v)
        return result

    def __repr_args__(self) -> List[str]:
        # parse properties

        args: Dict[str, Any] = {
            k: getattr(self, k)
            for k, v in self.__class__.__dict__.items()
            if isinstance(v, property)
        }
        # parse public field keys
        for k, v in self.__dict__.items():
            if not k.startswith("_") and self.__schema_fields__.get(k):
                args[k] = v

        return [
            f"{k}={repr(v)}"
            if isinstance(v, BaseSchema)
            else f"{k}:{type(v).__name__}={repr(v)}"
            for k, v in args.items()
        ]

    def __repr__(self):
        return f'{self.__schema_name__}({", ".join(self.__repr_args__())})'

    @property
    def __schema_name__(self) -> str:
        return self.__class__.__name__
