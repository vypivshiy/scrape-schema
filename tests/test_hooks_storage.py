from typing import List

import pytest

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.mock import MockField
from scrape_schema.hooks import FieldHook, FieldHookList

HOOK_DEFAULT = FieldHook(default="error")
HOOK_FACTORY_LST = FieldHook(default="error", factory=list)
HOOK_CALLBACK_EVERY_1 = FieldHook(callback=lambda s: 1)
HOOK_GT_10 = FieldHookList(default=11, filter_=lambda val: int(val) > 10)


class SchemaHooks3(BaseSchema):
    words: ScField[List[str], MockField(["alorem", "dolor", "morgen", "aupsum"])]
    sentence: ScField[str, MockField(["dolor", "morgen"])]


@pytest.mark.parametrize(
    "field,result",
    [
        (MockField(1, **HOOK_DEFAULT), 1),
        (MockField(None, **HOOK_DEFAULT), "error"),
        (MockField(None, **HOOK_FACTORY_LST), ["e", "r", "r", "o", "r"]),
        (MockField([], **HOOK_FACTORY_LST), ["e", "r", "r", "o", "r"]),
        (MockField(None, **HOOK_CALLBACK_EVERY_1), 1),
        (MockField(9_999, **HOOK_CALLBACK_EVERY_1), 1),
        (MockField("lorem", **HOOK_CALLBACK_EVERY_1), 1),
        (MockField([1, 2, 3], **HOOK_CALLBACK_EVERY_1), [1, 1, 1]),
        (MockField([1, 2, 3], **HOOK_FACTORY_LST), [1, 2, 3]),
        (MockField([10, 0], **HOOK_GT_10), []),
        (MockField(None, **HOOK_GT_10), 11),
        (MockField([1, 10, 100, 1000], **HOOK_GT_10), [100, 1000]),
    ],
)
def test_hooks_typed_dict(field: MockField, result):
    assert field.extract("") == result
