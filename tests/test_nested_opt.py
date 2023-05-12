"""optimised nested fields boost"""
from typing import List

from bs4 import BeautifulSoup
from parsel import Selector
from selectolax.parser import HTMLParser

from scrape_schema import BaseSchema, BaseSchemaConfig, ScField
from scrape_schema.callbacks.parsel import crop_by_selector_all, crop_by_xpath_all
from scrape_schema.callbacks.slax import crop_by_slax_all
from scrape_schema.callbacks.soup import crop_by_tag_all
from scrape_schema.fields.parsel import NestedParselList, ParselSelect, ParselXPath
from scrape_schema.fields.slax import NestedSlaxList, SlaxSelect
from scrape_schema.fields.soup import NestedSoupList, SoupFind

NESTED_HTML = """
<div>
    <p>spam</p>
</div>
<div>
    <p>egg</p>
</div>
<div>
    <p>spamegg</p>
</div>
"""


class BenchSchemaParselSel(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {Selector: {}}

    p: ScField[str, ParselSelect("p")]


class BenchSchemaParselXpath(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {Selector: {}}

    p: ScField[str, ParselXPath("//p")]


class BenchSchemaSoup(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {BeautifulSoup: {"features": "lxml"}}

    p: ScField[str, SoupFind("<p>")]


class BenchSchemaSlax(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}

    p: ScField[str, SlaxSelect("p")]


class SchemaEntrypoint(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {
            HTMLParser: {},
            Selector: {},
            BeautifulSoup: {"features": "lxml"},
        }

    soups: ScField[
        List[BenchSchemaSoup],
        NestedSoupList(
            BenchSchemaSoup,
            crop_rule=crop_by_tag_all("<div>"),
        ),
    ]
    parsel_xpaths: ScField[
        List[BenchSchemaParselXpath],
        NestedParselList(BenchSchemaParselXpath, crop_rule=crop_by_xpath_all("//div")),
    ]
    parsel_sels: ScField[
        List[BenchSchemaParselSel],
        NestedParselList(BenchSchemaParselSel, crop_rule=crop_by_selector_all("div")),
    ]
    slaxs: ScField[
        List[BenchSchemaSlax],
        NestedSlaxList(BenchSchemaSlax, crop_rule=crop_by_slax_all("div")),
    ]


BENCH_SCHEMA = SchemaEntrypoint(NESTED_HTML)


def test_optimized_nested():
    assert BENCH_SCHEMA.dict() == {
        "soups": [{"p": "spam"}, {"p": "egg"}, {"p": "spamegg"}],
        "parsel_xpaths": [{"p": "spam"}, {"p": "egg"}, {"p": "spamegg"}],
        "parsel_sels": [{"p": "spam"}, {"p": "egg"}, {"p": "spamegg"}],
        "slaxs": [{"p": "spam"}, {"p": "egg"}, {"p": "spamegg"}],
    }
