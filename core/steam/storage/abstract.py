from abc import ABC, abstractmethod
from typing import Dict


class CookieStorage(ABC):
    """
    Cookie storage abstract.
    """
    @abstractmethod
    async def set(self, login: str, value: Dict) -> None:
        ...

    @abstractmethod
    async def get(self, login: str, domain: str) -> Dict:
        ...
