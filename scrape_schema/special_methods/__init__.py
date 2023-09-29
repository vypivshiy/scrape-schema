from scrape_schema.special_methods.base import (
    MarkupMethod,
    SpecialMethods,
    SpecialMethodsHandler,
)
from scrape_schema.special_methods.methods import *

DEFAULT_SPEC_METHOD_HANDLER = SpecialMethodsHandler()
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.FN, FnMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.CONCAT_R, ConcatRightMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.CONCAT_L, ConcatLeftMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.REPLACE, ReplaceMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.REGEX_SEARCH, ReSearchMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.REGEX_FINDALL, ReFindallMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(
    SpecialMethods.CHOMP_JS_PARSE, ChompJsParseMethod()
)
DEFAULT_SPEC_METHOD_HANDLER.add_method(
    SpecialMethods.CHOMP_JS_PARSE_ALL, ChompJsParseAllMethod()
)
# 0.6.0
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.CAPITALIZE, CapitalizeMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.COUNT, CountMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.LOWER, LowerMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.UPPER, UpperMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.REPLACE, ReplaceMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.L_STRIP, LStripMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.R_STRIP, RStripMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.STRIP, StripMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.STR_JOIN, JoinMethod())
DEFAULT_SPEC_METHOD_HANDLER.add_method(SpecialMethods.SPLIT, SplitMethod())
