import pprint
from scrape_schema import BaseSchema, Parsel, Nested, Sc, sc_param


class SubSchema(BaseSchema):
    item: Sc[str, Parsel().xpath("//p/text()").get()]
    price: Sc[int, Parsel().xpath("//div[@class='price']/text()").get()]
    _available: Sc[str, Parsel().xpath("//div[contains(@class, 'available')]").attrib.get(key='class')]

    @sc_param
    def available(self) -> bool:
        return "yes" in self._available


class Schema(BaseSchema):
    first_item: Sc[SubSchema, Nested(Parsel().xpath("//ul").xpath("./li").getall()[0])]
    last_item: Sc[SubSchema, Nested(Parsel().xpath("//ul").xpath("./li").getall()[-1])]
    items: Sc[list[SubSchema], Nested(Parsel().xpath("//body/ul").xpath("./li").getall())]


text = """
<html>
    <body>
        <ul>
            <li>
                <p>audi</p>
                <div class="price">10000</div>
                <div class="available yes"></div>
            </li>
            <li>
                <p>ferrari</p>
                <div class="price">99999999</div>
                <div class="available no"></div>
            </li>
            <li>
                <p>bentley</p>
                <div class="price">50000</div>
                <div class="available yes"></div>
            </li>
            <li>
                <p>ford</p>
                <div class="price">20000</div>
                <div class="available yes"></div>
            </li>
            <li>
                <p>suzuki</p>
                <div class="price">25000</div>
                <div class="available yes"></div>
            </li>
        </ul>
    </body>
</html>
"""

pprint.pprint(Schema(text).dict(), compact=True)
# {'first_item': {'available': True, 'item': 'audi', 'price': 10000},
#  'items': [{'available': True, 'item': 'audi', 'price': 10000},
#            {'available': False, 'item': 'ferrari', 'price': 99999999},
#            {'available': True, 'item': 'bentley', 'price': 50000},
#            {'available': True, 'item': 'ford', 'price': 20000},
#            {'available': True, 'item': 'suzuki', 'price': 25000}],
#  'last_item': {'available': True, 'item': 'suzuki', 'price': 25000}}
