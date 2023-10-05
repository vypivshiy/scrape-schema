from typing import Any

from scrape_schema import BaseSchema
from scrape_schema.field import RawDLField


class DatalinesSchema1(BaseSchema):
    data: dict[str, Any] = RawDLField().css_dl()


class DatalinesSchema2(BaseSchema):
    # customize css queries. exclude .col-12 elements
    data: dict[str, Any] = RawDLField().css_dl(
        dl_css="div.info > dl.row", dt_css="dt.col-6", dd_css="dd.col-6"
    )
    # custom enchants
    data2: dict[str, str] = RawDLField().css_dl(
        dl_css="div.info > dl.row",
        dt_css="dt.col-6",
        dd_css="dd.col-6",
        strip=True,
        str_join=", ",
    )


if __name__ == "__main__":
    HTML_1 = """
    <dl>
    <dt>PHP</dt>
    <dd>A server side scripting language.</dd>
    <dt>JavaScript</dt>
    <dd>A client side scripting language.</dd>
    </dl>
    """

    HTML_2 = """
    <div class="info"><dl class="row">
        <dt class="col-12">keys</dt>
        <dd class="col-12">values</dd>
        <dd class="col-12"><hr></dd>
        <dt class="col-6">key1</dt>
        <dd class="col-6">value1 value2 FROM KEY1</dd>
        <dt class="col-6">items</dt>
        <dd class="col-6">
            <span>item 1</span>
            <span>item 2</span>
            <span>item 3</span>
            <span>item 4</span>
        </dd>
        <dt class="col-6">key2</dt>
        <dd class="col-6"></dd>
        <dt class="col-6">key3</dt>
        <dd class="col-6">value3</dd>
    """
    print(DatalinesSchema1(HTML_1).dict())
    # {'data': {'PHP': ['A server side scripting language.'], 'JavaScript': ['A client side scripting language.']}}

    print(DatalinesSchema2(HTML_2).dict())
    # {'data': {'key1': ['value1 value2 FROM KEY1'],
    # 'items': ['\n            ', 'item 1', ' \n            ', 'item 2',
    # ' \n            ', 'item 3', ' \n            ', 'item 4', ' \n        '],
    # 'key2': [],
    # 'key3': ['value3']},
    #
    # 'data2': {'key1': 'value1 value2 FROM KEY1',
    # 'items': ', item 1, , item 2, , item 3, , item 4,
    # ', 'key2': '',
    # 'key3': 'value3'}}
