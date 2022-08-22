from abc import ABC, abstractmethod
from typing import Dict


class CookieStorage(ABC):
    """
    Cookie storage abstract.
    """
    def __init__(self, key: str):
        self._key = key

    @property
    def key(self) -> str:
        return self._key

    @abstractmethod
    async def set(self, value: Dict) -> None:
        ...

    @abstractmethod
    async def get(self) -> Dict:
        ...
