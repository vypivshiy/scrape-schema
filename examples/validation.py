from scrape_schema import BaseSchema, Parsel
from scrape_schema.validator import markup_pre_validator


class Schema(BaseSchema):
    text: str = Parsel().css("h1::text").get()

    @markup_pre_validator()
    def validate(self) -> bool:
        # manual pre-validate rule
        return self.__selector__.xpath("//h1/text()").get() == "Hello, Parsel!"


Schema("<h1>Hello, Parsel!</h1>")  # OK
Schema("<h1>spam egg</h1>")  # raise SchemaPreValidationError
