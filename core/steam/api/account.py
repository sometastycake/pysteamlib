import re
from typing import Optional

from aiohttp import FormData
from steam.api.enums import Language
from steam.api.errors import NotFoundSteamid
from steam.api.schemas import ProfileInfo, ProfileInfoResponse
from steam.steam import Steam


class SteamAccountAPI:

    def __init__(self, steam: Steam, steamid: Optional[int] = None):
        self.steam = steam
        self.steamid = steamid

    async def get_steamid(self) -> int:
        response = await self.steam.request(
            url='https://steamcommunity.com/',
            headers={
                'Accept': '*/*',
                'Origin': 'https://steamcommunity.com',
            },
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
            },
        )
        return True if response == 'true' else False

    async def set_profile_info(self, info: ProfileInfo) -> None:
        data = FormData(
            fields=[
                ('sessionID', await self.steam.sessionid()),
                ('type', 'profileSave'),
                *list(info),
                ('type', 'profileSave'),
                ('sessionID', await self.steam.sessionid()),
                ('json', '1'),
            ],
        )
        steamid = self.steamid
        if not steamid:
            steamid = await self.get_steamid()
        response: ProfileInfoResponse = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{steamid}/edit/',
            data=data,
            headers={
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{steamid}/edit/info',
            },
            response_model=ProfileInfoResponse,
        )
        response.check_response()
