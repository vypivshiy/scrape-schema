from typing import Optional, Annotated
import pytest

from selectolax.parser import HTMLParser

from scrape_schema import BaseSchema, MetaSchema
from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList
from scrape_schema.callbacks.slax import get_tag, get_text

from tests.fixtures import HTML


class SlaxSchema(BaseSchema):
    class Meta(MetaSchema):
        parsers_config = {HTMLParser: {}}

    lang: Annotated[str, SlaxSelect("html", callback=get_tag("lang"))]
    charset: Annotated[str, SlaxSelect("head > meta", 
                                       callback=get_tag("charset"), 
                                       factory=lambda s: s.replace("-", ""))]
    title: Annotated[str, SlaxSelect('head > title')]
    title_lower: Annotated[str, SlaxSelect("head > title",
                                           factory=lambda text: text.lower())]
    body_string: Annotated[str, SlaxSelect('body > p.body-string')]
    body_string_chars: Annotated[list[str], SlaxSelect('body > p.body-string',
                                                       factory=list)]
    body_string_flag: Annotated[bool, SlaxSelect('body > p.body-string')]
    body_int: Annotated[int, SlaxSelect('body > p.body-int')]
    body_float: Annotated[float, SlaxSelect("body > p.body-int")]
    body_int_x10: Annotated[int, SlaxSelect("body > p.body-int",
                                            factory=lambda el: int(el) * 10)]

    fail_value_1: Annotated[Optional[str], SlaxSelect('body > spam.egg')]
    fail_value_2: Annotated[bool, SlaxSelect("body > spam.egg")]
    fail_value_3: Annotated[str, SlaxSelect('body > spam.egg',
                                            default="spam")]

    body_int_list: Annotated[list[int], SlaxSelectList('body > a.body-list')]
    body_float_list: Annotated[list[float], SlaxSelectList('body > a.body-list')]
    max_body_list: Annotated[int, SlaxSelectList('body > a.body-list',
                                                 callback=lambda el: int(get_text()(el)),
                                                 factory=max)]
    body_float_flag: Annotated[bool, SlaxSelectList('body > a.body-list', factory=bool)]

    fail_list_1: Annotated[Optional[list[int]], SlaxSelectList('body > spam.egg')]
    fail_list_2: Annotated[bool, SlaxSelectList('body > spam.egg')]
    fail_list_3: Annotated[list[str], SlaxSelectList('body > spam.egg',
                                                     default=["spam", "egg"])]


SLAX_SCHEMA = SlaxSchema(HTML)


@pytest.mark.parametrize(
    "attr,result",
    [
        ("lang", "en"),
        ("charset", "UTF8"),
        ("title", "TEST PAGE"),
        ("title_lower", "test page"),
        ("body_string", "test-string"),
        ("body_string_chars", ["t", "e", "s", "t", "-", "s", "t", "r", "i", "n", "g"]),
        ("body_string_flag", True),
        ("body_int", 555),
        ("body_float", 555.0),
        ("body_int_x10", 5550),
        ("fail_value_1", None),
        ("fail_value_2", False),
        ("fail_value_3", "spam"),
        ("body_int_list", [666, 777, 888]),
        ("body_float_list", [666.0, 777.0, 888.0]),
        ("max_body_list", 888),
        ("body_float_flag", True),
        ("fail_list_1", None),
        ("fail_list_2", False),
        ("fail_list_3", ["spam", "egg"]),
    ]
)
def test_slax_parse(attr, result):
    value = getattr(SLAX_SCHEMA, attr)
    assert value == result
