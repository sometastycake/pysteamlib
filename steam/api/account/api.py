import json
import re

import aiofiles
from aiohttp import FormData
from lxml.html import HtmlElement, document_fromstring
from yarl import URL

from steam.api.account.enums import Language
from steam.api.account.errors import KeyRegistrationError
from steam.api.account.schemas import (
    AvatarResponse,
    NicknameHistory,
    PrivacyInfo,
    PrivacyResponse,
    ProfileInfo,
    ProfileInfoResponse,
)
from steam.auth.steam import Steam
from steam.callbacks import _check_steam_error_from_response


class SteamAccount:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def get_nickname_history(self, login: str) -> NicknameHistory:
        """
        Get nickname history.
        """
        response: str = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/ajaxaliases/',
            headers={
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/',
                'Origin': 'https://steamcommunity.com',
            },
            login=login,
        )
        return NicknameHistory.parse_raw(response)

    async def change_account_language(self, language: Language, login: str) -> bool:
        """
        Change account language.
        """
        response = await self.steam.request(
            method='POST',
            url='https://steamcommunity.com/actions/SetLanguage/',
            data={
                'sessionid': await self.steam.sessionid(login),
                'language': language.value,
            },
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With:': 'XMLHttpRequest',
                'Origin': 'https://steamcommunity.com',
            },
            login=login,
        )
        return True if response == 'true' else False

    async def get_current_profile_info(self, login: str) -> ProfileInfo:
        """
        Get profile info.
        """
        response = await self.steam.request(
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/edit/info',
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            },
            login=login,
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

    async def set_profile_info(self, info: ProfileInfo, login: str) -> ProfileInfoResponse:
        """
        Set profile info.
        """
        response = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/edit/',
            data=FormData(
                fields=[
                    ('sessionID', await self.steam.sessionid(login)),
                    ('type', 'profileSave'),
                    *list(info),
                    ('type', 'profileSave'),
                    ('sessionID', await self.steam.sessionid(login)),
                    ('json', '1'),
                ],
            ),
            headers={
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/edit/info',
            },
            login=login,
        )
        result = ProfileInfoResponse.parse_raw(response)
        _check_steam_error_from_response(result)
        return result

    async def get_current_privacy(self, login: str) -> PrivacyInfo:
        """
        Get privacy settings.
        """
        response = await self.steam.request(
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/edit/info',
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            },
            login=login,
        )
        page: HtmlElement = document_fromstring(response)
        info = json.loads(page.cssselect('#profile_edit_config')[0].attrib['data-profile-edit'])
        return PrivacyInfo(**info['Privacy'])

    async def set_privacy(self, settings: PrivacyInfo, login: str) -> PrivacyResponse:
        """
        Privacy settings.
        """
        response: str = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/ajaxsetprivacy/',
            data=FormData(
                fields=[
                    ('sessionid', await self.steam.sessionid(login)),
                    ('Privacy', settings.PrivacySettings.json()),
                    ('eCommentPermission', settings.eCommentPermission.value),
                ],
            ),
            headers={
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/edit/settings',
            },
            login=login,
        )
        result = PrivacyResponse.parse_raw(response)
        _check_steam_error_from_response(result)
        return result

    async def revoke_api_key(self, login: str) -> str:
        """
        Revoke api key.
        """
        return await self.steam.request(
            url='https://steamcommunity.com/dev/revokekey',
            method='POST',
            data={
                'Revoke': 'Revoke My Steam Web API Key',
                'sessionid': await self.steam.sessionid(login),
            },
            headers={
                'Origin': 'https://steamcommunity.com',
                'Referer': 'https://steamcommunity.com/dev/apikey',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            login=login,
        )

    async def register_api_key(self, domain: str, login: str) -> str:
        """
        Register api key.
        """
        response = await self.steam.request(
            url='https://steamcommunity.com/dev/registerkey',
            method='POST',
            data={
                'domain': domain,
                'agreeToTerms': 'agreed',
                'sessionid': await self.steam.sessionid(login),
                'Submit': 'Register',
            },
            headers={
                'Origin': 'https://steamcommunity.com',
                'Referer': 'https://steamcommunity.com/dev/apikey',
            },
            login=login,
        )

        error = 'You will be granted access to Steam Web API keys when you have games in your Steam account.'
        if error in response:
            raise KeyRegistrationError(error)

        page: HtmlElement = document_fromstring(response)
        key = page.cssselect('#bodyContents_ex > p:nth-child(2)')[0].text
        return key[key.index(' ') + 1:]

    async def register_tradelink(self, login: str) -> str:
        """
        Register tradelink.
        """
        token = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/tradeoffers/newtradeurl',
            data={
                'sessionid': await self.steam.sessionid(login),
            },
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/tradeoffers/privacy',
                'X-Requested-With': 'XMLHttpRequest',
            },
            login=login,
        )

        params = {
            'partner': self.steam.steamid(login) - 76561197960265728,
            'token': token.replace('"', ''),
        }
        return str(URL('https://steamcommunity.com/tradeoffer/new/').with_query(params))

    async def upload_avatar(self, path_to_avatar: str, login: str) -> AvatarResponse:
        """
        Upload avatar.
        """
        async with aiofiles.open(path_to_avatar, mode='rb') as file:
            image = await file.read()
        response = await self.steam.request(
            method='POST',
            url='https://steamcommunity.com/actions/FileUploader/',
            data=FormData(
                fields=[
                    ('avatar', image),
                    ('type', 'player_avatar_image'),
                    ('sId', self.steam.steamid(login)),
                    ('sessionid', await self.steam.sessionid(login)),
                    ('doSub', '1'),
                    ('json', '1'),
                ],
            ),
            headers={
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/edit/avatar',
            },
            login=login,
        )
        return AvatarResponse.parse_raw(response)

    async def account_balance(self, login: str) -> int:
        """
        Get account balance.
        """
        response = await self.steam.request(
            url='https://store.steampowered.com/account/store_transactions/',
            headers={
                'Accept': '*/*',
                'Upgrade-Insecure-Requests': '1',
            },
            login=login,
        )
        page: HtmlElement = document_fromstring(response)
        balance = page.get_element_by_id('header_wallet_balance')
        return int(re.search(r'(\d+)', balance.text).group(1))
