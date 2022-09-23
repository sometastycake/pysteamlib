import json
from typing import List

import aiofiles
from aiohttp import FormData
from lxml.html import HtmlElement, document_fromstring
from pysteamauth.auth import Steam
from pysteamauth.errors.exceptions import UnauthorizedSteamRequestError
from yarl import URL

from steamlib.api.account.exceptions import KeyRegistrationError, ProfileError
from steamlib.api.account.schemas import (
    AvatarResponse,
    NicknameHistory,
    PrivacyInfo,
    PrivacyResponse,
    ProfileInfo,
    ProfileInfoResponse,
)
from steamlib.api.enums import Language


class SteamAccount:

    def __init__(self, steam: Steam):
        self.steam = steam

    def _check_profile_error(self, response: str) -> None:
        if 'class="profile_fatalerror_message"' in response:
            page: HtmlElement = document_fromstring(response)
            tag: List[HtmlElement] = page.cssselect('.profile_fatalerror .profile_fatalerror_message')
            message = 'Profile error'
            if tag:
                message = tag[0].text
            raise ProfileError(message)

    async def _get_profile_editing_page(self) -> str:
        """
        Get profile editing page.
        """
        url = f'https://steamcommunity.com/profiles/{self.steam.steamid}/edit/info'
        response = await self.steam.request(
            url=url,
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            },
            cookies={
                'Steam_Language': 'english',
            },
        )
        if str(self.steam.steamid) not in response:
            raise UnauthorizedSteamRequestError(f'Unauthorized request to "{url}"')
        self._check_profile_error(response)
        return response

    async def get_nickname_history(self) -> NicknameHistory:
        """
        Get nickname history.
        """
        response: str = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid}/ajaxaliases/',
            headers={
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid}/',
                'Origin': 'https://steamcommunity.com',
            },
        )
        return NicknameHistory.parse_raw(response)

    async def change_account_language(self, language: Language) -> bool:
        """
        Change account language.
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
        """
        response = await self._get_profile_editing_page()
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
        """
        response = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid}/edit/',
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
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid}/edit/info',
            },
        )
        result = ProfileInfoResponse.parse_raw(response)
        result.check_error()
        return result

    async def get_current_privacy(self) -> PrivacyInfo:
        """
        Get privacy settings.
        """
        response = await self._get_profile_editing_page()
        page: HtmlElement = document_fromstring(response)
        info = json.loads(page.cssselect('#profile_edit_config')[0].attrib['data-profile-edit'])
        return PrivacyInfo(**info['Privacy'])

    async def set_privacy(self, settings: PrivacyInfo) -> PrivacyResponse:
        """
        Privacy settings.
        """
        url = f'https://steamcommunity.com/profiles/{self.steam.steamid}/ajaxsetprivacy/'
        response: str = await self.steam.request(
            method='POST',
            url=url,
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
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid}/edit/settings',
            },
        )
        result = PrivacyResponse.parse_raw(response)
        result.check_error()
        return result

    async def revoke_api_key(self) -> None:
        """
        Revoke api key.
        """
        url = 'https://steamcommunity.com/dev/revokekey'
        response = await self.steam.request(
            url=url,
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
        if str(self.steam.steamid) not in response:
            raise UnauthorizedSteamRequestError(f'Unauthorized request to "{url}"')

    async def register_api_key(self, domain: str) -> str:
        """
        Register api key.
        """
        url = 'https://steamcommunity.com/dev/registerkey'
        response = await self.steam.request(
            url=url,
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

        if str(self.steam.steamid) not in response:
            raise UnauthorizedSteamRequestError(f'Unauthorized request to "{url}"')

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
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid}/tradeoffers/newtradeurl',
            data={
                'sessionid': await self.steam.sessionid(),
            },
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid}/tradeoffers/privacy',
                'X-Requested-With': 'XMLHttpRequest',
            },
        )

        params = {
            'partner': self.steam.steamid - 76561197960265728,
            'token': token.replace('"', ''),
        }
        return str(URL('https://steamcommunity.com/tradeoffer/new/').with_query(params))

    async def upload_avatar(self, path_to_avatar: str) -> AvatarResponse:
        """
        Upload avatar.
        """
        async with aiofiles.open(path_to_avatar, mode='rb') as file:
            image = await file.read()
        url = 'https://steamcommunity.com/actions/FileUploader/'
        response = await self.steam.request(
            method='POST',
            url=url,
            data=FormData(
                fields=[
                    ('avatar', image),
                    ('type', 'player_avatar_image'),
                    ('sId', str(self.steam.steamid)),
                    ('sessionid', await self.steam.sessionid()),
                    ('doSub', '1'),
                    ('json', '1'),
                ],
            ),
            headers={
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid}/edit/avatar',
            },
        )
        if response == '#Error_BadOrMissingSteamID':
            raise UnauthorizedSteamRequestError(f'Unauthorized request to "{url}"')
        return AvatarResponse.parse_raw(response)
