import re
import warnings
from abc import abstractmethod
from re import RegexFlag
from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    List,
    Optional,
    Pattern,
    Tuple,
    Type,
    Union,
)

from parsel import Selector, SelectorList

from scrape_schema._logger import _logger
from scrape_schema._protocols import SpecialMethodsProtocol
from scrape_schema._typing import (
    Annotated,
    NoneType,
    Self,
    get_args,
    get_origin,
    get_type_hints,
)
from scrape_schema.exceptions import SchemaPreValidationError
from scrape_schema.special_methods import (
    DEFAULT_SPEC_METHOD_HANDLER,
    MarkupMethod,
    SpecialMethods,
    SpecialMethodsHandler,
)
from scrape_schema.type_caster import TypeCaster
from scrape_schema.validator import markup_pre_validator


class sc_param(property):
    """Shortcut for adding property-like descriptors in BaseSchema,
    which will go into the output of the `dict()` method.

    Works like build-in `@property` decorator"""

    pass  # pragma: no cover


class BaseField:
    def __init__(
        self,
        auto_type: bool = True,
        default: Any = ...,
        alias: Optional[str] = None,
        **kwargs,
    ):
        """Base Field class

        Args:
            auto_type: usage auto_type feature. default True. works in BaseSchema object
            default: default value if parsing runtime will catch an error.
                Throws an error by default
            alias: alias fields to display in the BaseSchema object.
                If no value is specified, will apply the key of the given attribute
        """
        self._stack_methods: List[MarkupMethod] = []
        self.default = default
        self.auto_type = auto_type
        self.is_default = False  # flag check failed parsed value
        self.alias = alias

        self._spec_method_handler: SpecialMethodsHandler = DEFAULT_SPEC_METHOD_HANDLER
        self._last_failed_method: Optional[MarkupMethod] = None
        self._is_success: bool = True  # False - field is failed, True, no errors

    @abstractmethod
    def _prepare_markup(self, markup):
        pass  # pragma: no cover

    @abstractmethod
    def sc_parse(self, markup: Any):
        pass  # pragma: no cover


