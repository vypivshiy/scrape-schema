# Note: this parser works only English version (en.wikipedia.org)!

import json
from typing import Annotated

import requests
from selectolax.parser import HTMLParser

from scrape_schema import BaseSchema, BaseSchemaConfig
from scrape_schema.callbacks.slax import get_attr, get_text
from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList


class MainEnPage(BaseSchema):
    class Config(BaseSchemaConfig):
        parsers_config = {HTMLParser: {}}

    articles_count: Annotated[
        int,
        SlaxSelect(
            "#articlecount > a:nth-child(1)", callback=lambda el: el.text().replace(",", "")
        ),
    ]
    language: Annotated[str, SlaxSelect("#articlecount > a:nth-child(2)")]
    featured_article: Annotated[str, SlaxSelect("#mp-tfa > p")]
    did_your_know: Annotated[list[str], SlaxSelectList("#mp-dyk > ul > li")]
    in_the_news: Annotated[list[str], SlaxSelectList("#mp-itn > ul > li")]
    on_this_day_date: Annotated[str, SlaxSelect("#mp-otd > p")]
    on_this_day: Annotated[list[str], SlaxSelectList("#mp-otd > ul > li")]
    today_feature_picture: Annotated[
        str,
        SlaxSelect(
            "#mp-tfp > table > tbody > tr:nth-child(1) > td > a", callback=get_attr("href")
        ),
    ]
    today_feature_picture_description: Annotated[
        str, SlaxSelect("#mp-tfp > table > tbody > tr:nth-child(2) > td > p:nth-child(1)")
    ]
    footer_info: Annotated[str, SlaxSelect("#footer", callback=get_text(strip=True))]


if __name__ == "__main__":
    resp = requests.get("https://en.wikipedia.org").text
    main_page_en = MainEnPage(resp)
    print(json.dumps(main_page_en.dict(), indent=4))
