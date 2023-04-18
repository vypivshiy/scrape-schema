import json
import re
from dataclasses import dataclass, is_dataclass
from typing import Annotated, Any, Optional

from bs4 import BeautifulSoup
from fixtures import HTML

from scrape_schema import BaseConfigField, BaseField, BaseSchema, BaseSchemaConfig
from scrape_schema.callbacks.soup import crop_by_tag
from scrape_schema.fields.nested import Nested
from scrape_schema.fields.soup import SoupFind, SoupFindList


class FieldTitle(BaseField):
    def _parse(self, markup: str) -> Optional[str]:
        if match := re.search(r"<title>(.*?)</title>", markup):
            return match[1]
        return None


class FieldSoupImages(BaseField):
    class Config(BaseConfigField):
        parser = BeautifulSoup

    def _parse(self, markup: BeautifulSoup) -> list[str]:
        if results := markup.find_all("img"):
            return [element["src"] for element in results if element.get("src")]
        return []


@dataclass
class DictData:
    p: str
    a_int: list[int]


class FeaturesNested(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    p: Annotated[str, SoupFind('<p class="string">')]
    a_int: Annotated[list[int], SoupFindList('<a class="list">')]


class FeaturesSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "html.parser"}}

    title = FieldTitle()
    p_sub_strings: Annotated[
        list[str],
        SoupFindList(
            "<p>",
            # soup get return list names
            filter_=lambda el: el.get("class", [None])[0] == "sub-string",
        ),
    ]
    images = FieldSoupImages()
    # convert nested class to dict
    sub_dict: Annotated[
        dict[str, Any],
        Nested(
            FeaturesNested,
            crop_rule=crop_by_tag({"name": "div", "class_": "dict"}),
            factory=lambda schema: schema.dict(),
        ),
    ]
    # convert nested class to dataclass
    sub_dataclass: Annotated[
        DictData,
        Nested(
            FeaturesNested,
            crop_rule=crop_by_tag({"name": "div", "class_": "dict"}),
            factory=lambda schema: DictData(**schema.dict()),
        ),
    ]

    sub_json_str: Annotated[
        str,
        Nested(
            FeaturesNested,
            crop_rule=crop_by_tag({"name": "div", "class_": "dict"}),
            factory=lambda schema: json.dumps(schema.dict()),
        ),
    ]


FEATURES_SCHEMA = FeaturesSchema(HTML)


def test_custom_field():
    assert FEATURES_SCHEMA.title == "TEST PAGE"
    assert FEATURES_SCHEMA.images == ["/foo.png", "/baz.png", "/bar.png"]


def test_filter():
    assert FEATURES_SCHEMA.p_sub_strings == ["spam-1", "spam-2", "spam-3"]


def test_factory():
    assert isinstance(FEATURES_SCHEMA.sub_dict, dict)
    assert FEATURES_SCHEMA.sub_dict == {"a_int": [1, 2, 3, 4, 5, 6, 7, 8, 9], "p": "test-1"}
    assert is_dataclass(FEATURES_SCHEMA.sub_dataclass)
    assert FEATURES_SCHEMA.sub_dataclass == DictData(
        p="test-1", a_int=[1, 2, 3, 4, 5, 6, 7, 8, 9]
    )
    assert isinstance(FEATURES_SCHEMA.sub_json_str, str)
    assert (
        FEATURES_SCHEMA.sub_json_str == '{"p": "test-1", "a_int": [1, 2, 3, 4, 5, 6, 7, 8, 9]}'
    )
