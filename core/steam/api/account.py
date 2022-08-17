import json
import re
from typing import Optional

from aiohttp import FormData
from lxml.html import HtmlElement, document_fromstring
from steam.api.enums import Language
from steam.api.errors import NotFoundSteamid
from steam.api.schemas import ProfileInfo, ProfileInfoResponse
from steam.steam import Steam


class SteamAccountAPI:

    def __init__(self, steam: Steam, steamid: Optional[int] = None):
        self.steam = steam
        self._steamid = steamid

    @property
    async def steamid(self) -> int:
        if not self._steamid:
            self._steamid = await self.get_steamid()
        return self._steamid

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

    async def get_profile_info(self) -> ProfileInfo:
        response = await self.steam.request(
            url=f'https://steamcommunity.com/profiles/{await self.steamid}/edit/info',
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                          'image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            },
        )
        page: HtmlElement = document_fromstring(response)
        info = json.loads(page.cssselect('#profile_edit_config')[0].attrib['data-profile-edit'])
        return ProfileInfo(
            personaName=info['strPersonaName'],
            real_name=info['strRealName'],
            customURL=info['strCustomURL'],
            summary=info['strSummary'],
            country=info['LocationData']['locCountry'],
            state=info['LocationData']['locState'],
            city=info['LocationData']['locCity'],
            hide_profile_awards=info['ProfilePreferences']['hide_profile_awards'],
        )

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
        response: ProfileInfoResponse = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{await self.steamid}/edit/',
            data=data,
            headers={
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{await self.steamid}/edit/info',
            },
            response_model=ProfileInfoResponse,
        )
        response.check_response()
