from abc import abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Type, Union

from parsel import Selector
from scrape_schema2._typing import Annotated, Self, get_args, get_origin, get_type_hints, NoneType
from scrape_schema2.type_caster import TypeCaster


class SpecialMethods(Enum):
    FN = 0


class MarkupMethod(NamedTuple):
    METHOD_NAME: Union[str, SpecialMethods]
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = {}


class FieldConfig:
    instance: Type[Any] = NoneType
    defaults: Dict[str, Any] = {}


class sc_param(property):
    pass


class BaseField:
    class Config(FieldConfig):
        pass

    def __init__(self, auto_type: bool = True, **kwargs):
        self._stack_methods: List[MarkupMethod] = []
        self.auto_type = auto_type

    def _prepare_markup(self, markup):
        """convert string/bytes to parser class context"""
        if isinstance(self.Config.instance, NoneType):
            return markup
        elif isinstance(markup, (str, bytes)):
            return self.Config.instance(markup, **self.Config.defaults)
        return markup

    @abstractmethod
    def sc_parse(self, markup: Any):
        pass


class Field(BaseField):
    class Config(FieldConfig):
        pass

    def _prepare_markup(self, markup):
        """convert string/bytes to parser class context"""
        if isinstance(self.Config.instance, NoneType):
            return markup
        elif isinstance(markup, (str, bytes)):
            return self.Config.instance(markup, **self.Config.defaults)
        return markup

    @staticmethod
    def _special_method(markup, method: MarkupMethod):
        if method.METHOD_NAME == SpecialMethods.FN:
            return method.kwargs["function"](markup)
        return markup

    @staticmethod
    def _accept_method(markup, method: MarkupMethod) -> Any:
        if isinstance(method.METHOD_NAME, str):
            class_method = getattr(markup, method.METHOD_NAME)
            if isinstance(class_method, property):
                return class_method
            return getattr(markup, method.METHOD_NAME)(*method.args, **method.kwargs)
        raise TypeError(
            f"`{type(markup).__name__}` is not contains `{method.METHOD_NAME}`"
        )

    def _call_stack_methods(self, markup) -> Any:
        result = markup
        for method in self._stack_methods:
            if isinstance(method.METHOD_NAME, SpecialMethods):
                result = self._special_method(result, method)
            else:
                result = self._accept_method(result, method)
        return result

    def sc_parse(self, markup: Any) -> Any:
        markup = self._prepare_markup(markup)
        return self._call_stack_methods(markup)

    # build in methods

    def fn(self, function: Callable[..., Any]) -> Self:
        self.add_method(SpecialMethods.FN, function=function)
        return self

    def add_method(
        self, method_name: Union[str, SpecialMethods], *args, **kwargs
    ) -> Self:
        self._stack_methods.append(MarkupMethod(method_name, args=args, kwargs=kwargs))
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

                if (
                    field.Config.instance
                    and field.Config.instance.__name__ not in __parsers__
                ):
                    __parsers__[field.Config.instance.__name__] = field.Config.instance

                __schema_fields__[name] = field
                __schema_annotations__[name] = field_type
        setattr(cls_schema, "__schema_fields__", __schema_fields__)
        setattr(cls_schema, "__schema_annotations__", __schema_annotations__)
        setattr(cls_schema, "__parsers__", __parsers__)

        return cls_schema


class BaseSchema(metaclass=SchemaMeta):
    class Config:
        parsers: Dict[Type[Any], Dict[str, Any]] = {Selector: {}}
        type_caster: Optional[TypeCaster] = TypeCaster()  # TODO add interface

    def __init__(self, markup):
        self.__raw__ = markup
        for cls_parser in self.__parsers__.values():
            if self.Config.parsers.get(cls_parser, None) is None and cls_parser != type(
                None
            ):
                raise AttributeError(f"Config.parser required {cls_parser.__name__}")
        # cache parsers
        self.cached_parsers: Dict[str, Any] = {  # type: ignore
            cls_parser.__name__: cls_parser(markup, **kw)
            for cls_parser, kw in self.Config.parsers.items()
            if not isinstance(cls_parser, NoneType)
        }
        self.__init_fields__()

    def clear_cache(self):
        self.cached_parsers.clear()

    def __init_fields__(self):
        for name, field in self.__schema_fields__.items():
            field_type = self.__schema_annotations__[name]

            if field.__class__.__name__ == "Nested":  # fixme
                field.type_ = field_type

            if isinstance(field.Config.instance, NoneType):
                cache_key = field.Config.instance.__name__
                value = field.sc_parse(self.cached_parsers[cache_key])
            else:
                value = field.sc_parse(self.__raw__)
                if self.Config.type_caster and field.auto_type:  # fixme
                    value = self.Config.type_caster.cast(field_type, value)
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
            if isinstance(v, sc_param)
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
            if isinstance(v, sc_param)
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
