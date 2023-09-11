# mypy: disable-error-code="assignment"
import pytest
from tests.fixtures import HTML_FOR_SCHEMA

from scrape_schema import BaseSchema, Parsel, sc_param
from scrape_schema.exceptions import SchemaPreValidationError
from scrape_schema.validator import markup_pre_validator


class ValidatedSchema(BaseSchema):
    item: str = Parsel().xpath("//p/text()").get()

    @markup_pre_validator()
    def markup_has_not_title(self):
        return self.__selector__.xpath("//title/text()").get() is None


class ValidatedSchemaXpath(BaseSchema):
    @markup_pre_validator(xpath="//li/div[@class='price']")
    def validate(self):
        return True


class ValidatedSchemaCss(BaseSchema):
    @markup_pre_validator(css="li > div.price")
    def validate(self):
        return True


class ValidatedSchemaRe(BaseSchema):
    @markup_pre_validator(pattern=r"<p>audi</p>")
    def markup_not_title(self):
        return True


def test_failed_callable_validation():
    with pytest.raises(SchemaPreValidationError):
        ValidatedSchema("<title>hello</title>")


def test_callable_validation():
    ValidatedSchema(HTML_FOR_SCHEMA)


def test_xpath_validation():
    ValidatedSchemaXpath(HTML_FOR_SCHEMA)


def test_failed_xpath_validation():
    with pytest.raises(SchemaPreValidationError):
        ValidatedSchemaXpath("<title>hello</title>")


def test_css_validation():
    ValidatedSchemaCss(HTML_FOR_SCHEMA)


def test_failed_css_validation():
    with pytest.raises(SchemaPreValidationError):
        ValidatedSchemaCss("<title>hello</title>")


def test_re_validation():
    ValidatedSchemaRe(HTML_FOR_SCHEMA)


def test_failed_re_validation():
    with pytest.raises(SchemaPreValidationError):
        ValidatedSchemaRe("<title>hello</title>")
