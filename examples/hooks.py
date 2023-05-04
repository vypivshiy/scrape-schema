from scrape_schema import BaseSchema, ScField
from scrape_schema.fields.regex import ReMatch
from scrape_schema.hooks import FieldHook, HooksStorage

hooks = HooksStorage()

hooks.add_hook(
    "default_100",
    FieldHook(
        default=100,
    ),
)


class Schema(BaseSchema):
    a_word: ScField[str, ReMatch(r"(a[a-zA-Z]+)")]
    b_word: ScField[str, ReMatch(r"(b[a-zA-Z]+)")]
    c_word: ScField[str, ReMatch(r"(c[a-zA-Z]+)")]
    digit: ScField[int, ReMatch(r"(\d+)")]
    digit_x10: ScField[int, ReMatch(r"(\d+)")]

    @staticmethod
    @hooks.on_callback("a_word", "b_word", "c_word")
    def _upper_callback(val: str) -> str:
        return val.upper()

    @staticmethod
    @hooks.on_callback("digit_x10")
    def _my_callback(val: str):
        return int(val) * 10


if __name__ == "__main__":
    print("schema:")
    print(Schema("lorem arrange byte hyper camelot number 100"))
    print()

    # hooks structs usage
    print("usage hooks")

    lower_case_hook = FieldHook(default="no lower case")
    int_hook_x2 = FieldHook(callback=lambda s: s * 2, factory=int)
    print(ReMatch(r"(\d+)", **int_hook_x2).extract("1050"))

    print(ReMatch(r"([a-z]+)", **lower_case_hook).extract("WHAT 1050"))
    print(ReMatch(r"([a-z]+)", **lower_case_hook).extract("what 1050"))

    # register hooks in storage
    print()
    print("register hooks in storage:")
    hooks.add_hook("l_case", lower_case_hook)
    hooks.add_hook("int_x2", lower_case_hook)

    # usage
    # if hook not founded - return empty dict
    print(ReMatch(r"([a-z]+)", **hooks.get_hook("l_caze")).extract("WHAT 1050"))

    print(ReMatch(r"(\d+)", **hooks.get_hook("int_x2")).extract("1050"))
    print(ReMatch(r"([a-z]+)", **hooks.get_hook("l_case")).extract("WHAT 1050"))
    print(ReMatch(r"([a-z]+)", **hooks.get_hook("l_case")).extract("what 1050"))
