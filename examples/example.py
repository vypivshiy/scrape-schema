import pprint
import re

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch, ReMatchList

TEXT = """
banana potato BANANA POTATO
-foo:10
-bar:20
lorem upsum dolor
192.168.0.1
"""


class Schema(BaseSchema):
    ipv4: ScField[str, ReMatch(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")]
    max_digit: ScField[int, ReMatchList(r"(\d+)", callback=int, factory=max)]
    failed_value: ScField[bool, ReMatchList(r"(ora)", default=False)]
    digits: ScField[list[int], ReMatchList(r"(\d+)")]
    digits_float: ScField[
        list[float], ReMatchList(r"(\d+)", callback=lambda s: f"{s}.5")
    ]
    words_lower: ScField[list[str], ReMatchList(r"([a-z]+)")]
    words_upper: ScField[list[str], ReMatchList(r"([A-Z]+)")]


def parse_text(text: str):
    """alternative lines of code without usage `BaseSchema` and `fields.regex`"""
    if match := re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", text):
        ipv4 = match[1]
    else:
        ipv4 = None

    if matches := re.findall(r"(\d+)", text):
        max_digit = max(int(i) for i in matches)
    else:
        max_digit = None

    failed_value = bool(re.search(r"(ora)", text))

    if matches := re.findall(r"(\d+)", text):
        digits = [int(i) for i in matches]
        digits_float = [float(f"{i}.5") for i in matches]
    else:
        digits = None
        digits_float = None

    words_lower = matches if (matches := re.findall(r"([a-z]+)", text)) else None
    words_upper = matches if (matches := re.findall(r"([A-Z]+)", text)) else None

    return dict(
        ipv4=ipv4,
        max_digit=max_digit,
        failed_value=failed_value,
        digits=digits,
        digits_float=digits_float,
        words_lower=words_lower,
        words_upper=words_upper,
    )


if __name__ == "__main__":
    schema = Schema(TEXT)
    pprint.pprint(schema.dict(), width=48, compact=True)
    # {'digits': [10, 20, 192, 168, 0, 1],
    #  'digits_float': [10.5, 20.5, 192.5, 168.5, 0.5,
    #                   1.5],
    #  'failed_value': False,
    #  'ip_v4': '192.168.0.1',
    #  'max_digit': 192,
    #  'words_lower': ['banana', 'potato', 'foo',
    #                  'bar', 'lorem', 'upsum',
    #                  'dolor'],
    #  'words_upper': ['BANANA', 'POTATO']}
    print("___")
    pprint.pprint(parse_text(TEXT), width=48, compact=True)
