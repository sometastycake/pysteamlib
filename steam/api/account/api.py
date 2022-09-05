import json
import re

import aiofiles
from aiohttp import FormData
from lxml.html import HtmlElement, document_fromstring
from yarl import URL

from steam.api.account.enums import Language
from steam.api.account.exceptions import KeyRegistrationError
from steam.api.account.schemas import (
    AvatarResponse,
    NicknameHistory,
    PrivacyInfo,
    PrivacyResponse,
    ProfileInfo,
    ProfileInfoResponse,
)
from steam.auth.steam import Steam
from steam.errors.exceptions import UnauthorizedSteamRequestError
from steam.errors.response import check_steam_error_from_response


class SteamAccount:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def _get_profile_editing_page(self, login: str) -> str:
        """
        Get profile editing page.
        """
        url = f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/edit/info'
        response = await self.steam.http.request(
            url=url,
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            },
            cookies=await self.steam.cookies(login),
        )
        if str(self.steam.steamid(login)) not in response:
            raise UnauthorizedSteamRequestError(url=url)
        return response

    async def get_nickname_history(self, login: str) -> NicknameHistory:
        """
        Get nickname history.
        """
        response: str = await self.steam.http.request(
            method='POST',
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/ajaxaliases/',
            headers={
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/',
                'Origin': 'https://steamcommunity.com',
            },
            cookies=await self.steam.cookies(login),
        )
        return NicknameHistory.parse_raw(response)

    async def change_account_language(self, language: Language, login: str) -> bool:
        """
        Change account language.
        """
        response = await self.steam.http.request(
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
            cookies=await self.steam.cookies(login),
        )
        return True if response == 'true' else False

    async def get_current_profile_info(self, login: str) -> ProfileInfo:
        """
        Get profile info.
        """
        response = await self._get_profile_editing_page(login)
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
        response = await self.steam.http.request(
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
            cookies=await self.steam.cookies(login),
        )
        result = ProfileInfoResponse.parse_raw(response)
        check_steam_error_from_response(result)
        return result

    async def get_current_privacy(self, login: str) -> PrivacyInfo:
        """
        Get privacy settings.
        """
        response = await self._get_profile_editing_page(login)
        page: HtmlElement = document_fromstring(response)
        info = json.loads(page.cssselect('#profile_edit_config')[0].attrib['data-profile-edit'])
        return PrivacyInfo(**info['Privacy'])

    async def set_privacy(self, settings: PrivacyInfo, login: str) -> PrivacyResponse:
        """
        Privacy settings.
        """
        url = f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/ajaxsetprivacy/'
        response: str = await self.steam.http.request(
            method='POST',
            url=url,
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
            cookies=await self.steam.cookies(login),
        )
        result = PrivacyResponse.parse_raw(response)
        check_steam_error_from_response(result)
        return result

    async def revoke_api_key(self, login: str) -> None:
        """
        Revoke api key.
        """
        url = 'https://steamcommunity.com/dev/revokekey'
        response = await self.steam.http.request(
            url=url,
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
            cookies=await self.steam.cookies(login),
        )
        if str(self.steam.steamid(login)) not in response:
            raise UnauthorizedSteamRequestError(url=url)

    async def register_api_key(self, domain: str, login: str) -> str:
        """
        Register api key.
        """
        cookies = await self.steam.cookies(login)
        cookies.update({
            'Steam_Language': 'english',
        })
        url = 'https://steamcommunity.com/dev/registerkey'
        response = await self.steam.http.request(
            url=url,
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
            cookies=cookies,
        )

        if str(self.steam.steamid(login)) not in response:
            raise UnauthorizedSteamRequestError(url=url)

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
        token = await self.steam.http.request(
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
            cookies=await self.steam.cookies(login),
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
        url = 'https://steamcommunity.com/actions/FileUploader/'
        response = await self.steam.http.request(
            method='POST',
            url=url,
            data=FormData(
                fields=[
                    ('avatar', image),
                    ('type', 'player_avatar_image'),
                    ('sId', str(self.steam.steamid(login))),
                    ('sessionid', await self.steam.sessionid(login)),
                    ('doSub', '1'),
                    ('json', '1'),
                ],
            ),
            headers={
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/edit/avatar',
            },
            cookies=await self.steam.cookies(login),
        )
        if response == '#Error_BadOrMissingSteamID':
            raise UnauthorizedSteamRequestError(url=url)
        return AvatarResponse.parse_raw(response)

    async def account_balance(self, login: str) -> int:
        """
        Get account balance.
        """
        _, cookies = await self.steam.http.request_with_cookie_return(
            url='https://store.steampowered.com/account/',
            cookies=await self.steam.cookies(login),
        )
        cookies.update(await self.steam.cookies(login))
        url = 'https://store.steampowered.com/account/'
        response = await self.steam.http.request(
            url=url,
            headers={
                'Accept': '*/*',
                'Upgrade-Insecure-Requests': '1',
            },
            cookies=cookies,
        )
        if str(self.steam.steamid(login)) not in response:
            raise UnauthorizedSteamRequestError(url=url)
        page: HtmlElement = document_fromstring(response)
        balance = page.cssselect('.accountBalance > .price > a')
        if not balance:
            balance = page.cssselect('.accountBalance > .price')
        return int(re.search(r'(\d+)', balance[0].text).group(1))
