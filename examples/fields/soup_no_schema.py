from bs4 import BeautifulSoup
from scrape_schema.callbacks.soup import get_attr, get_text
from scrape_schema.fields.soup import SoupFind, SoupFindList, SoupSelect, SoupSelectList

HTML = """
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
"""
Image = SoupFind("<img>", callback=get_attr("src"))
AllPText = SoupFindList("<p>", filter_=lambda t: not(get_text()(t).isdigit()))
SubList = SoupFindList('<a class="sub-list">')
SelectSubDictA = SoupSelectList("div.sub-dict > a")
SelectSubString = SoupSelect("div.sub-dict > p.sub-string")

soup = BeautifulSoup(HTML, "html.parser")

img: str = Image.extract(soup)
p_lst: list[str] = AllPText.extract(soup)
sub_list: list[int] = SubList.extract(soup, type_=list[int])
sub_list_2: list[float] = SelectSubDictA.extract(soup, type_=list[float])
sub_str: str = SelectSubString.extract(soup)

print(img, p_lst, sub_list, sub_list_2, sub_str, sep="\n__\n")
# /foo.png
# __
# ['test-string', 'test-1', 'spam-1']
# __
# [10, 20, 30]
# __
# [10.0, 20.0, 30.0]
# __
# spam-1
