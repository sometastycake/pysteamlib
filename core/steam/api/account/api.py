import json
import re
from typing import Optional

from aiohttp import FormData
from lxml.html import HtmlElement, document_fromstring
from steam.api.account.enums import Language
from steam.api.account.errors import KeyRegistrationError, NotFoundSteamid
from steam.api.account.schemas import PrivacyInfo, PrivacyResponse, ProfileInfo, ProfileInfoResponse
from steam.steam import Steam
from yarl import URL


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
        """
        Getting steamid (digital id of account).
        """
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
        """
        Changing account language.
        """
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

    async def get_current_profile_info(self) -> ProfileInfo:
        """
        Getting profile info.
        """
        response = await self.steam.request(
            url=f'https://steamcommunity.com/profiles/{await self.steamid}/edit/info',
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
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

    async def set_profile_info(self, info: ProfileInfo) -> ProfileInfoResponse:
        """
        Setting profile info.
        """
        return await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{await self.steamid}/edit/',
            data=FormData(
                fields=[
                    ('sessionID', await self.steam.sessionid()),
                    ('type', 'profileSave'),
                    *list(info),
                    ('type', 'profileSave'),
                    ('sessionID', await self.steam.sessionid()),
                    ('json', '1'),
                ],
            ),
            headers={
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{await self.steamid}/edit/info',
            },
            response_model=ProfileInfoResponse,
        )

    async def get_current_privacy(self) -> PrivacyInfo:
        """
        Getting privacy settings.
        """
        response = await self.steam.request(
            url=f'https://steamcommunity.com/profiles/{await self.steamid}/edit/info',
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            },
        )
        page: HtmlElement = document_fromstring(response)
        info = json.loads(page.cssselect('#profile_edit_config')[0].attrib['data-profile-edit'])
        return PrivacyInfo(**info['Privacy'])

    async def set_privacy(self, settings: PrivacyInfo) -> PrivacyResponse:
        """
        Privacy settings.
        """
        return await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{await self.steamid}/ajaxsetprivacy/',
            data=FormData(
                fields=[
                    ('sessionid', await self.steam.sessionid()),
                    ('Privacy', settings.PrivacySettings.json()),
                    ('eCommentPermission', settings.eCommentPermission.value),
                ],
            ),
            headers={
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{await self.steamid}/edit/settings',
            },
            response_model=PrivacyResponse,
        )

    async def revoke_api_key(self) -> str:
        """
        Revoke api key.
        """
        return await self.steam.request(
            url='https://steamcommunity.com/dev/revokekey',
            method='POST',
            data={
                'Revoke': 'Revoke My Steam Web API Key',
                'sessionid': await self.steam.sessionid(),
            },
            headers={
                'Origin': 'https://steamcommunity.com',
                'Referer': 'https://steamcommunity.com/dev/apikey',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        )

    async def register_api_key(self, domain: str) -> str:
        """
        Register api key.
        """
        response = await self.steam.request(
            url='https://steamcommunity.com/dev/registerkey',
            method='POST',
            data={
                'domain': domain,
                'agreeToTerms': 'agreed',
                'sessionid': await self.steam.sessionid(),
                'Submit': 'Register',
            },
            headers={
                'Origin': 'https://steamcommunity.com',
                'Referer': 'https://steamcommunity.com/dev/apikey',
            },
        )

        error = 'You will be granted access to Steam Web API keys when you have games in your Steam account.'
        if error in response:
            raise KeyRegistrationError(error)

        page: HtmlElement = document_fromstring(response)
        key = page.cssselect('#bodyContents_ex > p:nth-child(2)')[0].text
        return key[key.index(' ') + 1:]

    async def register_tradelink(self) -> str:
        """
        Register tradelink.
        """
        token = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{await self.steamid}/tradeoffers/newtradeurl',
            data={
                'sessionid': await self.steam.sessionid(),
            },
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{await self.steamid}/tradeoffers/privacy',
                'X-Requested-With': 'XMLHttpRequest',
            },
        )

        params = {
            'partner': await self.steamid - 76561197960265728,
            'token': token.replace('"', ''),
        }
        return str(URL('https://steamcommunity.com/tradeoffer/new/').with_query(params))
