from typing import Any, Dict

from steam.storage.abstract import CookieStorage


class BaseStorage(CookieStorage):

    def __init__(self, key: str):
        super().__init__(key)
        self._cookie: Dict = {}

    async def get(self) -> Dict:
        return self._cookie.get(self.key, {})

    async def set(self, value: Any) -> None:
        self._cookie[self.key] = value
