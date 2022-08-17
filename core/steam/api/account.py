from steam.api.enums import Language
from steam.steam import Steam


class SteamAccountAPI:

    def __init__(self, steam: Steam):
        self.steam = steam

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
