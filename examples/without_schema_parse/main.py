from bs4 import BeautifulSoup

from scrape_schema.callbacks.soup import get_attr, get_text
from scrape_schema.fields.regex import ReMatch, ReMatchList
from scrape_schema.fields.soup import SoupFind, SoupFindList

TEXT = """
spam spammer egg
digits 1 2 3 4 5
"""

HTML = """
<p>spam</p>
<p>egg</p>
<div>10</div>
<div>90</div>
<a href="example.com">click me</a>
"""


def parse_regex(text):
    return {
        "spam": ReMatch(r"(sp\w+)").extract(text),
        "words": ReMatchList(r"([a-zA-Z]+)").extract(text),
        "sentence": ReMatchList(
            r"([a-zA-Z]+)", factory=lambda lst: " ".join(lst)
        ).extract(text),
        "digits": ReMatchList(r"(\d+)").extract(text, type_=list[int]),
        "sum": ReMatchList(r"(\d+)", callback=int, factory=sum).extract(text),
        "max": ReMatchList(r"(\d+)", callback=int, factory=max).extract(text),
        "min": ReMatchList(r"(\d+)", callback=int, factory=min).extract(text),
    }


def parse_soup(html):
    # soup fields accept `BeautifulSoup` object. if pass string - raise TypeError
    soup = BeautifulSoup(html, "html.parser")
    return {
        "p": SoupFindList("<p>").extract(soup),
        "a": SoupFind("<a>", callback=get_attr("href")).extract(soup),
        "div": SoupFindList("<div>").extract(soup, type_=list[int]),
        "sum": SoupFindList(
            "<div>", callback=lambda tag: int(get_text()(tag)), factory=sum
        ).extract(soup, type_=list[int]),
    }


def has_spam(text):
    return ReMatch(r"(spam)").extract(text, type_=bool)


if __name__ == "__main__":
    re_dict = parse_regex(TEXT)
    print(re_dict)
    # {'spam': 'spam', 'words': ['spam', 'spammer', 'egg', 'digits'],
    # 'sentence': 'spam spammer egg digits', 'digits': [1, 2, 3, 4, 5], 'sum': 15, 'max': 5, 'min': 1}

    print(has_spam("spammer"))  # True
    print(has_spam("eggs"))  # False

    re_soup = parse_soup(HTML)
    print(re_soup)
    # {'p': ['spam', 'egg'], 'a': 'example.com', 'div': [10, 90], 'sum': 100}
