from enum import Enum
from abc import abstractmethod
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    NamedTuple
)

from experimental._typing import Self, get_args, get_origin, get_type_hints, Annotated


from scrape_schema._type_caster import TypeCaster


class SpecialMethods(Enum):
    filter = 0
    sort = 1


class MarkupMethod(NamedTuple):
    METHOD_NAME: Union[str, SpecialMethods]
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = {}


class FieldConfig:
    instance: Type[Any] = type(None)
    defaults: Dict[str, Any] = {}


class _FieldParam(property):
    pass


field_param = _FieldParam


class BaseField:
    class Config(FieldConfig):
        pass

    def _prepare_markup(self, markup):
        """convert string/bytes to parser class context"""
        if isinstance(self.Config.instance, type(None)):
            return markup
        elif isinstance(markup, (str, bytes)):
            return self.Config.instance(markup)(**self.Config.defaults)
        return markup

    @abstractmethod
    def parse(self, markup, type_: Optional[Type] = None):
        pass


class Field(BaseField):
    class Config(FieldConfig):
        pass

    def __init__(self, cast_type: bool = True):
        self._cast_type = cast_type
        self._t_caster = TypeCaster()
        self._methods_stack: List[MarkupMethod] = []

    def _prepare_markup(self, markup):
        """convert string/bytes to parser class context"""
        if self.Config.instance is type(None):
            return markup
        elif isinstance(markup, (str, bytes)):
            return self.Config.instance(markup)(**self.Config.defaults)
        return markup

    @staticmethod
    def _special_method(markup, method: MarkupMethod):
        if method.METHOD_NAME == SpecialMethods.filter and isinstance(markup, list):
            return [r for r in markup if method.kwargs['func'](r)]

        elif method.METHOD_NAME == SpecialMethods.sort and isinstance(markup, list):
            return sorted(markup, **method.kwargs)
        return markup

    @staticmethod
    def _accept_method(markup, method: MarkupMethod):
        if isinstance(markup, list) and method.METHOD_NAME != "__getitem__":
            return [
                getattr(r, method.METHOD_NAME)(*method.args, **method.kwargs) for r in markup  # type: ignore
            ]
        return getattr(markup, method.METHOD_NAME)(*method.args, **method.kwargs)  # type: ignore

    def _call_stack_methods(self, markup) -> Any:
        result = markup
        for method in self._methods_stack:
            if method.METHOD_NAME is SpecialMethods:
                result = self._special_method(result, method)
            else:
                result = self._accept_method(result, method)
        return result

    def parse(self, markup, type_: Optional[Type] = None) -> Any:
        markup = self._prepare_markup(markup)
        result = self._call_stack_methods(markup)
        if self._cast_type and type_:
            return self._t_caster.cast(type_, result)
        return result

    # build in methods

    def filter(self, filter_: Callable[..., bool]) -> Self:
        return self.add_method(
            SpecialMethods.filter, func=filter_
        )

    def sort(self, key: Any, reverse: bool = False) -> Self:
        return self.add_method(SpecialMethods.sort, key=key, reverse=reverse)

    def add_method(self, method_name: Union[str, SpecialMethods], *args, **kwargs) -> Self:
        self._methods_stack.append(
            MarkupMethod(
                method_name,
                args=args,
                kwargs=kwargs
            )
        )
        return self

    def __getitem__(self, item) -> Self:
        return self.add_method("__getitem__", item)


class SchemaMeta(type):
    __schema_fields__: Dict[str, BaseField]
    __schema_annotations__: Dict[str, Type]
    __parsers__: Dict[str, Type]

    @staticmethod
    def _is_type_field(attr: Type) -> bool:
        return get_origin(attr) is Annotated and all(
            isinstance(arg, BaseField) for arg in get_args(attr)[1:]
        )

    @staticmethod
    def _extract_annotated(attr: Type) -> Tuple[Type, BaseField]:
        args = get_args(attr)
        return args[0], tuple(arg for arg in args[1:] if isinstance(arg, BaseField))[0]

    def __new__(mcs, name, bases, attrs):
        __schema_fields__: Dict[str, BaseField] = {}  # type: ignore
        __schema_annotations__: Dict[str, Type] = {}  # type: ignore
        __parsers__: Dict[str, Type] = {}  # type: ignore

        cls_schema = super().__new__(mcs, name, bases, attrs)
        if cls_schema.__name__ == "BaseSchema":
            return cls_schema

        # localns={} kwarg avoid TypeError 'function' object is not subscriptable
        for name, value in get_type_hints(
            cls_schema, localns={}, include_extras=True
        ).items():
            if name in ("__schema_fields__", "__schema_annotations__", "__parsers__"):
                continue
            if mcs._is_type_field(value):
                field_type, field = mcs._extract_annotated(value)

                if field.Config.instance and field.Config.instance.__name__ not in __parsers__:
                    __parsers__[field.Config.instance.__name__] = field.Config.instance

                __schema_fields__[name] = field
                __schema_annotations__[name] = field_type
        setattr(cls_schema, "__schema_fields__", __schema_fields__)
        setattr(cls_schema, "__schema_annotations__", __schema_annotations__)
        setattr(cls_schema, "__parsers__", __parsers__)

        return cls_schema


class BaseSchema(metaclass=SchemaMeta):
    class Config:
        parsers: Dict[Type[Any], Dict[str, Any]] = {}

    def __init__(self, markup):
        self.__raw__ = markup
        for cls_parser in self.__parsers__.values():
            if not self.Config.parsers.get(cls_parser, None) and cls_parser != type(None):
                raise AttributeError(f"Config.parser required {cls_parser.__name__}")
        # cache parsers
        self.cached_parsers: Dict[str, Any] = {
            cls_parser.__name__: cls_parser(markup, **kw)
            for cls_parser, kw in self.Config.parsers.items() if cls_parser != type(None)
        }
        self.__init_fields__()

    def clear_cache(self):
        self.cached_parsers.clear()

    def __init_fields__(self):
        for name, field in self.__schema_fields__.items():
            field_type = self.__schema_annotations__[name]
            if field.Config.instance != type(None):
                cache_key = field.Config.instance.__name__
                value = field.parse(self.cached_parsers[cache_key], field_type)
            else:
                value = field.parse(self.__raw__, field_type)
            setattr(self, name, value)

    @staticmethod
    def _to_dict(value: Union["BaseSchema", List, Dict, Any]):
        if isinstance(value, BaseSchema):
            return value.dict()

        elif isinstance(value, list):
            if all(isinstance(val, BaseSchema) for val in value):
                return [val.dict() for val in value]
        return value

    def dict(self):
        result: Dict[str, Any] = {  # type: ignore
            k: getattr(self, k)
            for k, v in self.__class__.__dict__.items()
            if isinstance(v, _FieldParam)
        }
        # parse public field keys
        for k, v in self.__dict__.items():
            if not k.startswith("_") and self.__schema_fields__.get(k):
                result[k] = self._to_dict(v)
        return result

    def __repr__(self):
        return f'{self.__schema_name__}({", ".join(self.__repr_args__())})'

    def __repr_args__(self):
        args: Dict[str, Any] = {  # type: ignore
            k: getattr(self, k)
            for k, v in self.__class__.__dict__.items()
            if isinstance(v, _FieldParam)
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

    @property
    def __schema_name__(self):
        return self.__class__.__name__
