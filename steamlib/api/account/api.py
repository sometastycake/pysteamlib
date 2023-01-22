import json
from typing import List

import aiofiles
from aiohttp import FormData
from lxml.html import HtmlElement, document_fromstring
from pysteamauth.auth import Steam
from yarl import URL

from steamlib.api.enums import Language

from .exceptions import KeyRegistrationError, ProfileError
from .schemas import AvatarResponse, NicknameHistory, PrivacyInfo, PrivacyResponse, ProfileInfo, ProfileInfoResponse


class SteamAccount:

    api_key_registration_errors = [
        'Your account currently has restricted functionality and cannot register for a Steam Web API Key',
        'You will be granted access to Steam Web API keys when you have games in your Steam account.',
    ]

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
        response: str = await self.steam.request(
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid}/edit/info',
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            },
            cookies={
                'Steam_Language': 'english',
            },
            raise_for_status=True,
        )
        self._check_profile_error(response)
        return response

    async def get_nickname_history(self) -> NicknameHistory:
        response: str = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid}/ajaxaliases/',
            headers={
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid}/',
                'Origin': 'https://steamcommunity.com',
            },
            raise_for_status=True,
        )
        return NicknameHistory.parse_raw(response)

    async def change_account_language(self, language: Language) -> bool:
        response: str = await self.steam.request(
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
            raise_for_status=True,
        )
        return True if response == 'true' else False

    async def get_current_profile_info(self) -> ProfileInfo:
        response: str = await self._get_profile_editing_page()
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
        response: str = await self.steam.request(
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
            raise_for_status=True,
        )
        return ProfileInfoResponse.parse_raw(response)

    async def get_current_privacy(self) -> PrivacyInfo:
        response: str = await self._get_profile_editing_page()
        page: HtmlElement = document_fromstring(response)
        info = json.loads(page.cssselect('#profile_edit_config')[0].attrib['data-profile-edit'])
        return PrivacyInfo(**info['Privacy'])

    async def set_privacy(self, settings: PrivacyInfo) -> PrivacyResponse:
        response: str = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid}/ajaxsetprivacy/',
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
            raise_for_status=True,
        )
        return PrivacyResponse.parse_raw(response)

    async def revoke_api_key(self) -> None:
        await self.steam.request(
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
            raise_for_status=True,
        )

    async def register_api_key(self, domain: str) -> str:
        response: str = await self.steam.request(
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
            cookies={
                'Steam_Language': 'english',
            },
            raise_for_status=True,
        )

        for error in self.api_key_registration_errors:
            if error in response:
                raise KeyRegistrationError(error)

        page: HtmlElement = document_fromstring(response)
        key = page.cssselect('#bodyContents_ex > p:nth-child(2)')[0].text
        return key[key.index(' ') + 1:]

    async def register_tradelink(self) -> str:
        token: str = await self.steam.request(
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
            raise_for_status=True,
        )

        params = {
            'partner': self.steam.partner_id,
            'token': token.replace('"', ''),
        }
        return str(URL('https://steamcommunity.com/tradeoffer/new/').with_query(params))

    async def upload_avatar(self, path_to_avatar: str) -> AvatarResponse:
        async with aiofiles.open(path_to_avatar, mode='rb') as file:
            image = await file.read()
        response: str = await self.steam.request(
            method='POST',
            url='https://steamcommunity.com/actions/FileUploader/',
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
            raise_for_status=True,
        )
        return AvatarResponse.parse_raw(response)

    async def get_tradelink(self) -> str:
        response: str = await self.steam.request(
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid}/tradeoffers/privacy',
            headers={
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid}/tradeoffers/',
            },
            cookies={
                'Steam_Language': 'english',
            },
            raise_for_status=True,
        )

        page: HtmlElement = document_fromstring(response)
        return page.get_element_by_id('trade_offer_access_url').value
