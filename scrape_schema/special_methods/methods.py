import warnings
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
    # 0.6.0
    "StripMethod",
    "LStripMethod",
    "RStripMethod",
    "LowerMethod",
    "UpperMethod",
    "CapitalizeMethod",
    "CountMethod",
    "JoinMethod",
    "SplitMethod",
]


class FnMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        if not (func := method.kwargs.get("function")):
            func = method.args[0]
            return func(markup)
        return func(markup)


class SplitMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        if isinstance(markup, list):
            raise TypeError("markup chain value should be str, not list")
        _sep, _max_split = method.args[0], method.args[1]
        return markup.split(_sep, _max_split)


class StripMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        if isinstance(markup, list):
            return [m.strip(method.args[0]) for m in markup]
        return markup.strip(method.args[0])


class RStripMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        if isinstance(markup, list):
            return [m.rstrip(method.args[0]) for m in markup]
        return markup.rstrip(method.args[0])


class LStripMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        if isinstance(markup, list):
            return [m.lstrip(method.args[0]) for m in markup]
        return markup.lstrip(method.args[0])


class LowerMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        if isinstance(markup, list):
            return [m.lower() for m in markup]
        return markup.lower()


class UpperMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        if isinstance(markup, list):
            return [m.upper() for m in markup]
        return markup.upper()


class CapitalizeMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        if isinstance(markup, list):
            return [m.capitalize() for m in markup]
        return markup.capitalize()


class CountMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        if isinstance(markup, list):
            return len(markup)
        return 1


class JoinMethod(BaseSpecialMethodStrategy):
    def __call__(self, markup: Any, method: MarkupMethod, **kwargs):
        if isinstance(markup, list):
            return method.args[0].join(markup)
        warnings.warn(
            f"Last chain method value={markup}, ignore join method",
            stacklevel=3,
            category=RuntimeWarning,
        )
        return markup


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
