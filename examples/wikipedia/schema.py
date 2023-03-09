import requests
import json
from selectolax.parser import HTMLParser

from scrape_schema import BaseSchema
from scrape_schema.fields.slax import SLaxSelect, SLaxSelectList
from scrape_schema.tools.slax import get_tag, get_text


class MainEnPage(BaseSchema):
    # Note: this parser works only English version (en.wikipedia.org)!
    __MARKUP_PARSERS__ = {HTMLParser: {}}
    articles_count: int = SLaxSelect("#articlecount > a:nth-child(1)",
                                     callback=lambda el: el.text().replace(",", ""))
    language: str = SLaxSelect('#articlecount > a:nth-child(2)')
    featured_article: str = SLaxSelect('#mp-tfa > p')
    did_your_know: list[str] = SLaxSelectList('#mp-dyk > ul > li')
    in_the_news: list[str] = SLaxSelectList('#mp-itn > ul > li')
    on_this_day_date: str = SLaxSelect('#mp-otd > p')
    on_this_day: list[str] = SLaxSelectList('#mp-otd > ul > li')
    today_feature_picture: str = SLaxSelect('#mp-tfp > table > tbody > tr:nth-child(1) > td > a',
                                            callback=get_tag('href'))
    today_feature_picture_description: str = SLaxSelect(
        '#mp-tfp > table > tbody > tr:nth-child(2) > td > p:nth-child(1)')
    footer_info: str = SLaxSelect('#footer', callback=get_text(strip=True))


if __name__ == '__main__':
    resp = requests.get("https://en.wikipedia.org").text
    main_page_en = MainEnPage(resp)
    print(json.dumps(main_page_en.dict(), indent=4))
