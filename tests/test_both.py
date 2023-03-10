from operator import eq

from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser

from scrape_schema import BaseSchema
from scrape_schema.fields.slax import SLaxSelect, SLaxSelectList
from scrape_schema.fields.soup import SoupFind, SoupSelect, SoupFindList, SoupSelectList
from scrape_schema.fields.nested import NestedList, Nested
from scrape_schema.fields.regex import ReMatch, ReMatchList

from scrape_schema.tools.slax import crop_by_slax, crop_by_slax_all

from fixtures import HTML


class MixSchemaConfig(BaseSchema):
    __MARKUP_PARSERS__ = {HTMLParser: {}, BeautifulSoup: {"features": "html.parser"}}


class NestedSubMixSlax(MixSchemaConfig):
    p: str = SLaxSelect("p.sub-string", factory=lambda text: text.strip())
    a: list[int] = SoupSelectList("a.sub-list")


class NestedSubMixSoupFind(MixSchemaConfig):
    p: str = SoupFind('<p class="sub-string">', factory=lambda text: text.strip())
    a: list[int] = SoupFindList('<a class="sub-list">')


class NestedSubMixSoupSelect(MixSchemaConfig):
    p: str = SoupSelect("p.sub-string", factory=lambda text: text.strip())
    a: list[int] = SLaxSelectList("a.sub-list")


class NestedSubMixRe(MixSchemaConfig):
    p: str = ReMatch(r'<p class="sub-string">(.*?)</p>', factory=lambda text: text.strip())
    a: list[int] = ReMatchList(r'<a class="sub-list">(\d+)</a>')


class NestedDivSoupFind(MixSchemaConfig):
    p: str = SoupFind('<p class="string">')
    a_int: list[int] = SoupFindList('<a class="list">')
    sub_dict_slax: NestedSubMixSlax = Nested(NestedSubMixSlax, crop_rule=crop_by_slax('div.sub-dict'))
    sub_dict_soup_find: NestedSubMixSlax = Nested(NestedSubMixSoupFind, crop_rule=crop_by_slax('div.sub-dict'))
    sub_dict_soup_select: NestedSubMixSlax = Nested(NestedSubMixSoupSelect, crop_rule=crop_by_slax('div.sub-dict'))
    sub_dict_re: NestedSubMixSlax = Nested(NestedSubMixRe, crop_rule=crop_by_slax('div.sub-dict'))


class MixSchema(MixSchemaConfig):
    title_soup_find: str = SoupFind("<title>")
    title_soup_select: str = SoupSelect("head > title")
    title_slax: str = SLaxSelect('head > title')
    title_re: str = ReMatch(R"<title>(.*?)</title>")

    float_soup_find: float = SoupFind('<p class="body-int">555</p>')
    float_soup_select: float = SoupSelect('body > p.body-int')
    float_slax: float = SLaxSelect('body > p.body-int')
    float_re: float = ReMatch(r'<p class="body-int">(\d+)</p>')

    list_int_soup_find: list[int] = SoupFindList('<a class="body-list">')
    list_int_soup_select: list[int] = SoupSelectList("body > a.body-list")
    list_int_slax: list[int] = SLaxSelectList("body > a.body-list")
    list_int_re: list[int] = ReMatchList(r'<a class="body-list">(\d+)</a>')

    nested_list: list[NestedDivSoupFind] = NestedList(NestedDivSoupFind,
                                                      crop_rule=crop_by_slax_all('body > div.dict'))


MIX_SCHEMA = MixSchema(HTML)


def test_title():
    assert MIX_SCHEMA.title_soup_find == \
           MIX_SCHEMA.title_soup_select == \
           MIX_SCHEMA.title_slax == \
           MIX_SCHEMA.title_re


def test_list():
    assert MIX_SCHEMA.list_int_soup_find == \
           MIX_SCHEMA.list_int_soup_select == \
           MIX_SCHEMA.list_int_slax == \
           MIX_SCHEMA.list_int_re


def test_float():
    assert MIX_SCHEMA.float_soup_find == \
           MIX_SCHEMA.float_soup_select == \
           MIX_SCHEMA.float_slax == \
           MIX_SCHEMA.float_re


def test_assert_mix_nested():
    for schema in MIX_SCHEMA.nested_list:
        assert schema.sub_dict_re.dict() == \
               schema.sub_dict_slax.dict() == \
               schema.sub_dict_soup_find.dict() == \
               schema.sub_dict_soup_select.dict()
