import warnings
from typing import Any, Callable, Dict, KeysView, Optional, Tuple, TypedDict, Union

from scrape_schema._logger import logger

__all__ = ["FieldHook", "FieldHookList", "HooksStorage"]


class FieldHook(TypedDict, total=False):
    """Typed dict kwargs for fields classes"""

    default: Optional[Any]
    callback: Optional[Callable[..., Any]]
    factory: Optional[Callable[..., Any]]


class FieldHookList(FieldHook, total=False):
    """typed dict kwargs for iterable fields (+ filter_ argument)"""

    filter_: Optional[Callable[..., bool]]


class HooksStorage:
    """Singleton hook storage class"""

    _instance = None

    __callback_hooks__: Dict[str, Optional[Callable]] = {}
    __factory_hooks__: Dict[str, Optional[Callable]] = {}
    __filter_hooks__: Dict[str, Optional[Callable]] = {}
    __field_hooks__: Dict[str, Union[FieldHook, FieldHookList]] = {}

    def __new__(cls):
        warnings.warn(stacklevel=0, category=DeprecationWarning,
                      message="HooksStorage will be deleted in next updates, use @property decorators in BaseSchema "
                              "classes")
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def _register_hook(
        hooks_dict: Dict[str, Optional[Callable]],
        names: Tuple[str, ...],
        func: Optional[Callable] = None,
    ):
        for name in names:
            hooks_dict[name] = func
        return

    def on_filter(self, *attrs_names: str):
        """add filter param for attr names in schemas

        :param attrs_names: schema attribute names
        """

        def decorator(func):
            logger.debug("Register `on_filter` hook: %s %s", attrs_names, func)
            self._register_hook(self.__filter_hooks__, attrs_names, func)
            return func

        return decorator

    def on_factory(self, *attrs_names: str):
        """add factory param for attr names in schemas

        :param attrs_names: schema attribute names
        """

        def decorator(func):
            logger.debug("Register `on_factory` hook: %s %s", attrs_names, func)
            self._register_hook(self.__factory_hooks__, attrs_names, func)
            return func

        return decorator

    def on_callback(self, *attrs_names: str):
        """add callback param for attr names in schemas

        :param attrs_names: schema attribute names
        """

        def decorator(func):
            logger.debug("Register on_callback hook: %s %s", attrs_names, func)
            self._register_hook(self.__callback_hooks__, attrs_names, func)
            return func

        return decorator

    def get_callback(self, name: str) -> Optional[Callable]:
        """get callback by name. if not contains - return None"""
        return self.__callback_hooks__.get(name)

    def get_filter(self, name: str) -> Optional[Callable]:
        """get filter by name. if not contains - return None"""
        return self.__filter_hooks__.get(name)

    def get_factory(self, name: str) -> Optional[Callable]:
        """get factory by name. if not contains - return None"""
        return self.__factory_hooks__.get(name)

    def add_hook(self, name: str, hook: Union[FieldHook, FieldHookList]):
        """add FieldHook or FieldHookList in storage."""
        logger.debug("Add `%s` %s", name, hook)
        self.__field_hooks__[name] = hook

    def add_kwargs_hook(
        self,
        name: str,
        default: Optional[Any] = None,
        callback: Optional[Callable] = None,
        filter_: Optional[Callable] = None,
        factory: Optional[Callable] = None,
    ):
        """create hook by keyword arguments and add in storage."""
        logger.debug(
            "Add `%s` FieldHook. Arguments: default=%s, callback=%s, filter_=%s, factory=%s",
            name,
            default,
            callback,
            filter_,
            factory,
        )

        if filter_:
            self.__field_hooks__[name] = FieldHookList(
                default=default, callback=callback, filter_=filter_, factory=factory
            )
            return
        self.__field_hooks__[name] = FieldHook(
            default=default, callback=callback, factory=factory
        )
        return

    def get_hook(self, name: str) -> Union[FieldHook, FieldHookList]:
        """return stored hook. If not founded key - return empty dict"""
        if hook := self.__field_hooks__.get(name):
            logger.debug("Get hook %s. Values: %s", name, hook)
            return hook
        logger.debug("Not contains hook in `%s` key. Return empty dict", name)
        return {}

    def hook_keys(self) -> KeysView[str]:
        """get all hook keys"""
        return self.__field_hooks__.keys()
