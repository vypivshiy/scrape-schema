from scrape_schema import BaseSchema, Parsel
from scrape_schema.exceptions import SchemaPreValidationError
from scrape_schema.validator import markup_pre_validator


class ValidateSchemaXpath(BaseSchema):
    title: str = Parsel().xpath("//title/text()").get()

    @markup_pre_validator(xpath="//title")
    def validate(self):
        return True


class ValidateSchemaCss(BaseSchema):
    title: str = Parsel().xpath("//title/text()").get()

    @markup_pre_validator(css="title")
    def validate(self):
        return True


class ValidateSchemaRe(BaseSchema):
    title: str = Parsel().xpath("//title/text()").get()

    @markup_pre_validator(pattern=r"<title>.*?</title>")
    def validate(self):
        return True


if __name__ == "__main__":
    text = "<title>hello, scrape-schema!</title>"
    text_2 = "<h1>hello, scrape-schema!</h1>"
    # passed validation
    print(ValidateSchemaXpath(text).dict())
    print(ValidateSchemaCss(text).dict())
    print(ValidateSchemaRe(text).dict())
    # failed
    try:
        ValidateSchemaXpath(text_2)
    except SchemaPreValidationError:
        print("failed")
    try:
        ValidateSchemaCss(text_2)
    except SchemaPreValidationError:
        print("failed")
    try:
        ValidateSchemaRe(text_2)
    except SchemaPreValidationError:
        print("failed")
