from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch

MOCK_TEXT = "lorem 100; dolor 200"


class ConstructorSchema(BaseSchema):
    word: ScField[str, ReMatch(r"([a-zA-Z]+)")]
    digit: ScField[int, ReMatch(r"(\d+)")]


def test_default():
    assert ConstructorSchema(MOCK_TEXT).dict() == {"word": "lorem", "digit": 100}


def test_from_markup():
    assert (
        ConstructorSchema(MOCK_TEXT).dict()
        == ConstructorSchema.from_markup(MOCK_TEXT).dict()
    )


def test_from_list():
    lst = ConstructorSchema.from_list(MOCK_TEXT.split("; "))
    assert [d.dict() for d in lst] == [
        {"word": "lorem", "digit": 100},
        {"word": "dolor", "digit": 200},
    ]


def test_from_crop_rule():
    assert ConstructorSchema.from_crop_rule(
        MOCK_TEXT, crop_rule=lambda s: s.split("; ")[-1]
    ).dict() == {"word": "dolor", "digit": 200}


def test_from_crop_rule_list():
    lst = ConstructorSchema.from_crop_rule_list(
        MOCK_TEXT, crop_rule=lambda s: s.split("; ")
    )
    assert [d.dict() for d in lst] == [
        {"word": "lorem", "digit": 100},
        {"word": "dolor", "digit": 200},
    ]
