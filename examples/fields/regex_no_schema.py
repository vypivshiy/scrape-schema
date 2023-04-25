from scrape_schema.fields.regex import ReMatch, ReMatchList, ReMatchDict, ReMatchListDict


ReDigit = ReMatch(r"(\d+)")
ReWord = ReMatch(r"([a-zA-Z]+)")

ReDigits = ReMatchList(r"(\d+)")
ReWords = ReMatchList(r"([a-zA-Z]+)")

ReSentence = ReMatchList(r"([a-zA-Z]+)", factory=lambda lst: " ".join(lst))
ReSum = ReMatchList(r"(\d+)", callback=int, factory=sum)

ReDigitDict = ReMatchDict(r"(?P<digit>\d+)")
ReDigitListDict = ReMatchListDict(r"(?P<digit>\d+)")

TEXT = "lorem 10 upsum 100 900 dolor"

digit: int = ReDigit.extract(TEXT, type_=int)
digits: list[int] = ReDigits.extract(TEXT, type_=list[int])
digits_sum: int = ReSum.extract(TEXT)
print(digit, digits, digits_sum, sep="\n--\n")

word: str = ReWord.extract(TEXT)
words: list[str] = ReWords.extract(TEXT)
sentence: str = ReSentence.extract(TEXT)
print(word, words, sentence, sep="\n--\n")

digit_dict: dict[str, int] = ReDigitDict.extract(TEXT, type_=dict[str, int])
digit_list_dict: list[dict[str, str]] = ReDigitListDict.extract(TEXT)
print(digit_dict, digit_list_dict, sep="\n--\n")
# 10
# --
# [10, 100, 900]
# --
# 1010
# lorem
# --
# ['lorem', 'upsum', 'dolor']
# --
# lorem upsum dolor
# {'digit': 10}
# --
# [{'digit': '10'}, {'digit': '100'}, {'digit': '900'}]
