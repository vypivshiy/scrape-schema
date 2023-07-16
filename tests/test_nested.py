from typing import List

import pytest
from tests.fixtures import HTML_FOR_SCHEMA

from scrape_schema import BaseSchema, Nested, Parsel, Sc, sc_param


class SubSchema(BaseSchema):
    item: Sc[str, Parsel().xpath("//p/text()").get()]


class Schema(BaseSchema):
    items: Sc[List[dict], Nested(Parsel().xpath("//body/ul").xpath("./li"))]


class Schema2(BaseSchema):
    first_item: Sc[dict, Nested(Parsel().xpath("//ul").xpath("./li")[0])]


def test_nested_failed_type():
    with pytest.raises(TypeError):
        Schema(HTML_FOR_SCHEMA)


def test_nested_failed_type2():
    with pytest.raises(TypeError):
        Schema2(HTML_FOR_SCHEMA)


def test_nested_without_schema():
    with pytest.raises(TypeError):
        Nested(Parsel().xpath("//ul").xpath("./li")).sc_parse(HTML_FOR_SCHEMA)
