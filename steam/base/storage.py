from typing import Dict

from steam.abstract.storage import CookieStorageAbstract


class BaseCookieStorage(CookieStorageAbstract):

    def __init__(self):
        self.cookie: Dict = {}

    async def get(self, login: str) -> Dict:
        return self.cookie.get(login, {})

    async def set(self, login: str, cookies: Dict) -> None:
        self.cookie[login] = cookies
