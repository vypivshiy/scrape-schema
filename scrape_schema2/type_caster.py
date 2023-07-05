import sys
from typing import Any, Type, Union

from scrape_schema2.base import get_args, get_origin

from scrape_schema._logger import logger

NoneType = type(None)


class TypeCaster:
    def _typing_to_builtin(self, type_hint: Type) -> Type:
        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if origin is not None and args:
            # Recursively convert the nested generic types
            converted_args = tuple(self._typing_to_builtin(arg) for arg in args)
            return origin[converted_args]
        else:
            return type_hint

    def cast(self, type_hint: Type, value: Any) -> Any:
        if sys.version_info >= (3, 9):
            type_hint = self._typing_to_builtin(type_hint)

        origin = get_origin(type_hint)
        args = get_args(type_hint)
        logger.info(
            "`{}` Cast type start. `value={}`, type_annotation={}, `origin={}`, `args={}`",
            self.__class__.__name__,
            value,
            type_hint,
            origin,
            args,
        )
        # None
        if value is None and type_hint is not bool:
            return value

        if origin is not None and args:
            # list
            if origin is list:
                logger.debug(
                    "List cast {} -> arg={}, value={}",
                    self.__class__.__name__,
                    args[0],
                    value,
                )
                return [self.cast(type_hint=args[0], value=v) for v in value]
            # dict
            elif origin is dict:
                key_type, value_type = args
                logger.debug(
                    "Dict cast {} -> key={}, value={}  `{}`",
                    self.__class__.__name__,
                    key_type.__name__,
                    value_type.__name__,
                    value,
                )
                return {
                    self.cast(type_hint=key_type, value=k): self.cast(
                        type_hint=value_type, value=v
                    )
                    for k, v in value.items()
                }
            # Optional
            elif origin is Union:
                if value is None and NoneType in args:
                    logger.debug(
                        "Optional cast {} -> {}", self.__class__.__name__, value
                    )
                    return None
                # in python3.8 raise TypeError: issubclass() arg 1 must be a class
                # example _cast_type(Optional[List[int]], [])
                non_none_args = [arg for arg in args if arg is not NoneType]
                if len(non_none_args) == 1:
                    return self.cast(type_hint=non_none_args[0], value=value)
        # bool cast
        elif type_hint is bool:
            logger.debug("Cast {} `{}()` -> bool", self.__class__.__name__, value)
            return bool(value)
        else:
            # direct cast
            logger.debug(
                "Cast `{}` := `{}({})`", self.__class__.__name__, type_hint, value
            )
            return type_hint(value)
