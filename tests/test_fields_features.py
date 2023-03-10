import re
from typing import Any
from dataclasses import dataclass, is_dataclass
import json

from bs4 import BeautifulSoup

import pytest

from scrape_schema import BaseSchema
from scrape_schema.base import BaseField
from scrape_schema.fields.nested import Nested
from scrape_schema.fields.soup import SoupFindList, SoupFind
from scrape_schema.tools.soup import crop_by_tag

from fixtures import HTML

from scrape_schema.exceptions import ValidationError


class FieldTitle(BaseField):
    def parse(self, instance: BaseSchema, name: str, markup: str) -> str:
        if match := re.search(r'<title>(.*?)</title>', markup):
            return match[1]
        return self.default


class FieldSoupImages(BaseField):
    __MARKUP_PARSER__ = BeautifulSoup

    def parse(self, instance: BaseSchema, name: str, markup: BeautifulSoup):
        if results := markup.find_all("img"):
            return [element['src'] for element in results if element.get("src")]
        return []


@dataclass
class DictData:
    p: str
    a_int: list[int]


class FeaturesNested(BaseSchema):
    __MARKUP_PARSERS__ = {BeautifulSoup: {"features": "html.parser"}}
    p: str = SoupFind('<p class="string">')
    a_int: list[int] = SoupFindList('<a class="list">')


class FeaturesSchema(BaseSchema):
    __MARKUP_PARSERS__ = {BeautifulSoup: {"features": "html.parser"}}
    title = FieldTitle()
    p_sub_strings: list[str] = SoupFindList("<p>",
                                            # soup get return list names
                                            filter_=lambda el: el.get("class", [None])[0] == "sub-string")
    images = FieldSoupImages()
    # convert nested class to dict
    sub_dict: dict[str, Any] = Nested(FeaturesNested,
                                      crop_rule=crop_by_tag({"name": "div", "class_": "dict"}),
                                      factory=lambda schema: schema.dict())
    # convert nested class to dataclass
    sub_dataclass: DictData = Nested(FeaturesNested,
                                     crop_rule=crop_by_tag({"name": "div", "class_": "dict"}),
                                     factory=lambda schema: DictData(**schema.dict()))
    sub_json_str: str = Nested(FeaturesNested,
                               crop_rule=crop_by_tag({"name": "div", "class_": "dict"}),
                               factory=lambda schema: json.dumps(schema.dict()))


class ValidationSchema(BaseSchema):
    __MARKUP_PARSERS__ = {BeautifulSoup: {"features": "html.parser"}}
    __VALIDATE__ = True
    p_sub_strings: list[str] = SoupFindList(
        "<p>",
        filter_=lambda el: el.get("class", [None])[0] == "sub-string",
        validator=lambda els: all(el.startswith("spam-") for el in els),
    )


class FailValidationSchema(BaseSchema):
    __MARKUP_PARSERS__ = {BeautifulSoup: {"features": "html.parser"}}
    __VALIDATE__ = True
    p_sub_strings: list[str] = SoupFindList(
        "<p>", validator=lambda els: all(el.startswith("spam-") for el in els)
    )


FEATURES_SCHEMA = FeaturesSchema(HTML)


def test_custom_field():
    assert FEATURES_SCHEMA.title == 'TEST PAGE'
    assert FEATURES_SCHEMA.images == ['/foo.png', '/baz.png', '/bar.png']


def test_filter():
    assert FEATURES_SCHEMA.p_sub_strings == ['spam-1', 'spam-2', 'spam-3']


def test_success_validator():
    schema = ValidationSchema(HTML)
    assert all(el.startswith("spam-") for el in schema.p_sub_strings)


def test_validate_error():
    with pytest.raises(ValidationError):
        FailValidationSchema(HTML)


def test_factory():
    assert isinstance(FEATURES_SCHEMA.sub_dict, dict)
    assert FEATURES_SCHEMA.sub_dict == {'a_int': [1, 2, 3, 4, 5, 6, 7, 8, 9], 'p': 'test-1'}
    assert is_dataclass(FEATURES_SCHEMA.sub_dataclass)
    assert FEATURES_SCHEMA.sub_dataclass == DictData(p="test-1", a_int=[1, 2, 3, 4, 5, 6, 7, 8, 9])
    assert isinstance(FEATURES_SCHEMA.sub_json_str, str)
    assert FEATURES_SCHEMA.sub_json_str == '{"p": "test-1", "a_int": [1, 2, 3, 4, 5, 6, 7, 8, 9]}'
