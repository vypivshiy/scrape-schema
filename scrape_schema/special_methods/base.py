from abc import abstractmethod
from enum import Enum
from typing import Any, Dict, NamedTuple, Protocol, Tuple, Union


class SpecialMethods(Enum):
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
    METHOD_NAME: Union[str, SpecialMethods]
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = {}

    def __repr__(self):
        return f"{self.METHOD_NAME} args={self.args}, kwargs={self.kwargs}"


class SpecialMethodCallable(Protocol):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        pass


class BaseSpecialMethodStrategy:
    @abstractmethod
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        pass


class SpecialMethodsHandler:
    def __init__(self):
        self.spec_methods_dict: Dict[SpecialMethods, SpecialMethodCallable] = {}  # type: ignore

    def add_method(self, spec_method: SpecialMethods, strategy: SpecialMethodCallable):
        self.spec_methods_dict[spec_method] = strategy

    def handle(self, method: MarkupMethod, markup: Any, **kwargs):
        if isinstance(method.METHOD_NAME, SpecialMethods):
            return self.spec_methods_dict[method.METHOD_NAME](markup, method, **kwargs)
        raise TypeError("Unknown special method")
