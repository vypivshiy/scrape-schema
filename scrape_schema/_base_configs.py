from typing import Any, ClassVar, Dict, Optional, Type

from scrape_schema._field_hook import FieldHooks


class BaseFieldConfig:
    """BaseField configuration class:

    * parser: Optional[Type[Any]] - parser backend object. If value None - work with python str
    """

    parser: ClassVar[Optional[Type[Any]]] = None
    hooks: ClassVar["FieldHooks"] = FieldHooks()


class BaseSchemaConfig:
    """Schema configuration for BaseSchema

    parsers_config: dict[Type[Any], dict[str, Any]] parser classes for usage backend

    type_cast: bool usage type casting feature. default True

    fails_attempt: int - fields parse success counter checker. default -1 disable

    fails_attempt < 0   - disable checker (default)

    fails_attempt == 0  - if _first_ field return `default` value - throw `ParseFailAttemptsError`

    fails_attempt = n, fails_attempt > 0 - print *n* warnings messages if field return `default` value.
    if `n` msgs - throw `ParseFailAttemptsError`
    """

    parsers_config: ClassVar[Dict[Type[Any], Dict[str, Any]]] = {}
    type_cast: ClassVar[bool] = True
    fails_attempt: ClassVar[int] = -1
    hooks_priority: ClassVar[bool] = True
