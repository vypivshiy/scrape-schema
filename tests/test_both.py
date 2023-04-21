from typing import Annotated

from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser
from tests.fixtures import HTML

from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.callbacks.slax import crop_by_slax, crop_by_slax_all
from scrape_schema.fields.nested import Nested, NestedList
from scrape_schema.fields.regex import ReMatch, ReMatchList
from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect, SoupSelectList


class BaseMixSchema(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}, BeautifulSoup: {"features": "html.parser"}}


class NestedSubMixSlax(BaseMixSchema):
    p: Annotated[str, SlaxSelect("p.sub-string", factory=lambda text: text.strip())]
    a: Annotated[list[int], SoupSelectList("a.sub-list")]


class NestedSubMixSoupFind(BaseMixSchema):
    p: Annotated[
        str, SoupFind('<p class="sub-string">', factory=lambda text: text.strip())
    ]
    a: Annotated[list[int], SoupFindList('<a class="sub-list">')]


class NestedSubMixSoupSelect(BaseMixSchema):
    p: Annotated[str, SoupSelect("p.sub-string", factory=lambda text: text.strip())]
    a: Annotated[list[int], SlaxSelectList("a.sub-list")]


class NestedSubMixRe(BaseMixSchema):
    p: Annotated[
        str,
        ReMatch(r'<p class="sub-string">(.*?)</p>', factory=lambda text: text.strip()),
    ]
    a: Annotated[list[int], ReMatchList(r'<a class="sub-list">(\d+)</a>')]


class NestedDivSoupFind(BaseMixSchema):
    p: Annotated[str, SoupFind('<p class="string">')]
    a_int: Annotated[list[int], SoupFindList('<a class="list">')]
    sub_dict_slax: Annotated[
        NestedSubMixSlax,
        Nested(NestedSubMixSlax, crop_rule=crop_by_slax("div.sub-dict")),
    ]
    sub_dict_soup_find: Annotated[
        NestedSubMixSlax,
        Nested(NestedSubMixSoupFind, crop_rule=crop_by_slax("div.sub-dict")),
    ]
    sub_dict_soup_select: Annotated[
        NestedSubMixSlax,
        Nested(NestedSubMixSoupSelect, crop_rule=crop_by_slax("div.sub-dict")),
    ]
    sub_dict_re: Annotated[
        NestedSubMixSlax, Nested(NestedSubMixRe, crop_rule=crop_by_slax("div.sub-dict"))
    ]


class MixSchema(BaseMixSchema):
    title_soup_find: Annotated[str, SoupFind("<title>")]
    title_soup_select: Annotated[str, SoupSelect("head > title")]
    title_slax: Annotated[str, SlaxSelect("head > title")]
    title_re: Annotated[str, ReMatch(R"<title>(.*?)</title>")]

    float_soup_find: Annotated[float, SoupFind('<p class="body-int">555</p>')]
    float_soup_select: Annotated[float, SoupSelect("body > p.body-int")]
    float_slax: Annotated[float, SlaxSelect("body > p.body-int")]
    float_re: Annotated[float, ReMatch(r'<p class="body-int">(\d+)</p>')]

    list_int_soup_find: Annotated[list[int], SoupFindList('<a class="body-list">')]
    list_int_soup_select: Annotated[list[int], SoupSelectList("body > a.body-list")]
    list_int_slax: Annotated[list[int], SlaxSelectList("body > a.body-list")]
    list_int_re: Annotated[list[int], ReMatchList(r'<a class="body-list">(\d+)</a>')]

    nested_list: Annotated[
        list[NestedDivSoupFind],
        NestedList(NestedDivSoupFind, crop_rule=crop_by_slax_all("body > div.dict")),
    ]


MIX_SCHEMA = MixSchema(HTML)


def test_title():
    assert (
        MIX_SCHEMA.title_soup_find
        == MIX_SCHEMA.title_soup_select
        == MIX_SCHEMA.title_slax
        == MIX_SCHEMA.title_re
    )


def test_list():
    assert (
        MIX_SCHEMA.list_int_soup_find
        == MIX_SCHEMA.list_int_soup_select
        == MIX_SCHEMA.list_int_slax
        == MIX_SCHEMA.list_int_re
    )


def test_float():
    assert (
        MIX_SCHEMA.float_soup_find
        == MIX_SCHEMA.float_soup_select
        == MIX_SCHEMA.float_slax
        == MIX_SCHEMA.float_re
    )


def test_assert_mix_nested():
    for schema in MIX_SCHEMA.nested_list:
        assert (
            schema.sub_dict_re.dict()
            == schema.sub_dict_slax.dict()
            == schema.sub_dict_soup_find.dict()
            == schema.sub_dict_soup_select.dict()
        )
