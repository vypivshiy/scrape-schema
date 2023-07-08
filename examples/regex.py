import pprint
from typing import List  # if you usage python3.8. If python3.9 - use build-in list

from scrape_schema import BaseSchema, Parsel, Sc, sc_param

# Note: `Sc` is shortcut typing.Annotated

TEXT = """
banana potato BANANA POTATO
-foo:10
-bar:20
lorem upsum dolor
192.168.0.1
"""


class MySchema(BaseSchema):
    ipv4: Sc[
        str, Parsel(raw=True).re_search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")[1]
    ]
    failed_value: Sc[bool, Parsel(default=False, raw=True).re_search(r"(ora)")[1]]
    digits: Sc[List[int], Parsel(raw=True).re_findall(r"(\d+)")]
    digits_float: Sc[
        List[float],
        Parsel(raw=True).re_findall(r"(\d+)").fn(lambda lst: [f"{s}.5" for s in lst]),
    ]
    words_lower: Sc[List[str], Parsel(raw=True).re_findall("([a-z]+)")]
    words_upper: Sc[List[str], Parsel(raw=True).re_findall(r"([A-Z]+)")]

    @sc_param
    def sum(self):
        return sum(self.digits)

    @sc_param
    def all_words(self):
        return self.words_lower + self.words_upper


pprint.pprint(MySchema(TEXT).dict(), compact=True)
# {'all_words': ['banana', 'potato', 'foo', 'bar', 'lorem', 'upsum', 'dolor',
#                'BANANA', 'POTATO'],
#  'digits': [10, 20, 192, 168, 0, 1],
#  'digits_float': [10.5, 20.5, 192.5, 168.5, 0.5, 1.5],
#  'failed_value': False,
#  'ipv4': '192.168.0.1',
#  'sum': 391,
#  'words_lower': ['banana', 'potato', 'foo', 'bar', 'lorem', 'upsum', 'dolor'],
#  'words_upper': ['BANANA', 'POTATO']}
