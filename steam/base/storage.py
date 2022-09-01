from typing import Dict

from steam.abstract.storage import CookieStorageAbstract


class BaseCookieStorage(CookieStorageAbstract):

    def __init__(self):
        self.cookies: Dict = {}

    async def get(self, login: str) -> Dict:
        return self.cookies.get(login, {})

    async def set(self, login: str, cookies: Dict) -> None:
        self.cookies[login] = cookies

    async def clear(self, login: str) -> None:
        self.cookies.pop(login, None)
