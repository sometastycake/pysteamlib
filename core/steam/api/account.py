import re

from steam.api.enums import Language
from steam.api.errors import NotFoundSteamid
from steam.steam import Steam


class SteamAccountAPI:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def get_steamid(self) -> int:
        response = await self.steam.request(
            url='https://steamcommunity.com/',
            headers={
                'Accept': '*/*',
                'Origin': 'https://steamcommunity.com',
            }
        )
        steamid = re.search(
            pattern='g_steamID = \"(\d+)\";',
            string=response,
        )
        if not steamid:
            raise NotFoundSteamid
        return int(steamid.group(1))

    async def change_account_language(self, language: Language) -> bool:
        response = await self.steam.request(
            method='POST',
            url='https://steamcommunity.com/actions/SetLanguage/',
            data={
                'sessionid': await self.steam.sessionid(),
                'language': language.value,
            },
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With:': 'XMLHttpRequest',
                'Origin': 'https://steamcommunity.com',
            }
        )
        return True if response == 'true' else False
