from typing import Any

from scrape_schema.base import MARKUP_TYPE, BaseField


class MockField(BaseField):
    """mock field for testing"""

    def __init__(self, value: Any, callback=None, filter_=None, factory=None, **kwargs):
        super().__init__(callback=callback, filter_=filter_, factory=factory, **kwargs)
        self.value = value

    def _parse(self, markup: MARKUP_TYPE) -> Any:
        return self.value
