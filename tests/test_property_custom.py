from scrape_schema import ScField, BaseSchema
from scrape_schema.fields.regex import ReMatch


class PropSchema(BaseSchema):
    _value_1: ScField[int, ReMatch(r"(\d+)+")]
    _value_2: ScField[str, ReMatch(r"(\d+)+")]
    _word: ScField[str, ReMatch(r"([a-z]+)")]
    public_value: ScField[str, ReMatch(r"(spam)+")]

    @property
    def float_value(self):
        return float(self._value_1)

    @property
    def value_x2(self):
        return self._value_1**2

    @property
    def upper_word(self):
        return self._word.upper()

    @property
    def sentence(self):
        return f"{self._word} {self.public_value}"


PROP_SC = PropSchema("911 dolor spam")


def test_prop_sc_dict():
    assert PROP_SC.dict() == {'float_value': 911.0,
                              'value_x2': 829921,
                              'upper_word': 'DOLOR',
                              'sentence': 'dolor spam',
                              'public_value': 'spam'}


def test_prop_sc_raw_dict():
    assert PROP_SC.raw_dict() == {'_value_1': 911,
                                  '_value_2': '911',
                                  '_word': 'dolor',
                                  'public_value': 'spam'}
