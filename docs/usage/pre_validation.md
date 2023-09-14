## Validation

You can check the markup argument before initialization. And if the check fails, it will throw
`SchemaPreValidationError` exception

```python
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
```

Also, decorator have shortcuts for quick pre validate document:

```python
from scrape_schema import BaseSchema, Parsel
from scrape_schema.validator import markup_pre_validator
from scrape_schema.exceptions import SchemaPreValidationError


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


if __name__ == '__main__':
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
# {'title': 'hello, scrape-schema!'}
# {'title': 'hello, scrape-schema!'}
# {'title': 'hello, scrape-schema!'}
# failed
# failed
# failed
```