class Field(BaseField):
    def _prepare_markup(
        self, markup: Union[str, bytes, Selector, SelectorList]
    ) -> Union[Selector, SelectorList]:
        """convert string/bytes to parser class context

        Args:
            markup: str, bytes, Selector, SelectorList object

        Returns:
            markup converted to Selector object, if markup arg is str or bytes

        Raises:
            TypeError if markup is not str, bytes, Selector, SelectorList object
        """
        self._last_failed_method = None  # reset failed method link
        _logger.debug("Field markup type: %s", type(markup).__name__)
        if isinstance(markup, (Selector, SelectorList)):
            return markup
        elif isinstance(markup, str):
            return Selector(markup)
        elif isinstance(markup, bytes):
            return Selector(body=markup)
        raise TypeError(f"Unsupported markup type: {type(markup).__name__}")

    @property
    def success(self) -> bool:
        """last parsed field status"""
        return self._is_success

    def _special_method(self, markup: Any, method: MarkupMethod) -> Any:
        """Handle special method

        Args:
            markup: variable for special_method
            method: markup method object

        Returns:
            method execution result
        """
        return self._spec_method_handler.handle(method, markup)

    def __repr__(self):
        args = f"auto_type={self.auto_type}, default={self.default}, alias={self.alias}"
        if self._stack_methods:
            return (  # pragma: no cover
                f"{self.__class__.__name__}({args})."
                f"{'.'.join(repr(m) for m in self._stack_methods)}"
            )
        return f"{self.__class__.__name__}({args})"

    @staticmethod
    def _accept_method(markup: Any, method: MarkupMethod) -> Any:
        """call method

        Args:
            markup: variable for MarkupMethod
            method: markup method object

        Returns:
            method execution result
        """
        if isinstance(method.METHOD_NAME, str):
            class_method = getattr(markup, method.METHOD_NAME)
            # Selector.attrib check case or raw dict
            if isinstance(class_method, (property, dict)):
                return class_method
            # callable
            return class_method(*method.args, **method.kwargs)
        raise TypeError(  # pragma: no cover
            f"`{type(markup).__name__}` is not a valid method name: {method.METHOD_NAME}"
        )

    @staticmethod
    def __log_debug_markup_len(markup: Any) -> int:
        """this method for logging module"""
        if isinstance(markup, NoneType):  # pragma: no cover
            return 0
        elif isinstance(markup, (Selector, SelectorList)):
            markup = markup.get()
            return 0 if isinstance(markup, NoneType) else len(markup)
        return len(str(markup))

    @staticmethod
    def __log_debug_markup_part(markup: Any, max_len: int = 64) -> str:
        """this method for logging module"""
        if isinstance(markup, NoneType):  # pragma: no cover
            return ""
        elif isinstance(markup, (Selector, SelectorList)):
            markup = markup.get()
            return (
                ""
                if isinstance(markup, NoneType)
                else f"{markup[:max_len]}..."
                if len(markup) > max_len
                else markup
            )
        markup = str(markup)
        return f"{markup[:max_len]}..." if len(markup) > max_len else markup

    def _call_stack_methods(self, markup: Any) -> Any:
        """call all passed methods

        Args:
            markup: first markup target

        Returns:
            result of all executed methods

        Raises:
            most often `AttributeError` and `TypeError` due to the absence
            of a method name due to incorrect output data in the call chain
        """
        self._is_success = True  # reset success parsed flag
        result = markup
        _logger.info(
            "Start parse markup. Stack methods count: %s", len(self._stack_methods)
        )
        _logger.debug(
            "Markup (len=%i) target: %s",
            self.__log_debug_markup_len(markup),
            self.__log_debug_markup_part(markup),
        )
        for i, method in enumerate(self._stack_methods, 1):
            try:
                if isinstance(method.METHOD_NAME, SpecialMethods):
                    result = self._special_method(result, method)
                else:
                    result = self._accept_method(result, method)
                _logger.debug(
                    "[%s] %s -> %s", i, method, self.__log_debug_markup_part(result)
                )
            except Exception as e:
                self._is_success = False  # mark failed parse field
                _logger.warning(
                    "Oops, %s throw exception `%s: %s`",
                    str(method).lower(),
                    e.__class__.__name__,
                    e,
                )
                self._last_failed_method = method
                return self._stack_method_error_handler(method, e, markup)
        _logger.info("Call methods done. result=%s", result)
        if self.default is not Ellipsis and result in (None, []):
            return self.default
        return result

    def _stack_method_error_handler(
        self, method: Union[MarkupMethod, SpecialMethods], e: Exception, markup
    ):
        _logger.error("Failed call method: %s", method)
        _logger.error(
            "Full markup:\nSTART\n%s\nEND",
            markup.get() if isinstance(markup, (Selector, SelectorList)) else markup,
        )
        if self.default is Ellipsis:
            _logger.error(
                "Method `%r` return traceback: `%s: %s`",
                method,
                e.__class__.__name__,
                e,
            )
            raise e
        _logger.info(
            "Skip type casting and set default value: %s",
            self.default,
        )
        self.is_default = True
        return self.default

    def sc_parse(self, markup: Union[str, bytes, Selector, SelectorList]) -> Any:
        """parse field entrypoint. Execute all passed methods

        Args:
            markup: markup target

        Returns:
            result of all executed methods
        """
        markup = self._prepare_markup(markup)
        return self._call_stack_methods(markup)

    # build in methods

    def fn(self, function: Callable[..., Any]) -> SpecialMethodsProtocol:
        """call another function and return result

        Args:
            function: function to be executed

        Returns:
            executed function result
        """
        return self.add_method(SpecialMethods.FN, function=function)  # type: ignore

    def concat_l(self, left_string: str) -> SpecialMethodsProtocol:
        """add string to left. Last argument should be string
            value + left_string
        Args:
            left_string:

        Returns:
            concatenated value
        """
        return self.add_method(SpecialMethods.CONCAT_L, left_string)  # type: ignore

    def concat_r(self, right_string: str) -> SpecialMethodsProtocol:
        """add string to right. Last argument should be string
            right_string + value
        Args:
            right_string:

        Returns:
            concatenated string
        """
        return self.add_method(SpecialMethods.CONCAT_R, right_string)  # type: ignore

    def sc_replace(self, old: str, new: str, count: int = -1) -> SpecialMethodsProtocol:
        warnings.warn(
            "Method `sc_replace` "
            "deprecated and will be removed in future releases. Usage `replace method instead`",
            category=DeprecationWarning,
        )
        return self.replace(old, new, count)

    def replace(self, old: str, new: str, count: int = -1) -> SpecialMethodsProtocol:
        """str.replace method. Last argument should be string. old string replaced by new

        Args:
            old: string
            new: string
            count: Maximum number of occurrences to replace. -1 (default) means replace all occurrences.

        Returns:
            replaced string
        """
        return self.add_method(SpecialMethods.REPLACE, old, new, count)  # type: ignore

    def re_search(
        self,
        pattern: Union[str, Pattern[str]],
        flags: Union[int, RegexFlag] = 0,
        groupdict: bool = False,
    ) -> SpecialMethodsProtocol:
        """re.search method for text result.

        Last chain should be return string.

        Args:
            pattern: regex pattern
            flags: regex compilation flags
            groupdict: accept groupdict method. pattern required named groups. default False
        Raises:
            AttributeError: if groupdict=True and pattern not contains named groups
        """
        pattern = re.compile(pattern, flags=flags)
        if groupdict and not pattern.groupindex:
            raise TypeError("groupdict required named groups")
        return self.add_method(  # type: ignore
            SpecialMethods.REGEX_SEARCH, pattern, groupdict, flags
        )

    def re_findall(
        self,
        pattern: Union[str, Pattern[str]],
        flags: Union[int, RegexFlag] = 0,
        groupdict: bool = False,
    ) -> SpecialMethodsProtocol:
        """[match for match in re.finditer(...)] method for text result.

        Last chain should be return string.

        Args:
            pattern: regex pattern
            flags: regex compilation flags
            groupdict: accept groupdict method. patter required named groups. default False

        Raises:
            AttributeError: if groupdict=True and pattern not contains named groups
        """
        pattern = re.compile(pattern, flags=flags)
        if groupdict and not pattern.groupindex:
            raise TypeError("groupdict required named groups")

        return self.add_method(  # type: ignore
            SpecialMethods.REGEX_FINDALL, pattern, groupdict, flags
        )

    def chomp_js_parse(
        self, unicode_escape: Any = False, json_params: Any = None
    ) -> SpecialMethodsProtocol:
        """Extracts first JSON object encountered in the input string

        Args:
            unicode_escape: Attempt to fix input string if it contains escaped special characters
            json_params: Allow passing down standard `json.loads` options

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

        Args:
            unicode_escape: Attempt to fix input string if it contains escaped special characters
            omitempty: Skip empty dictionaries and lists
            json_params: Allow passing down standard `json.loads` flags

        Returns:
            Iterating over it yields all encountered JSON objects
        """
        return self.add_method(  # type: ignore
            SpecialMethods.CHOMP_JS_PARSE_ALL, unicode_escape, omitempty, json_params
        )

    # 6.0.0 special methods

    def strip(self, chars: Optional[str] = None) -> SpecialMethodsProtocol:
        """Same as `str.strip()` method.

        If last chain list[str] argument - invoke this method to all arguments

        Args:
            chars: strip chars. Default strip all whitespaces (\t, \n included)
        """
        return self.add_method(SpecialMethods.STRIP, chars)  # type: ignore

    def rstrip(self, chars: Optional[str] = None) -> SpecialMethodsProtocol:
        """Same as `str.rstrip()` method.

        If last chain list[str] argument - invoke this method to all arguments

        Args:
            chars: strip chars. Default strip right whitespaces (\t, \n included)
        """
        return self.add_method(SpecialMethods.R_STRIP, chars)  # type: ignore

    def lstrip(self, chars: Optional[str] = None) -> SpecialMethodsProtocol:
        """Same as `str.lstrip()` method.

        If last chain list[str] argument - invoke this method to all arguments

        Args:
            chars: strip chars. Default strip left whitespaces (\t, \n included)
        """
        return self.add_method(SpecialMethods.L_STRIP, chars)  # type: ignore

    def lower(self) -> SpecialMethodsProtocol:
        """Same as `str.lower()` method.

        If last chain list[str] argument - invoke this method to all arguments
        """
        return self.add_method(SpecialMethods.LOWER)  # type: ignore

    def upper(self) -> SpecialMethodsProtocol:
        """Same as `str.upper()` method.

        If last chain list[str] argument - invoke this method to all arguments
        """
        return self.add_method(SpecialMethods.UPPER)  # type: ignore

    def capitalize(self) -> SpecialMethodsProtocol:
        """Same as `str.capitalize()` method.

        If last chain list[str] argument - invoke this method to all arguments
        """
        return self.add_method(SpecialMethods.CAPITALIZE)  # type: ignore

    def split(
        self, sep: Optional[str] = None, max_split: int = -1
    ) -> SpecialMethodsProtocol:
        """Same as `str.split()` method.

        If last chain list[str] argument - raise TypeError
        """
        return self.add_method(SpecialMethods.SPLIT, sep, max_split)  # type: ignore

    def join(self, join_sep: str) -> SpecialMethodsProtocol:
        """Same as `str.join()` method.

        If last chain list[str] argument - raise TypeError

        Args:
            join_sep: separate char for result
        """
        return self.add_method(SpecialMethods.STR_JOIN, join_sep)  # type: ignore

    def count(self) -> SpecialMethodsProtocol:
        """Return items count.

        if last chain value is list - return len value else 1

        """
        return self.add_method(SpecialMethods.COUNT)  # type: ignore

    def add_method(
        self, method_name: Union[str, SpecialMethods], *args, **kwargs
    ) -> Self:
        """low-level interface adding methods to call stack"""
        self._stack_methods.append(MarkupMethod(method_name, args=args, kwargs=kwargs))
        return self

    def __getitem__(self, item: Hashable) -> Self:
        """This method provide __getitem__ API (get by key or slice)

        Args:
            item: key or slice
        """
        return self.add_method("__getitem__", item)


