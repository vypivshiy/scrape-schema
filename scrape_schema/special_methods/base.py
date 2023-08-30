from abc import abstractmethod
from enum import Enum
from typing import Any, Dict, NamedTuple, Protocol, Tuple, Union


class SpecialMethods(Enum):
    """enumeration of special methods for fields

    Attributes:
        FN: execute function
        CONCAT_L: execute left string concatenation
        CONCAT_R: execute right string concatenation
        REPLACE: execute `str.replace` method
        REGEX_SEARCH: execute `re.search()` method
        REGEX_FINDALL: execute `re.findall()` method
        CHOMP_JS_PARSE: execute `chompjs.parse_js_object()` method
        CHOMP_JS_PARSE_ALL: execute `chompjs.parse_js_objects()` method
    """

    # special methods for another methods
    FN = 0
    CONCAT_L = 1
    CONCAT_R = 2
    REPLACE = 3
    REGEX_SEARCH = 4
    REGEX_FINDALL = 5
    CHOMP_JS_PARSE = 6
    CHOMP_JS_PARSE_ALL = 7


class MarkupMethod(NamedTuple):
    """MarkupMethod structure for provide fluid interface

    Attributes:
        METHOD_NAME: method name or SpecialMethod Enum value
        args: arguments to be passed to the method
        kwargs: kwargs to be passed to the method
    """

    METHOD_NAME: Union[str, SpecialMethods]
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = {}

    def __repr__(self):
        arguments = ""
        if self.args:
            arguments += ", ".join(str(a) for a in self.args)
        if self.kwargs:
            arguments += ", " + ", ".join(f"{k}={v}" for k, v in self.kwargs.items())

        method = (
            self.METHOD_NAME.name
            if isinstance(self.METHOD_NAME, SpecialMethods)
            else self.METHOD_NAME
        )
        return f"{method}({arguments})"  # pragma: no cover


class SpecialMethodCallable(Protocol):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        pass  # pragma: no cover


class BaseSpecialMethodStrategy:
    @abstractmethod
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        pass  # pragma: no cover


class SpecialMethodsHandler:
    def __init__(self):
        """Special method handler"""
        self.spec_methods_dict: Dict[SpecialMethods, SpecialMethodCallable] = {}  # type: ignore

    def add_method(
        self, spec_method: SpecialMethods, strategy: SpecialMethodCallable
    ) -> None:
        """Add special method to handler storage"""
        self.spec_methods_dict[spec_method] = strategy

    def handle(self, method: MarkupMethod, markup: Any, **kwargs) -> Any:
        """Handle special method

        Args:
            method: MarkupMethod object
            markup: value
            **kwargs: any keyword arguments

        Returns:
            method execution result
        Raises:
            TypeError if special methods not contains in this handler object
        """
        if isinstance(method.METHOD_NAME, SpecialMethods):
            return self.spec_methods_dict[method.METHOD_NAME](markup, method, **kwargs)
        raise TypeError("Unknown special method")  # pragma: no cover
