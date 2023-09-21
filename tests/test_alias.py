from scrape_schema import BaseSchema, Sc, Text


class AliasTestSchema(BaseSchema):
    snake_dict: Sc[str, Text(alias="camelDict")]


def test_alias():
    sc = AliasTestSchema("test")
    assert sc.dict() == {"camelDict": "test"}
    assert sc.dict().get("snake_dict", None) is None
    assert sc.dict(by_alias=False).get("snake_dict") == "test"
