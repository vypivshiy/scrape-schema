from typing import Any

import chompjs

from scrape_schema.special_methods.base import BaseSpecialMethodStrategy, MarkupMethod

__all__ = [
    "FnMethod",
    "ChompJsParseMethod",
    "ChompJsParseAllMethod",
    "ConcatLeftMethod",
    "ConcatRightMethod",
    "ReSearchMethod",
    "ReplaceMethod",
    "ReFindallMethod",
]


class FnMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        return method.kwargs["function"](markup)


class ConcatLeftMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        if isinstance(markup, list):
            return [method.args[0] + m for m in markup]
        return method.args[0] + markup


class ConcatRightMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        if isinstance(markup, list):
            return [m + method.args[0] for m in markup]
        return markup + method.args[0]


class ReplaceMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        __old, __new, __count = method.args[0], method.args[1], method.args[2]
        if isinstance(markup, list):
            return [m.replace(__old, __new, __count) for m in markup]
        return markup.replace(__old, __new, __count)


class ReSearchMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        pattern, groupdict, _flag = method.args
        if groupdict:
            if not pattern.groupindex:
                raise TypeError(f"Pattern `{pattern.pattern}` is not contains groups")
            return pattern.search(markup).groupdict()
        return pattern.search(markup)


class ReFindallMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        pattern, groupdict, _flag = method.args
        if groupdict:
            if not pattern.groupindex:
                raise TypeError(f"Pattern `{pattern.pattern}` is not contains groups")
            return [match.groupdict() for match in pattern.finditer(markup)]
        return pattern.findall(markup)


class ChompJsParseMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        return chompjs.parse_js_object(markup, *method.args)


class ChompJsParseAllMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        return chompjs.parse_js_objects(markup, *method.args)
