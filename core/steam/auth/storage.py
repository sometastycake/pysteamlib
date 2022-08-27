from typing import Dict

from steam.storage.abstract import CookieStorage


class BaseStorage(CookieStorage):

    def __init__(self):
        self.cookie: Dict = {}

    async def get(self, login: str, domain: str) -> Dict:
        cookies = self.cookie.get(login, {})
        return cookies.get(domain, {})

    async def set(self, login: str, value: Dict) -> None:
        self.cookie[login] = value