class SchemaMeta(type):
    """Metaclass for prefetching fields, field annotations, and field alias keys"""

    @staticmethod
    def __is_type_field(attr: Type) -> bool:
        return get_origin(attr) is Annotated and all(
            isinstance(arg, BaseField) for arg in get_args(attr)[1:]
        )

    @staticmethod
    def __parse_annotated_field(attr: Type) -> Tuple[Type, BaseField]:
        args = get_args(attr)
        return args[0], tuple(arg for arg in args[1:] if isinstance(arg, BaseField))[0]

    @staticmethod
    def __is_attribute_field(cls_schema, name: str) -> bool:
        if (field := cls_schema.__dict__.get(name)) and isinstance(field, BaseField):
            return True
        return False

    @staticmethod
    def __parse_attribute_field(cls_schema, name: str) -> Tuple[Type, BaseField]:
        field = cls_schema.__dict__.get(name)
        type_ = cls_schema.__annotations__.get(name, Any)
        return type_, field

    def __new__(mcs, name, bases, attrs):
        # cache fields, annotations and used parsers for more simplify access
        __schema_fields__: Dict[str, BaseField] = {}  # type: ignore
        __schema_annotations__: Dict[str, Type] = {}  # type: ignore
        __schema_aliases__: Dict[str, str] = {}  # type: ignore

        cls_schema = super().__new__(mcs, name, bases, attrs)
        if cls_schema.__name__ == "BaseSchema":
            return cls_schema

        # localns={} kwarg avoid TypeError 'function' object is not subscriptable
        for name, value in get_type_hints(
            cls_schema, localns={}, include_extras=True
        ).items():
            if name in (
                "__schema_fields__",
                "__schema_annotations__",
                "__schema_aliases__",
            ):
                continue  # pragma: no cover
            # Annotated[type, Field]
            if mcs.__is_type_field(value):  # pragma: no cover
                field_type, field = mcs.__parse_annotated_field(value)
                __schema_fields__[name] = field
                if field.alias:
                    __schema_aliases__[name] = field.alias
                __schema_annotations__[name] = field_type
            # attr_name: type = Field
            elif mcs.__is_attribute_field(cls_schema, name):
                field_type, field = mcs.__parse_attribute_field(cls_schema, name)
                __schema_fields__[name] = field
                if field.alias:
                    __schema_aliases__[name] = field.alias
                __schema_annotations__[name] = field_type

        setattr(cls_schema, "__schema_fields__", __schema_fields__)
        setattr(cls_schema, "__schema_annotations__", __schema_annotations__)
        setattr(cls_schema, "__schema_aliases__", __schema_aliases__)
        return cls_schema


