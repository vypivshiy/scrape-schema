from scrape_schema import Parsel


def test_stack():
    p = Parsel()
    assert len(p._stack_methods) == 0
    p.xpath("//a").css("c > b")
    assert len(p._stack_methods) == 2


def test_xpath_raw_tag():
    html = "<div> test case </div>"
    assert Parsel().xpath("//div").get().sc_parse(html) == "<div> test case </div>"


def test_xpath_text():
    html = "<div> test case </div>"
    assert Parsel().xpath("//div/text()").get().sc_parse(html) == " test case "
