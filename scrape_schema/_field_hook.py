from functools import wraps
from typing import Callable, Dict, Optional, Tuple, Union


class FieldHooks:
    _instance = None

    __callback_hooks__: Dict[str, Callable] = {}
    __factory_hooks__: Dict[str, Callable] = {}
    __filter_hooks__: Dict[str, Callable] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def _register_hook(
        hooks_dict: Dict[str, Callable],
        name: Union[str, Tuple[str, ...]],
        func: Callable,
    ):
        if isinstance(name, str):
            hooks_dict[name] = func
            return
        elif isinstance(name, tuple) and all(isinstance(n, str) for n in name):
            for n in name:
                hooks_dict[n] = func
            return
        raise TypeError("`name` should be `str` or `tuple[str, ...]`")

    def filter(self, name: Union[str, Tuple[str, ...]]):
        def decorator(func):
            self._register_hook(self.__filter_hooks__, name, func)
            return func

        return decorator

    def factory(self, name: Union[str, Tuple[str, ...]]):
        def decorator(func):
            self._register_hook(self.__factory_hooks__, name, func)
            return func

        return decorator

    def callback(self, name: Union[str, Tuple[str, ...]]):
        def decorator(func):
            self._register_hook(self.__callback_hooks__, name, func)
            return func

        return decorator

    def get_callback(self, name: str) -> Optional[Callable]:
        return self.__callback_hooks__.get(name)

    def get_filter(self, name: str) -> Optional[Callable]:
        return self.__filter_hooks__.get(name)

    def get_factory(self, name: str) -> Optional[Callable]:
        return self.__factory_hooks__.get(name)
