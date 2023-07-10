import re
from abc import abstractmethod
from re import RegexFlag
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple, Type, Union

from parsel import Selector, SelectorList

from scrape_schema._logger import _logger
from scrape_schema._protocols import SpecialMethodsProtocol
from scrape_schema._typing import Annotated, Self, get_args, get_origin, get_type_hints
from scrape_schema.special_methods import (
    DEFAULT_SPEC_METHOD_HANDLER,
    MarkupMethod,
    SpecialMethods,
    SpecialMethodsHandler,
)
from scrape_schema.type_caster import TypeCaster


class sc_param(property):
    """Shortcut for adding property-like descriptors in BaseSchema"""
    pass  # pragma: no cover


class BaseField:
    def __init__(self, auto_type: bool = True, default: Any = ..., **kwargs):
        self._stack_methods: List[MarkupMethod] = []
        self.default = default
        self.auto_type = auto_type
        self.is_default = False  # flag check failed parsed value
        self._spec_method_handler: SpecialMethodsHandler = DEFAULT_SPEC_METHOD_HANDLER

    @abstractmethod
    def _prepare_markup(self, markup):
        pass  # pragma: no cover

    @abstractmethod
    def sc_parse(self, markup: Any):
        pass  # pragma: no cover


class Field(BaseField):
    def _prepare_markup(self, markup: Union[str, bytes, Selector, SelectorList]):
        """convert string/bytes to parser class context"""
        if isinstance(markup, (Selector, SelectorList)):
            return markup
        elif isinstance(markup, str):
            _logger.debug(
                "Convert raw markup to parsel.Selector",
            )
            return Selector(markup)
        elif isinstance(markup, bytes):
            return Selector(body=markup)
        raise TypeError("Uncorrected markup type")

    def _special_method(self, markup: Any, method: MarkupMethod) -> Any:
        return self._spec_method_handler.handle(method, markup)

    @staticmethod
    def _accept_method(markup: Any, method: MarkupMethod) -> Any:
        if isinstance(method.METHOD_NAME, str):
            class_method = getattr(markup, method.METHOD_NAME)
            if isinstance(class_method, (property, dict)):  # attrib check
                return class_method
            return getattr(markup, method.METHOD_NAME)(*method.args, **method.kwargs)
        raise TypeError(
            f"`{type(markup).__name__}` is not contains `{method.METHOD_NAME}`"
        )

    def _call_stack_methods(self, markup: Any) -> Any:
        result = markup
        _logger.info("start call methods. stack count: %s", len(self._stack_methods))
        for method in self._stack_methods:
            try:
                if isinstance(method.METHOD_NAME, SpecialMethods):
                    result = self._special_method(result, method)
                else:
                    result = self._accept_method(result, method)
            except Exception as e:
                return self._stack_method_handler(method, e)
        _logger.info("Call methods done. result=%s", result)
        return result

    def _stack_method_handler(
        self, method: Union[MarkupMethod, SpecialMethods], e: Exception
    ):
        _logger.error("Method `%s` return traceback %s", method, e)
        _logger.exception(e)
        if self.default is Ellipsis:
            raise e
        _logger.warning("Set default value %s and disable type_casting", self.default)
        self.is_default = True
        return self.default

    def sc_parse(self, markup: Any) -> Any:
        markup = self._prepare_markup(markup)
        return self._call_stack_methods(markup)

    # build in methods

    def fn(self, function: Callable[..., Any]) -> SpecialMethodsProtocol:
        """call another function and return result"""
        return self.add_method(SpecialMethods.FN, function=function)  # type: ignore

    def concat_l(self, left_string: str) -> SpecialMethodsProtocol:
        """add string to left. Last argument should be string"""
        return self.add_method(SpecialMethods.CONCAT_L, left_string)  # type: ignore

    def concat_r(self, right_string: str) -> SpecialMethodsProtocol:
        """add string to right. Last argument should be string"""
        return self.add_method(SpecialMethods.CONCAT_R, right_string)  # type: ignore

    def sc_replace(self, old: str, new: str, count: int = -1) -> SpecialMethodsProtocol:
        """replace string method. Last argument should be string"""
        return self.add_method(SpecialMethods.REPLACE, old, new, count)  # type: ignore

    def re_search(
        self,
        pattern: Union[str, Pattern[str]],
        flags: Union[int, RegexFlag] = 0,
        groupdict: bool = False,
    ) -> SpecialMethodsProtocol:
        """re.search method for text result.

        Last chain should be return string.

        :param pattern: regex pattern
        :param flags: compilation flags
        :param groupdict: accept groupdict method. patter required named groups. default False
        """
        pattern = re.compile(pattern, flags=flags)
        return self.add_method(SpecialMethods.REGEX_SEARCH, pattern, groupdict)  # type: ignore

    def re_findall(
        self,
        pattern: Union[str, Pattern[str]],
        flags: Union[int, RegexFlag] = 0,
        groupdict: bool = False,
    ) -> SpecialMethodsProtocol:
        """[match for match in re.finditer(...)] method for text result.

        Last chain should be return string.

        :param pattern: regex pattern
        :param flags: compilation flags
        :param groupdict: accept groupdict method. patter required named groups. default False
        """
        pattern = re.compile(pattern, flags=flags)
        return self.add_method(SpecialMethods.REGEX_FINDALL, pattern, groupdict)  # type: ignore

    def chomp_js_parse(
        self, unicode_escape: Any = False, json_params: Any = None
    ) -> SpecialMethodsProtocol:
        """Extracts first JSON object encountered in the input string

        Params:
            string – Input string
            unicode_escape – Attempt to fix input string if it contains escaped special characters
            json_params – Allow passing down standard json.loads options

        Returns:
            Extracted JSON object
        """
        return self.add_method(  # type: ignore
            SpecialMethods.CHOMP_JS_PARSE, unicode_escape, json_params
        )

    def chomp_js_parse_all(
        self,
        unicode_escape: Any = False,
        omitempty: Any = False,
        json_params: Any = None,
    ) -> SpecialMethodsProtocol:
        """Returns a list extracting all JSON objects encountered in the input string. Can be used to read JSON Lines

        Params:
            string – Input string
            unicode_escape – Attempt to fix input string if it contains escaped special characters
            omitempty – Skip empty dictionaries and lists
            json_params – Allow passing down standard json.loads flags

        Returns:
            Iterating over it yields all encountered JSON objects
        """
        return self.add_method(  # type: ignore
            SpecialMethods.CHOMP_JS_PARSE_ALL, unicode_escape, omitempty, json_params
        )

    def add_method(
        self, method_name: Union[str, SpecialMethods], *args, **kwargs
    ) -> Self:
        """low-level interface adding methods to call stack"""
        self._stack_methods.append(MarkupMethod(method_name, args=args, kwargs=kwargs))
        return self

    def __getitem__(self, item) -> Self:
        return self.add_method("__getitem__", item)


