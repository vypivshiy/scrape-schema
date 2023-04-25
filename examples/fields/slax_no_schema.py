from selectolax.parser import HTMLParser

from scrape_schema.fields.slax import SlaxSelect, SlaxSelectList

HTML = """

<div class="dict">
  <p class="string">test-1</p>
  <a class="int">1</a>
</div>
<div class="dict">
  <p class="string">test-2</p>
  <a class="int">2</a>
</div>
<div class="dict2">
  <p class="string">test-3</p>
  <a class="list">3</a>
  <a class="list">8</a>
  <a class="list">9</a>
</div>
"""

Select1 = SlaxSelect("div.dict > a.int")
Select2 = SlaxSelect("div.dict > p.string")
SelectList1 = SlaxSelectList("div.dict > a.int")
SelectListSum = SlaxSelectList("div.dict > a.int", factory=lambda lst: sum(int(i) for i in lst))
SelectList2 = SlaxSelectList("div.dict > p.string")

parser = HTMLParser(HTML)

digit: int = Select1.extract(parser, type_=int)
word: str = Select2.extract(parser)
digits_sum: int = SelectListSum.extract(parser)
digits: list[int] = SelectList1.extract(parser, type_=list[int])
words: list[str] = SelectList2.extract(parser)

print(digit, word, digits_sum, digits, words, sep="\n--\n")
# 1
# --
# test-1
# --
# 3
# --
# [1, 2]
# --
# ['test-1', 'test-2']
