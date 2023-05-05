from typing import Union

import pytest

from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.mock import MockField
from scrape_schema.hooks import FieldHook, FieldHookList, HooksStorage

hooks = HooksStorage()

HOOK_DEFAULT = FieldHook(default="error")
HOOK_FACTORY_LST = FieldHook(default="error", factory=list)
HOOK_CALLBACK_EVERY_1 = FieldHook(callback=lambda s: 1)
HOOK_GT_10 = FieldHookList(default=11, filter_=lambda val: int(val) > 10)


@hooks.on_callback("SchemaHooks1.word_1", "SchemaHooks1.word_2", "SchemaHooks1.word_3")
def _word_callback(val: str):
    return f"hooked {val}"


class SchemaHooks1(BaseSchema):
    word_1: ScField[str, MockField("spam")]
    word_2: ScField[str, MockField("egg")]
    word_3: ScField[str, MockField("baz")]
    word_4: ScField[str, MockField("foo")]


class SchemaHooks2(BaseSchema):
    word_1: ScField[str, MockField("spam2")]
    word_2: ScField[str, MockField("egg2")]
    word_3: ScField[str, MockField("baz2")]
    word_4: ScField[str, MockField("foo2")]


def test_hooks_storage_1():
    assert SchemaHooks1("").dict() == {
        "word_1": "hooked spam",
        "word_2": "hooked egg",
        "word_3": "hooked baz",
        "word_4": "foo",
    }


def test_hooks_storage_2():
    assert SchemaHooks2("").dict() == {
        "word_1": "spam2",
        "word_2": "egg2",
        "word_3": "baz2",
        "word_4": "foo2",
    }


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
def test_structured_hooks(field: MockField, result):
    assert field.extract("") == result
