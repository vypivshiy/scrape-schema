from typing import List

import pytest
from parsel import Selector
from tests.fixtures import HTML_FOR_SCHEMA

from scrape_schema import BaseSchema, Nested, Parsel, Sc, sc_param


class SubSchema(BaseSchema):
    item: Sc[str, Parsel().xpath("//p/text()").get()]
    price: Sc[int, Parsel().xpath("//div[@class='price']/text()").get()]
    _available: Sc[
        str,
        Parsel().xpath("//div[contains(@class, 'available')]").attrib.get(key="class"),
    ]

    @sc_param
    def available(self) -> bool:
        return "yes" in self._available


class Schema(BaseSchema):
    first_item: Sc[SubSchema, Nested(Parsel().xpath("//ul").xpath("./li")[0])]
    last_item: Sc[SubSchema, Nested(Parsel().xpath("//ul").xpath("./li")[-1])]
    items: Sc[List[SubSchema], Nested(Parsel().xpath("//body/ul").xpath("./li"))]

    @sc_param
    def max_price_item(self):
        return max(self.items, key=lambda obj: obj.price)


def test_parse_schema():
    assert Schema(HTML_FOR_SCHEMA).dict() == {
        "max_price_item": {"available": False, "item": "ferrari", "price": 99999999},
        "first_item": {"available": True, "item": "audi", "price": 10000},
        "last_item": {"available": True, "item": "suzuki", "price": 25000},
        "items": [
            {"available": True, "item": "audi", "price": 10000},
            {"available": False, "item": "ferrari", "price": 99999999},
            {"available": True, "item": "bentley", "price": 50000},
            {"available": True, "item": "ford", "price": 20000},
            {"available": True, "item": "suzuki", "price": 25000},
        ],
    }


def test_parse_from_selector():
    sel = Selector(HTML_FOR_SCHEMA)

    assert Schema(sel).dict() == {
        "max_price_item": {"available": False, "item": "ferrari", "price": 99999999},
        "first_item": {"available": True, "item": "audi", "price": 10000},
        "last_item": {"available": True, "item": "suzuki", "price": 25000},
        "items": [
            {"available": True, "item": "audi", "price": 10000},
            {"available": False, "item": "ferrari", "price": 99999999},
            {"available": True, "item": "bentley", "price": 50000},
            {"available": True, "item": "ford", "price": 20000},
            {"available": True, "item": "suzuki", "price": 25000},
        ],
    }


def test_parse_from_selector_list():
    sel = Selector(HTML_FOR_SCHEMA)
    sel_list = sel.xpath("//body/ul").xpath("./li")
    assert SubSchema(sel_list).dict() == {
        "available": True,
        "item": "audi",
        "price": 10000,
    }


def test_parse_bytes():
    byte_body = HTML_FOR_SCHEMA.encode()
    assert Schema(byte_body).dict() == {
        "max_price_item": {"available": False, "item": "ferrari", "price": 99999999},
        "first_item": {"available": True, "item": "audi", "price": 10000},
        "last_item": {"available": True, "item": "suzuki", "price": 25000},
        "items": [
            {"available": True, "item": "audi", "price": 10000},
            {"available": False, "item": "ferrari", "price": 99999999},
            {"available": True, "item": "bentley", "price": 50000},
            {"available": True, "item": "ford", "price": 20000},
            {"available": True, "item": "suzuki", "price": 25000},
        ],
    }


def test_incorrect_type():
    with pytest.raises(TypeError):
        Schema(0).dict()


def test_magic_methods():
    sel = Selector(HTML_FOR_SCHEMA)
    schema = Schema(sel)
    schema2 = Schema(HTML_FOR_SCHEMA)
    assert schema2.__raw__ == HTML_FOR_SCHEMA

    assert schema.__selector__ == sel
    assert schema.__sc_params__.get("max_price_item")


def test_default_field_value():
    class DefaultSchema(BaseSchema):
        a: Sc[str, Parsel(default="fail").xpath("//div/div").css("p").get()]
        b: Sc[
            int,
            Parsel(default="fail").xpath("//div/div").css("p").get().concat_l("test"),
        ]
        c: Sc[
            str, Parsel().xpath("//div/div").css("p").get()
        ]  # return None and has default value, set 'fail'

    assert DefaultSchema("???").dict() == {"a": "fail", "b": "fail", "c": None}
