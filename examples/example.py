from typing import Optional

from parsel import SelectorList

from scrape_schema import BaseSchema, Nested, Parsel, Sc, sc_param


class SubSchema(BaseSchema):
    body_list: Sc[list[int], Parsel().xpath("//a[@class='list']/text()").getall()]
    p: Sc[str, Parsel().xpath("//p/text()").get()]


class Sample(BaseSchema):
    title: Sc[str, Parsel().xpath("//head/title/text()").get()]
    charset: Sc[str, Parsel().xpath("//head/meta/@charset").get()]
    # if not set default value - throw exception and close program
    failed: Sc[Optional[str], Parsel(default=None).xpath("unknownlol > p::text").get()]

    _images: Sc[SelectorList, Parsel(auto_type=False).xpath("//img")]
    subs: Sc[list[SubSchema], Nested(Parsel().xpath("//div[@class='dict']").getall())]

    @sc_param
    def images(self):
        return [f"https://example.com{img.xpath('@src').get()}" for img in self._images]

    @property
    def foo(self):
        return "foo"


if __name__ == '__main__':
    HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TEST PAGE</title>
</head>
<body>
    <img src="/foo.png">foo</img>
    <p class="body-string">test-string</p>
    <p class="body-int">555</p>
    <a class="body-list">666</a>
    <a class="body-list">777</a>
    <a class="body-list">888</a>
    <div class="dict">
      <p class="string">test-1</p>
      <a class="list">1</a>
      <a class="list">2</a>
      <a class="list">3</a>
      <div class="sub-dict">
        <p class="sub-string">spam-1</p>
        <a class="sub-list">10</a>
        <a class="sub-list">20</a>
        <a class="sub-list">30</a>
      </div>
    </div>
    <div class="dict">
      <p class="string">test-2</p>
      <a class="list">4</a>
      <a class="list">5</a>
      <a class="list">6</a>
      <div class="sub-dict">
        <p class="sub-string">spam-2</p>
        <a class="sub-list">40</a>
        <a class="sub-list">50</a>
        <a class="sub-list">60</a>
      </div>
    </div>
    <img src="/baz.png">baz</img>
    <div class="dict">
      <p class="string">test-3</p>
      <a class="list">7</a>
      <a class="list">8</a>
      <a class="list">9</a>
      <div class="sub-dict">
        <p class="sub-string">spam-3</p>
        <a class="sub-list">70</a>
        <a class="sub-list">80</a>
        <a class="sub-list">90</a>
      </div>
    </div>
    <img src="/bar.png">bar</img>
</body>
</html>
"""
    print(Sample(HTML).dict())
