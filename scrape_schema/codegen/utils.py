"""shortcuts for get access to BaseSchema attributes"""
from typing import TYPE_CHECKING, Any, Dict, List, Type, Union

try:
    from jinja2 import Template
except ImportError:
    raise ImportError(
        "Required jinja2. Type 'pip install scrape-schema[codegen]' or 'pip install jinja2'"
    )

from scrape_schema._typing import NoneType, get_args, get_origin, get_type_hints
from scrape_schema.base import sc_param

if TYPE_CHECKING:
    from scrape_schema import BaseSchema
    from scrape_schema.base import BaseField
    from scrape_schema.special_methods import MarkupMethod

    _SCHEMA_TYPE = Union[Type[BaseSchema], BaseSchema]


def get_stack_methods(field: "BaseField") -> List["MarkupMethod"]:
    return field._stack_methods


def get_fields_annotations(schema: "_SCHEMA_TYPE") -> Dict[str, Type]:
    if get_origin(schema) is list:
        return get_args(schema)[0].__schema_annotations__
    return schema.__schema_annotations__


def get_fields(schema: "_SCHEMA_TYPE") -> Dict[str, "BaseField"]:
    return schema.__schema_fields__


def get_fields_aliases(schema: "_SCHEMA_TYPE") -> Dict[str, str]:
    return schema.__schema_aliases__


def get_sc_params(schema: "_SCHEMA_TYPE") -> Dict[str, Type]:
    """extract @sc_param getters"""
    result: Dict[str, Type] = {}
    for k, v in schema.__dict__.items():
        if isinstance(v, sc_param):
            schema_param = getattr(schema, k).fget
            return_antd = get_type_hints(schema_param).get("return", Any)
            result[k] = return_antd
    return result


def type_to_str(type_hint):
    if len(get_args(type_hint)) == 0:
        return type_hint.__name__
    origin = get_origin(type_hint)
    args = get_args(type_hint)
    if origin == Union and NoneType in args:
        args = tuple(a for a in args if a != NoneType)
        return f"Optional[{', '.join(a.__name__ if len(get_args(a)) == 0 else type_to_str(a) for a in args)}]"
    return f"{origin.__name__}[{', '.join(a.__name__ if len(get_args(a)) == 0 else type_to_str(a) for a in args)}]"


def render(template: str, *args, **kwargs) -> str:
    return Template(template).render(*args, **kwargs)


if __name__ == "__main__":
    assert type_to_str(list[int]) == "list[int]"
    assert type_to_str(dict[int, str]) == "dict[int, str]"
