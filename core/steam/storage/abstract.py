"""
Cookie storage example.

class SimpleStorage(CookieStorage):

    def __init__(self, key: str):
        super().__init__(key)
        self.cache = {}

    async def set(self, value: Dict[str, Any]) -> None:
        self.cache.update({self._key: value})

    async def get(self) -> Dict[str, Any]:
        return self.cache.get(self._key)

"""
from abc import ABC, abstractmethod
from typing import Any


class CookieStorage(ABC):
    """
    Cookie storage abstract.
    """
    def __init__(self, key: str):
        self._key = key

    @abstractmethod
    async def set(self, value: Any) -> Any:
        ...

    @abstractmethod
    async def get(self) -> Any:
        ...