class SchemaConfig:
    """BaseSchema configuration

    Attributes:
        selector_kwargs: default kwargs for parsel.Selector class
        type_caster: type_caster module
    """

    selector_kwargs: Dict[str, Any] = {}  # default execute extra kwargs
    type_caster: Optional[TypeCaster] = TypeCaster()  # type_caster class


class BaseSchema(metaclass=SchemaMeta):
    __schema_fields__: Dict[str, BaseField]
    __schema_annotations__: Dict[str, Type]
    __schema_aliases__: Dict[str, str]

    """Main schema class

    Attributes:
        __schema_fields__: Dict[str, BaseField] access to fields object by key in current schema
        __schema_annotations__: Dict[str, Type] access to fields annotations in current schema
        __schema_aliases__: Dict[str, str] access to fields aliases in current schema

    """

    class Config(SchemaConfig):
        pass

    @property
    def __sc_params__(self) -> Dict[str, Any]:
        """Magic method for access all @sc_param decorated properties

        Returns:
            dict with all @sc_param decorated properties

        """
        return {
            k: v for k, v in self.__class__.__dict__.items() if isinstance(v, sc_param)
        }

    @property
    def __selector__(self) -> Union[Selector, SelectorList]:
        """Get available cached Parsel.Selector or SelectorList object

        Returns:
            Parsel SelectorType object
        """
        return self._cached_parser

    def __init__(self, markup: Union[str, bytes, Selector, SelectorList]):
        """Create a new object by parsing fields from markup.

        Args:
            markup: string, bytes or parsel.Selector object
        Raises:
            TypeError: if markup is not string, bytes or Selector objects
        """
        self._cached_parser: Union[Selector, SelectorList]
        self._markup: str

        self.__init_markup(markup)
        self.__pre_validate_markup()
        self.__init_fields()

    def __init_markup(self, markup: Union[str, bytes, Selector, SelectorList]):
        if isinstance(markup, str):
            self._markup = markup
            self._cached_parser = Selector(markup, **self.Config.selector_kwargs)
        elif isinstance(markup, bytes):
            self._cached_parser = Selector(body=markup, **self.Config.selector_kwargs)
            self._markup = markup.decode()
        elif isinstance(markup, (Selector, SelectorList)):
            self._markup = markup.get()  # type: ignore
            self._cached_parser = markup
        else:
            raise TypeError(
                f"Markup support only str, bytes or Selector types, not {type(markup).__name__}"
            )

    def __pre_validate_markup(self):
        # find @markup_pre_validator decorated methods and validate
        for k, v in self.__class__.__dict__.items():
            if isinstance(v, BaseField) or isinstance(v, sc_param):
                continue
            if getattr(v, "__dict__", None) and (
                pre_validator := v.__dict__.get("__wrapped__")
            ):
                if issubclass(pre_validator, markup_pre_validator):
                    if not getattr(self, k)():
                        msg = f"Validation error in {self.__schema_name__}.{k} method"
                        raise SchemaPreValidationError(msg)

    def __init_fields(self) -> None:
        """Parse fields entrypoint.

        Automatically called in the `__init__` constructor
        """
        _logger.info(
            "[%s] Start parse fields count: %s",
            self.__schema_name__,
            len(self.__schema_fields__.keys()),
        )
        for name, field in self.__schema_fields__.items():
            field_type = self.__schema_annotations__[name]
            _logger.debug("Start parse attribute: `%s.%s`", self.__schema_name__, name)
            if getattr(field, "__I_AM_NESTED_FIELD__", False):
                field.type_ = field_type  # type: ignore
            value = field.sc_parse(self.__selector__)
            if self.Config.type_caster and field.auto_type and not field.is_default:
                value = self.Config.type_caster.cast(field_type, value)
            if not field._is_success and not field.is_default:
                _logger.error("Parse error in %s.%s field", self.__schema_name__, name)

            # disable default value flag
            if field.is_default:
                _logger.error(
                    "`%s.%s` failed parse in %r method, set default value",
                    self.__schema_name__,
                    name,
                    field._last_failed_method,
                )  # type: ignore
                field.is_default = False

            _logger.info("%s.%s = %s", self.__schema_name__, name, value)
            setattr(self, name, value)

    @property
    def __raw__(self) -> str:
        """Get raw string markdown value

        Returns:
            markup string object
        """
        return self._markup

    @staticmethod
    def _to_dict(
        value: Union["BaseSchema", List, Dict, Any]
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], Any]:
        """convert BaseSchema objects to build-in python objects like dict, list"""
        if isinstance(value, BaseSchema):
            return value.dict()

        elif isinstance(value, list):
            if all(isinstance(val, BaseSchema) for val in value):  # pragma: no cover
                return [val.dict() for val in value]
        return value

    def dict(self, *, by_alias: bool = True) -> Dict[str, Any]:
        """Convert schema object to python dict. if field have alias key - set alias key
        Args:
            by_alias: bool set key by field alias. Default True
        Returns:
            dictionary with all public fields and sc_param properties
        """
        result: Dict[str, Any] = {  # type: ignore
            self.__schema_aliases__.get(k, k): self._to_dict(getattr(self, k))
            for k, v in self.__sc_params__.items()
        }
        # parse public field keys
        for k, v in self.__dict__.items():
            if not k.startswith("_") and self.__schema_fields__.get(k):
                k = self.__schema_aliases__.get(k, k) if by_alias else k
                result[k] = self._to_dict(v)
        return result

    def __repr__(self):
        return f'{self.__schema_name__}({", ".join(self.__repr_args__())})'

    def __repr_args__(self) -> List[str]:
        args: Dict[str, Any] = {  # type: ignore
            k: getattr(self, k) for k, v in self.__sc_params__.items()
        }
        # parse public field keys
        for k, v in self.__dict__.items():
            if not k.startswith("_") and self.__schema_fields__.get(k):  # type: ignore
                if alias := self.__schema_aliases__.get(k):  # type: ignore
                    args[f"{alias}({k})"] = v
                else:
                    args[k] = v

        return [
            f"{k}={repr(v)}"
            if isinstance(v, BaseSchema)
            else f"{k}:{type(v).__name__}={repr(v)}"
            for k, v in args.items()
        ]

    @property
    def __schema_name__(self) -> str:
        """

        Returns:
            class name
        """
        return self.__class__.__name__
