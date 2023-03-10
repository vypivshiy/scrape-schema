import pprint
from scrape_schema import BaseSchema
from scrape_schema.fields.regex import ReMatch, ReMatchList


TEXT = "1 2 3 4 5 6"


class Schema(BaseSchema):
    first_digit = ReMatch(r'(\d)')  # return string
    first_digit_int: int = ReMatch(r'(\d)')  # return int
    first_digit_float: float = ReMatch(r'(\d)')  # return float
    digit_float_x35: first_digit = ReMatch(r'(\d)', callback=float, factory=lambda s: s+3.5)
    has_word: bool = ReMatch(r"([a-z]+)")  # False
    has_digit: bool = ReMatch(r"(\d)")  # True

    digits: list[int] = ReMatchList(r'(\d)')
    # get all digit, convert to int and get max value
    max_digit: int = ReMatchList(r'(\d)', callback=int, factory=max)
    # get all digit, convert to int and get min value
    min_digit: int = ReMatchList(r'(\d)', callback=int, factory=min)
    # get digits, then less or equal 3
    less_3: list[int] = ReMatchList(r'(\d)', filter_=lambda s: int(s) <= 3)
    # get digits, then less or equal 3 and sum
    sum_less_3: int = ReMatchList(r'(\d)', filter_=lambda s: int(s) <= 3, callback=int, factory=sum)
    # get digits, then bigger than 3, convert to int
    bigger_3: list[int] = ReMatchList(r'(\d)', filter_=lambda s: int(s) > 3, callback=int)
    # get digits, then bigger than 3 and sum
    sum_bigger_3: int = ReMatchList(r'(\d)', filter_=lambda s: int(s) > 3, callback=int, factory=sum)
    # get all digit and sum
    sum_digits: int = ReMatchList(r'(\d)', callback=int, factory=sum)


if __name__ == '__main__':
    schema = Schema(TEXT)
    pprint.pprint(schema.dict(), indent=4, width=48)
    # {   'bigger_3': [4, 5, 6],
    #     'digit_float_x35': 4.5,
    #     'digits': [1, 2, 3, 4, 5, 6],
    #     'first_digit': '1',
    #     'first_digit_float': 1.0,
    #     'first_digit_int': 1,
    #     'has_digit': True,
    #     'has_word': False,
    #     'less_3': [1, 2, 3],
    #     'max_digit': 6,
    #     'min_digit': 1,
    #     'sum_bigger_3': 15,
    #     'sum_digits': 21,
    #     'sum_less_3': 6}
