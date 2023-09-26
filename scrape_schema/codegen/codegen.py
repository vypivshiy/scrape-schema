# mypy: disable-error-code="assignment"
# ruff: noqa: F405
# ruff: noqa: F403
# TODO this experimental POC, later this need refactoring and rewrite
import inspect
import random
import types
import warnings
from typing import List, Type

try:
    from jinja2 import Template
except ImportError:
    raise ImportError(
        "Required jinja2. For install, type pip install scrape-schema[codegen]"
    )

from scrape_schema.base import BaseField, BaseSchema
from scrape_schema.codegen.constants import *
from scrape_schema.field import Parsel
from scrape_schema.special_methods.base import MarkupMethod, SpecialMethods

__all__ = ["generate_code"]


def _extract_stack_methods(field: BaseField) -> List[MarkupMethod]:
    return field._stack_methods


def _generate_method_name(name: str) -> str:
    return Template(J2_CLASS_METHOD_NAME).render(name=name)


def _extract_lambda_source(lambda_func):
    source_lines, _ = inspect.getsourcelines(lambda_func)
    source_code = "".join(source_lines).strip()

    return source_code


def _extract_def_code(function):
    return inspect.getsource(function)


def _generate_special_method(method: MarkupMethod):
    if method.METHOD_NAME == SpecialMethods.CONCAT_L:
        arg = method.args[0]
        return Template(J2_STEP_METHOD_CONCAT_L).render(arg=repr(arg))
    elif method.METHOD_NAME == SpecialMethods.CONCAT_R:
        arg = method.args[0]
        return Template(J2_STEP_METHOD_CONCAT_R).render(arg=repr(arg))
    elif method.METHOD_NAME == SpecialMethods.REPLACE:
        old, new, count = method.args
        return Template(J2_STEP_METHOD_REPLACE).render(old=old, new=new, count=count)
    elif method.METHOD_NAME == SpecialMethods.FN:
        func = method.kwargs["function"]
        if isinstance(func, types.LambdaType):
            code = _extract_lambda_source(func)
            return Template(J2_STEP_METHOD_FN_LAMBDA).render(code=code)
        elif inspect.isfunction(func):
            code = _extract_def_code(func)
            return Template(J2_STEP_METHOD_FN).render(
                code=code,
                rnd_hash=repr(random.randint(100, 999)),
            )
    elif method.METHOD_NAME == SpecialMethods.REGEX_SEARCH:
        pattern, groupdict, flags = method.args
        if groupdict:
            return Template(J2_STEP_METHOD_RE_SEARCH_GROUP_DICT).render(
                pattern=pattern, flags=flags
            )
        return Template(J2_STEP_METHOD_RE_SEARCH).render(pattern=pattern, flags=flags)
    elif method.METHOD_NAME == SpecialMethods.REGEX_FINDALL:
        pattern, groupdict, flags = method.args
        if groupdict:
            return Template(J2_STEP_METHOD_FINDALL_GROUP_DICT).render(
                pattern=pattern, flags=flags
            )
        return Template(J2_STEP_METHOD_FINDALL).render(pattern=pattern, flags=flags)
    elif method.METHOD_NAME == SpecialMethods.CHOMP_JS_PARSE:
        unicode_escape, json_params = method.args
        return Template(J2_STEP_METHOD_CHOMP_JS_PARSE).render(
            unicode_escape=unicode_escape, json_params=json_params
        )
    elif method.METHOD_NAME == SpecialMethods.CHOMP_JS_PARSE_ALL:
        unicode_escape, omitempty, json_params = method.args
        return Template(J2_STEP_METHOD_CHOMP_JS_PARSE_ALL).render(
            unicode_escape=unicode_escape, omitempty=omitempty, json_params=json_params
        )


def _generate_method_code(
    *, name: str, field: BaseField, methods: List[MarkupMethod]
) -> str:
    docstring = f"{repr(field)} signature"
    default_value = "..." if field.default is Ellipsis else field.default
    attr_name = field.alias or name
    method_name = _generate_method_name(name=name)
    first_step = Template(J2_METHOD_FIRST_STEP).render(expr=repr(methods[0]))
    method_steps = []
    for method in methods[1:]:
        if isinstance(method.METHOD_NAME, SpecialMethods):
            method_steps.append(_generate_special_method(method))
        elif method.METHOD_NAME == "__getitem__":
            item = method.args[0]
            method_steps.append(Template(J2_STEP_METHOD_GETITEM).render(arg=item))

        # parsel.Selector.re case
        elif method.METHOD_NAME == "re":
            regex, replace_entities = method.args
            regex = "r" + repr(regex).replace("\\", "", 1)
            method_steps.append(
                Template(J2_METHOD_SELECTOR_RE).render(
                    regex=regex, replace_entities=replace_entities
                )
            )
        else:
            method_steps.append(
                Template(J2_METHOD_SELECTOR_STEP).render(expr=repr(method))
            )
    return Template(J2_CLASS_METHOD).render(
        method_name=method_name,
        doc=docstring,
        name=repr(attr_name),
        default=default_value,
        first_step=first_step,
        steps=method_steps,
    )


def generate_code(schema: Type[BaseSchema]):
    """convert scrape_schema.BaseSchema type to python code

    this method exclude auto typing features and scrape-schema dependencies

    dependencies: parsel, chompjs, re
    """
    warnings.warn(
        "this function write just PoC and will be rewritten later",
        category=DeprecationWarning,
        stacklevel=2,
    )
    fields = schema.__schema_fields__
    fields_aliases = schema.__schema_aliases__
    schema_name = schema.__name__

    methods_code = []
    methods_meta = {}
    for name, field in fields.items():
        field_methods = _extract_stack_methods(field)
        if alias := fields_aliases.get(name, None):
            name = alias

        # assemble methods
        methods_code.append(
            _generate_method_code(name=name, field=field, methods=field_methods)
        )
        methods_meta[repr(name)] = f"self.{_generate_method_name(name)}(markup)"
    # generate code
    return Template(J2_CLASS).render(
        imports=J2_IMPORTS,
        schema_name=schema_name,
        methods_meta=methods_meta,
        methods_code=methods_code,
    )


if __name__ == "__main__":

    class Schema(BaseSchema):
        title: str = Parsel().xpath("//title/text()").get()
        div: List[str] = Parsel(alias="urls").xpath("//a/@href").getall()[0]

    print(generate_code(Schema))
    # f = Parsel(alias='title').xpath("//title/text()").get().concat_l("a")
    # print(generate(f))
