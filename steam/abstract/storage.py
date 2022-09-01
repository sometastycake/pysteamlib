from abc import ABC, abstractmethod
from typing import Dict


class CookieStorageAbstract(ABC):

    @abstractmethod
    async def set(self, login: str, cookies: Dict) -> None:
        ...

    @abstractmethod
    async def get(self, login: str) -> Dict:
        ...

    @abstractmethod
    async def clear(self, login: str) -> None:
        ...
