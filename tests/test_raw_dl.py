from scrape_schema.field import DLRawField

# https://www.w3resource.com/html/definition-lists/HTML-definition-lists-dl-dt-dd-tags-elements.php
DL_HTML = """
<dl>
<dt>PHP</dt>
<dd> A server side scripting language. </dd>
<dt>JavaScript</dt>
<dd> A client side scripting language. </dd>
</dl>

"""


def test_dl_raw_parse():
    assert DLRawField().css_dl().sc_parse(DL_HTML) == {
        "PHP": [" A server side scripting language. "],
        "JavaScript": [" A client side scripting language. "],
    }


def test_dl_raw_arguments():
    assert DLRawField().css_dl(strip=True).sc_parse(DL_HTML) == {
        "PHP": ["A server side scripting language."],
        "JavaScript": ["A client side scripting language."],
    }

    assert DLRawField().css_dl(strip=True, str_join="").sc_parse(DL_HTML) == {
        "JavaScript": "A client side scripting language.",
        "PHP": "A server side scripting language.",
    }

    assert DLRawField().css_dl(
        strip=True, re_sub_pattern=r"A|a", re_sub_count=1
    ).sc_parse(DL_HTML) == {
        "JvaScript": [" client side scripting lnguge."],
        "PHP": [" server side scripting lnguge."],
    }
    assert DLRawField().css_dl(strip=True, re_sub_pattern=r"A|a").sc_parse(DL_HTML) == {
        "JvScript": [" client side scripting lnguge."],
        "PHP": [" server side scripting lnguge."],
    }
    print()
