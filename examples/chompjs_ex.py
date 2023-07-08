from typing import Any, TypedDict

from scrape_schema import BaseSchema, Parsel, Sc, sc_param

text = """
 <script>
            var sampleParams = Sandbox.init(
            {"key": "spam", "values": [1,2,3,4,5], "layer1": {"layer2": {"layer3": [null, null, true, false]}}}
            );
</script>
"""


ResultDict = TypedDict(
    "ResultDict", {"key": str, "values": list[int], "layer1": dict[str, Any]}
)


class ChompJSAddon(BaseSchema):
    # auto_type will work unpredictably with chompjs output, disable is recommended or type this field by TypedDict
    # or set dict[str, Any]
    result: Sc[
        ResultDict,
        Parsel(auto_type=False).xpath("//script/text()").get().chomp_js_parse(),
    ]

    @sc_param
    def typed_result(self) -> ResultDict:
        return self.result

    @sc_param
    def key(self) -> str:
        return self.result["key"]

    @sc_param
    def values(self) -> list[int]:
        return self.result["values"]


print(ChompJSAddon(text).dict())

# {'key': 'spam', 'values': [1, 2, 3, 4, 5], 'layer1': {'layer2': {'layer3': [None, None, True, False]}}}