class SchemaMeta(type):
    __schema_fields__: Dict[str, BaseField]
    __schema_annotations__: Dict[str, Type]

    @staticmethod
    def __is_type_field(attr: Type) -> bool:
        return get_origin(attr) is Annotated and all(
            isinstance(arg, BaseField) for arg in get_args(attr)[1:]
        )

    @staticmethod
    def __parse_annotated_field(attr: Type) -> Tuple[Type, BaseField]:
        args = get_args(attr)
        return args[0], tuple(arg for arg in args[1:] if isinstance(arg, BaseField))[0]

    def __new__(mcs, name, bases, attrs):
        # cache fields, annotations and used parsers for more simplify access
        __schema_fields__: Dict[str, BaseField] = {}  # type: ignore
        __schema_annotations__: Dict[str, Type] = {}  # type: ignore

        cls_schema = super().__new__(mcs, name, bases, attrs)
        if cls_schema.__name__ == "BaseSchema":
            return cls_schema

        # localns={} kwarg avoid TypeError 'function' object is not subscriptable
        for name, value in get_type_hints(
            cls_schema, localns={}, include_extras=True
        ).items():
            if name in ("__schema_fields__", "__schema_annotations__", "__parsers__"):
                continue  # pragma: no cover
            if mcs.__is_type_field(value):
                field_type, field = mcs.__parse_annotated_field(value)
                __schema_fields__[name] = field
                __schema_annotations__[name] = field_type

        setattr(cls_schema, "__schema_fields__", __schema_fields__)
        setattr(cls_schema, "__schema_annotations__", __schema_annotations__)
        setattr(cls_schema, "__meta_info__", {})
        return cls_schema


class BaseSchema(metaclass=SchemaMeta):
    class Config:
        selector_kwargs: Dict[str, Any] = {}
        type_caster: Optional[TypeCaster] = TypeCaster()  # TODO make interface

    @property
    def __parser__(self) -> Union[Selector, SelectorList]:
        return self._cached_parser

    @property
    def __raw__(self) -> str:
        return self._markup

    def __init__(self, markup: Any):
        self._cached_parser: Union[Selector, SelectorList]
        if isinstance(markup, str):
            self._markup = markup
            self._cached_parser = Selector(markup, **self.Config.selector_kwargs)
        elif isinstance(markup, bytes):
            self._cached_parser = Selector(body=markup, **self.Config.selector_kwargs)
            self._markup = markup.decode()
        # TODO write adapter for another backends
        elif isinstance(markup, (Selector, SelectorList)):
            self._markup = markup.get()  # type: ignore
            self._cached_parser = markup

        else:
            raise TypeError(
                f"markup support only str,bytes or Selector types, not {type(markup).__name__}"
            )
        # initialize and parse fields
        self.__init_fields__()

    def __init_fields__(self):
        _logger.info(
            "[%s] Start parse fields count: %s",
            self.__schema_name__,
            len(self.__schema_fields__.keys()),
        )
        for name, field in self.__schema_fields__.items():
            field_type = self.__schema_annotations__[name]
            _logger.debug("%s.%s start parse", self.__schema_name__, name)
            if field.__class__.__name__ == "Nested":  # todo fix
                field.type_ = field_type

            # todo refactoring
            value = field.sc_parse(self.__parser__)

            if self.Config.type_caster and field.auto_type and not field.is_default:
                value = self.Config.type_caster.cast(field_type, value)
            # disable default value flag
            if field.is_default:
                field.is_default = False

            _logger.info("%s.%s = %s", self.__schema_name__, name, value)
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
            k: self._to_dict(getattr(self, k))
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

    def __repr_args__(self) -> List[str]:
        args: Dict[str, Any] = {  # type: ignore
            k: getattr(self, k)
            for k, v in self.__class__.__dict__.items()
            if isinstance(v, sc_param)
        }
        # parse public field keys
        for k, v in self.__dict__.items():
            if not k.startswith("_") and self.__schema_fields__.get(k):  # type: ignore
                args[k] = v

        return [
            f"{k}={repr(v)}"
            if isinstance(v, BaseSchema)
            else f"{k}:{type(v).__name__}={repr(v)}"
            for k, v in args.items()
        ]

    @property
    def __schema_name__(self) -> str:
        return self.__class__.__name__
