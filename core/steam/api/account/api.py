import json
import re
from typing import Optional

import aiofiles
from aiohttp import FormData
from lxml.html import HtmlElement, document_fromstring
from steam.api.account.enums import Language
from steam.api.account.errors import KeyRegistrationError, NotFoundSteamid
from steam.api.account.schemas import AvatarResponse, PrivacyInfo, PrivacyResponse, ProfileInfo, ProfileInfoResponse
from steam.auth.steam import Steam
from steam.callbacks import check_steam_error_from_response
from yarl import URL


class SteamAccountAPI:

    def __init__(self, steam: Steam, steamid: Optional[int] = None):
        self.steam = steam
        self._steamid = steamid

    @property
    async def steamid(self) -> int:
        """
        Get steamid.

        :return: steamid.
        """
        if not self._steamid:
            self._steamid = await self.get_steamid()
        return self._steamid

    async def get_steamid(self) -> int:
        """
        Get steamid from Steam.

        :return: steamid.
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
            raise NotFoundSteamid('Not found steamid')
        return int(steamid.group(1))

    async def change_account_language(self, language: Language) -> bool:
        """
        Change account language.

        :return: Is success.
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
        Get profile info.

        :return: Profile info.
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
        Set profile info.

        :return: Set profile info status.
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
            callback=check_steam_error_from_response,
        )

    async def get_current_privacy(self) -> PrivacyInfo:
        """
        Get privacy settings.

        :return: Privacy info.
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

        :return: Privacy response.
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
            callback=check_steam_error_from_response,
        )

    async def revoke_api_key(self) -> str:
        """
        Revoke api key.

        :return: Result html page.
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

        :return: API key.
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

        :return: Tradelink.
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

    async def upload_avatar(self, path_to_avatar: str) -> AvatarResponse:
        """
        Upload avatar.

        :return: Upload avatar status.
        """
        async with aiofiles.open(path_to_avatar, mode='rb') as file:
            content = await file.read()
        return await self.steam.request(
            method='POST',
            url='https://steamcommunity.com/actions/FileUploader/',
            data=FormData(
                fields=[
                    ('avatar', content),
                    ('type', 'player_avatar_image'),
                    ('sId', str(await self.steamid)),
                    ('sessionid', await self.steam.sessionid()),
                    ('doSub', '1'),
                    ('json', '1'),
                ],
            ),
            headers={
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{await self.steamid}/edit/avatar',
            },
            response_model=AvatarResponse,
        )

    async def account_balance(self) -> int:
        """
        Get account balance.

        :return: Account balance.
        """
        response = await self.steam.request(
            url='https://store.steampowered.com/account/store_transactions/',
            headers={
                'Accept': '*/*',
                'Origin': 'https://steamcommunity.com',
            },
        )
        page: HtmlElement = document_fromstring(response)
        balance = page.get_element_by_id('header_wallet_balance')
        return int(re.search('(\d+)', balance.text).group(1))
