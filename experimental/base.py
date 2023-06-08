from enum import Enum

from typing import Dict, Type, Any, Optional, NamedTuple, Tuple, List, Callable, Set, Union
from typing_extensions import Self, Annotated, get_origin, get_args, get_type_hints


from bs4 import BeautifulSoup

from scrape_schema._type_caster import TypeCaster


class SpecialMethods(Enum):
    filter = "%filter%"
    sort = "%sort%"


class MarkupMethod(NamedTuple):
    method_name: Union[str, SpecialMethods]
    args: Tuple[Any, ...] = ()
    kwargs: Dict[str, Any] = {}


class FieldConfig:
    instance: Type[Any] = type(None)
    defaults: Dict[str, Any] = {}


class BaseField:
    class Config(FieldConfig):
        pass

    def __init__(self, cast_type: bool = True):
        """

        :rtype: Any
        """
        self._cast_type = cast_type
        self._t_caster = TypeCaster()
        self._methods_stack: List[MarkupMethod] = []

    def _prepare_markup(self, markup):
        if isinstance(self.Config.instance, type(None)):
            return markup
        elif isinstance(markup, str):
            return self.Config.instance(markup)(**self.Config.defaults)
        return markup

    @staticmethod
    def _special_method(markup, method: MarkupMethod):
        if method.method_name == SpecialMethods.filter and isinstance(markup, list):
            return [r for r in markup if method.kwargs['func'](r)]

        elif method.method_name == SpecialMethods.sort and isinstance(markup, list):
            return sorted(markup, **method.kwargs)

        return markup

    def _call_stack_methods(self, markup) -> Any:
        result = markup
        for method in self._methods_stack:
            if method.method_name is SpecialMethods:
                result = self._special_method(result, method)
            else:
                result = getattr(result, method.method_name)(*method.args, **method.kwargs)
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


class Soup(BaseField):
    class Config(FieldConfig):
        instance = BeautifulSoup
        defaults = {"features": "html.parser"}

    def find(self, name=None, attrs=None, recursive=True, string=None, **kwargs):
        """Look in the children of this PageElement and find the first
               PageElement that matches the given criteria.

               All find_* methods take a common set of arguments. See the online
               documentation for detailed explanations.

               :param name: A filter on tag name.
               :param attrs: A dictionary of filters on attribute values.
               :param recursive: If this is True, find() will perform a
                   recursive search of this PageElement's children. Otherwise,
                   only the direct children will be considered.
               :param limit: Stop looking after finding this many results.
               :kwargs: A dictionary of filters on attribute values.
               :return: A PageElement.
               :rtype: bs4.element.Tag | bs4.element.NavigableString
               """
        if attrs is None:
            attrs = {}
        # BeautifulSoup.find()
        return self.add_method("find", name=name, attrs=attrs, recursive=recursive, string=string, **kwargs)

    def find_all(self, name=None, attrs=None, recursive=True, string=None, limit=None, **kwargs):
        """Look in the children of this PageElement and find all
                PageElements that match the given criteria.

                All find_* methods take a common set of arguments. See the online
                documentation for detailed explanations.

                :param name: A filter on tag name.
                :param attrs: A dictionary of filters on attribute values.
                :param recursive: If this is True, find_all() will perform a
                    recursive search of this PageElement's children. Otherwise,
                    only the direct children will be considered.
                :param limit: Stop looking after finding this many results.
                :kwargs: A dictionary of filters on attribute values.
                :return: A ResultSet of PageElements.
                :rtype: bs4.element.ResultSet
                """
        if attrs is None:
            attrs = {}
        return self.add_method("find_all", name=name, attrs=attrs, recursive=recursive, string=string, limit=limit, **kwargs)

    def find_parent(self, *args, **kwargs):
        return self.add_method('find_parent', *args, **kwargs)

    def find_parents(self, *args, **kwargs):
        return self.add_method('find_parents', *args, **kwargs)

    def select(self, *args, **kwargs):
        return self.add_method('select', *args, **kwargs)

    def select_one(self, *args, **kwargs):
        return self.add_method('select_one', *args, **kwargs)

    def get(self, key: str, default=None):
        return self.add_method('get', key=key, default=default)

    def get_text(self, *args, **kwargs):
        return self.add_method('get_text', *args, **kwargs)


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
        # cache parsers
        self.cached_parsers: Dict[str, Any] = {  # type: ignore
            k: v(markup, **self.Config.parsers[v])
            for k, v in self.__parsers__.items()
        }
        self.__init_fields__()

    def clear_cache(self):
        self.cached_parsers.clear()

    def __init_fields__(self):
        for name, field in self.__schema_fields__.items():
            cache_key = field.Config.instance.__name__
            field_type = self.__schema_annotations__[name]
            setattr(self, name, field.parse(self.cached_parsers[cache_key], field_type))


if __name__ == '__main__':
    class Schema(BaseSchema):
        class Config:
            parsers = {BeautifulSoup: {"features": 'html.parser'}}

        title: Annotated[str, Soup().find("title").get_text()]
        href: Annotated[str, Soup().find("div").find("a").get('href')]
        a_text: Annotated[float, Soup().find("a").get_text()]


    sc = Schema('<title>"test title"</title>\n<div><a href="example.com">123</a><\div>\n')
    print(sc.title, sc.href, sc.a_text)
