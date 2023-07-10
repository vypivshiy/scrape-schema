from typing import List

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


def test_schema():
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
