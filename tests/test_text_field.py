from typing import List

from tests.fixtures import RAW_TEXT

from scrape_schema import BaseSchema, Sc, Text, sc_param


class RawSchema(BaseSchema):
    ipv4: Sc[str, Text().re_search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")[1]]
    failed_value: Sc[bool, Text(default=False).re_search(r"(ora)")[1]]
    digits: Sc[List[int], Text().re_findall(r"(\d+)")]
    digits_float: Sc[
        List[float], Text().re_findall(r"(\d+)").fn(lambda lst: [f"{s}.5" for s in lst])
    ]
    words_lower: Sc[List[str], Text().re_findall("([a-z]+)")]
    words_upper: Sc[List[str], Text().re_findall(r"([A-Z]+)")]

    @sc_param
    def sum(self):
        return sum(self.digits)

    @sc_param
    def all_words(self):
        return self.words_lower + self.words_upper


def test_text_fields():
    schema = RawSchema(RAW_TEXT)
    assert schema.dict() == {
        "sum": 391,
        "all_words": [
            "banana",
            "potato",
            "foo",
            "bar",
            "lorem",
            "upsum",
            "dolor",
            "BANANA",
            "POTATO",
        ],
        "ipv4": "192.168.0.1",
        "failed_value": False,
        "digits": [10, 20, 192, 168, 0, 1],
        "digits_float": [10.5, 20.5, 192.5, 168.5, 0.5, 1.5],
        "words_lower": ["banana", "potato", "foo", "bar", "lorem", "upsum", "dolor"],
        "words_upper": ["BANANA", "POTATO"],
    }
