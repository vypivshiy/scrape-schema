"""generate pydantic structure"""
from typing import NamedTuple, Type

from scrape_schema import BaseSchema, Nested, Parsel, sc_param
from scrape_schema._typing import get_args, get_origin
from scrape_schema.base import Field
from scrape_schema.codegen.utils import (
    get_fields,
    get_fields_annotations,
    get_sc_params,
    render,
    type_to_str,
)

J2_PYDANTIC_TMP_SUB_SCHEMA = """
class {{ schema_name }}(BaseModel):
    {% for field in field_signatures -%}
        {{ field }}
    {% endfor -%}
    {% for param in sc_param_signatures -%}
        {{ param }}
    {% endfor -%}
"""

J2_PYDANTIC_TMP_MAIN = '''
"""Created by scrape-schema codegen"""

from typing import Any, Optional
from pydantic import BaseModel, Field
{% for sub_schema in sub_schemas %}
    {{ sub_schema }}
{%- endfor %}

class {{ schema_name }}(BaseModel):
    {% for field in field_signatures -%}
        {{ field }}
    {% endfor -%}
    {% for param in sc_param_signatures -%}
        {{ param }}
    {% endfor -%}
'''


class FieldSignature(NamedTuple):
    name: str
    type_: Type
    field: Field

    def __str__(self):
        type_ = type_to_str(self.type_)
        if isinstance(self.field, Nested):
            return f"{self.name}: {type_}"
        if self.field.alias and self.field.default is not Ellipsis:
            return (
                f"{self.name}: {type_} = "
                f"Field(default={self.field.default!r}, alias={self.field.alias!r})"
            )
        elif self.field.alias:
            return f"{self.name}: {type_} = Field(alias={self.field.alias!r})"
        elif self.field.default is not Ellipsis:
            return f"{self.name}: {type_} = {self.field.default!r}"
        return f"{self.name}: {type_}"


class ScParamSignature(NamedTuple):
    name: str
    type_: Type

    def __str__(self):
        type_ = type_to_str(self.type_)
        return f"{self.name}: {type_}"


def parse_sub_schema(sub_schema: Type[BaseSchema]) -> list[str]:
    sub_schemas: list[str] = []
    field_signatures: list[FieldSignature] = []
    params_signature: list[ScParamSignature] = []
    annotations = get_fields_annotations(sub_schema)

    schema = get_args(sub_schema)[0] if get_origin(sub_schema) is list else sub_schema
    for k, v in get_fields(schema).items():
        if isinstance(v, Nested):
            type_ = annotations.get(k)
            sub_schemas.extend(parse_sub_schema(type_))  # type: ignore
            field_signatures.append(
                FieldSignature(name=k, type_=type_, field=v)  # type: ignore
            )
        else:
            field_signatures.append(
                FieldSignature(name=k, type_=annotations.get(k), field=v)
            )  # type: ignore

    for k, v in get_sc_params(schema).items():
        params_signature.append(ScParamSignature(name=k, type_=v))

    sub_schemas.append(
        render(
            J2_PYDANTIC_TMP_SUB_SCHEMA,
            field_signatures=field_signatures,
            schema_name=schema.__name__,
            sc_param_signatures=params_signature,
        )
    )
    return sub_schemas


def scrape_schema_to_pydantic(schema: Type[BaseSchema]) -> str:
    sub_schemas: list[str] = []
    field_signatures: list[FieldSignature] = []
    params_signature: list[ScParamSignature] = []
    annotations = get_fields_annotations(schema)
    for k, v in get_fields(schema).items():
        if isinstance(v, Nested):
            type_ = annotations.get(k)
            sub_schemas.extend(parse_sub_schema(type_))  # type: ignore
            field_signatures.append(
                FieldSignature(name=k, type_=type_, field=v)  # type: ignore
            )
        else:
            field_signatures.append(
                FieldSignature(name=k, type_=annotations.get(k), field=v)
            )  # type: ignore
    for k, v in get_sc_params(schema).items():
        params_signature.append(ScParamSignature(name=k, type_=v))

    return render(
        J2_PYDANTIC_TMP_MAIN,
        sub_schemas=list(set(sub_schemas)),
        schema_name=schema.__name__,
        field_signatures=field_signatures,
        sc_param_signatures=params_signature,
    )


def generate_pydantic_schema(schema_entrypoint: Type[BaseSchema]):
    return scrape_schema_to_pydantic(schema_entrypoint)


if __name__ == "__main__":
    from typing import Optional

    class Item(BaseSchema):
        foo: str = Parsel().xpath("//a").get()
        bar: float = Parsel().xpath("//ul/li").get()

        @sc_param
        def spammers(self) -> list[int]:
            return [1, 2, 3]

    class Schema(BaseSchema):
        h: str = Parsel().xpath("//h1/text()").get()
        a: str = Parsel(default="0").xpath("").get()
        b: int = Parsel(alias="alias").xpath("a").get()
        c: str = Parsel(alias="alias2", default="def")
        item: Item = Nested(Parsel().xpath("//div"))
        items: list[Item] = Nested(Parsel().xpath("//div"))
        opt: Optional[int] = Parsel().get()

        @sc_param
        def spam(self):
            return "spam"

        @sc_param
        def egg(self) -> int:
            return 1

    code = generate_pydantic_schema(Schema)
    print(code)
    # models check
    assert "class Item(BaseModel)" in code
    assert "Schema(BaseModel)" in code
    # attrs check
    assert "c: str = Field(default='def', alias='alias2')" in code
    assert "b: int = Field(alias='alias')" in code
    # sc_params
    assert "spammers: list[int]" in code
