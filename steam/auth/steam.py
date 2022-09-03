import asyncio
import base64
import binascii
import hashlib
import hmac
import json
import math
import time
from struct import pack
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar

from bitstring import BitArray
from lxml.html import HtmlElement, document_fromstring

from steam.abstract.captcha import CaptchaSolverAbstract
from steam.abstract.request import RequestStrategyAbstract
from steam.abstract.storage import CookieStorageAbstract
from steam.auth.exc import (
    AccountAlreadyExistsError,
    GetRsaError,
    IncorrectCredentials,
    InvalidAuthenticatorError,
    LoginError,
    NotFoundAuthenticatorError,
    NotFoundMobileConfirmationError,
    TooManyAuthorizations,
)
from steam.auth.schemas import (
    RSA,
    AccountData,
    Authenticator,
    LoginRequest,
    LoginResult,
    MobileConfirmation,
    ServerTimeResponse,
    SteamAuthorizationStatus,
)
from steam.base.captcha.captcha import BaseAntigateCaptchaSolver
from steam.base.request import BaseRequestStrategy
from steam.base.storage import BaseCookieStorage

CookieStorageType = TypeVar('CookieStorageType', bound=CookieStorageAbstract)
RequestStrategyType = TypeVar('RequestStrategyType', bound=RequestStrategyAbstract)
CaptchaSolverType = TypeVar('CaptchaSolverType', bound=CaptchaSolverAbstract)


class Steam:
    """
    Steam authorization class.
    """
    def __init__(
        self,
        storage_class: Type[CookieStorageType] = BaseCookieStorage,
        request_class: Type[RequestStrategyAbstract] = BaseRequestStrategy,
        captcha_solver_class: Type[CaptchaSolverType] = BaseAntigateCaptchaSolver,
    ):
        self._http = request_class()
        self._storage = storage_class()
        self._captcha_solver = captcha_solver_class()
        self._accounts: Dict[str, AccountData] = {}

    @property
    def http(self) -> RequestStrategyAbstract:
        return self._http

    def steamid(self, login: str) -> int:
        """Get steamid."""
        return self._accounts[login].steamid

    def password(self, login: str) -> str:
        """Get password."""
        return self._accounts[login].password

    def authenticator(self, login: str) -> Authenticator:
        """Get authenticator."""
        authenticator = self._accounts[login].authenticator
        if authenticator is None:
            raise NotFoundAuthenticatorError(f'Not found authenticator: "{login}"')
        return authenticator

    def add_account(self, login: str, details: AccountData):
        """Add account."""
        if login in self._accounts:
            raise AccountAlreadyExistsError(f'Account already exists: "{login}"')
        self._accounts[login] = details

    async def cookies(self, login: str) -> Dict[str, str]:
        """Get cookies."""
        return await self._storage.get(login)

    async def sessionid(self, login: str) -> str:
        """Sessionid cookie."""
        return (await self.cookies(login))['sessionid']

    async def request_for_login(self, url: str, login: str, method: str = 'GET', **kwargs: Any) -> str:
        """
        Request with Steam session for specified login.
        """
        cookies = await self._storage.get(login)

        return await self._http.request(
            url=url,
            method=method,
            cookies={
                **cookies,
                **kwargs.pop('cookies', {}),
            },
            **kwargs,
        )

    async def is_authorized(self, login: str) -> bool:
        """
        Is alive authorization.
        """
        response = await self.request_for_login(
            url='https://steamcommunity.com/chat/clientjstoken',
            login=login,
        )
        return SteamAuthorizationStatus.parse_raw(response).logged_in

    async def _getrsakey(self, login: str) -> RSA:
        """
        Getting data for password encryption.
        """
        response = await self.request_for_login(
            method='POST',
            url='https://steamcommunity.com/login/getrsakey/',
            data={
                'donotcache': int(time.time()),
                'username': login,
            },
            login=login,
            cookies={
                'mobileClient': 'ios',
                'mobileClientVersion': '2.0.20',
            },
        )
        return RSA.parse_raw(response)

    async def _do_login(self, request: LoginRequest) -> Tuple[LoginResult, Dict[str, str]]:
        """
        Authorization request.
        """
        response, cookies = await self._http.request_with_cookie_return(
            method='POST',
            url='https://steamcommunity.com/login/dologin/',
            data=request.dict(),
            cookies={
                'mobileClient': 'ios',
                'mobileClientVersion': '2.0.20',
            },
        )
        return LoginResult.parse_raw(response), cookies

    async def get_server_time(self) -> int:
        """
        Get server time.
        """
        response = await self._http.request(
            method='POST',
            url='https://api.steampowered.com/ITwoFactorService/QueryTime/v0001',
        )
        return ServerTimeResponse.parse_raw(response).response.server_time

    async def get_steam_guard(self, shared_secret: str) -> str:
        """
        Calculating Steam Guard code.
        """
        server_time = await self.get_server_time()

        data = binascii.unhexlify(
            hmac.new(
                key=base64.b64decode(shared_secret),
                msg=pack('!L', 0) + pack('!L', math.floor(server_time // 30)),
                digestmod=hashlib.sha1,
            ).hexdigest(),
        )

        value = data[19] & 0xF
        fullcode = (
            (data[value] & 0x7F) << 24 |       # noqa:W504
            (data[value + 1] & 0xFF) << 16 |   # noqa:W504
            (data[value + 2] & 0xFF) << 8 |    # noqa:W504
            (data[value + 3] & 0xFF)
        )

        code = ''
        chars = '23456789BCDFGHJKMNPQRTVWXY'
        for _ in range(5):
            code += chars[fullcode % len(chars)]
            fullcode //= len(chars)

        return code

    def _get_confirmation_hash(self, server_time: int, identity_secret: str, tag: str = 'conf') -> str:
        """
        Get confirmation hash.
        """
        identitysecret = base64.b64decode(identity_secret)
        secret = BitArray(
            bytes=identitysecret,
            length=len(identitysecret) * 8,
        )
        tag_buffer = BitArray(
            bytes=tag.encode('utf8'),
            length=len(tag) * 8,
        )
        buffer = BitArray(4 * 8)
        buffer.append(BitArray(int=server_time, length=32))
        buffer.append(tag_buffer)
        confirmation = hmac.new(
            key=secret.tobytes(),
            msg=buffer.tobytes(),
            digestmod=hashlib.sha1,
        )
        return str(base64.b64encode(confirmation.digest()), 'utf8')

    def _parse_mobile_confirmations_response(self, response: str) -> List[MobileConfirmation]:
        """
        Parse mobile confirmations response.
        """
        page: HtmlElement = document_fromstring(response)
        raw_confirmations: List[HtmlElement] = page.cssselect('#mobileconf_list > .mobileconf_list_entry')
        if not raw_confirmations:
            return []
        confirmations = []
        for confirmation in raw_confirmations:
            confirmations.append(MobileConfirmation(
                confirmation_id=int(confirmation.attrib['data-confid']),
                confirmation_key=int(confirmation.attrib['data-key']),
                tradeofferid=int(confirmation.attrib['data-creator']),
            ))
        return confirmations

    async def get_mobile_confirmations(self, login: str) -> List[MobileConfirmation]:
        """
        Get mobile confirmations.
        """
        cookies = await self._storage.get(login)
        cookies.update({
            'mobileClient': 'ios',
            'mobileClientVersion': '2.0.20',
            'steamid': str(self.steamid(login)),
            'Steam_Language': 'english',
        })
        server_time = await self.get_server_time()
        confirmation_hash = self._get_confirmation_hash(
            server_time=server_time,
            identity_secret=self.authenticator(login).identity_secret,
        )
        response = await self._http.request(
            url='https://steamcommunity.com/mobileconf/conf',
            method='GET',
            cookies=cookies,
            params={
                'p': self.authenticator(login).device_id,
                'a': str(self.steamid(login)),
                'k': confirmation_hash,
                't': server_time,
                'm': 'ios',
                'tag': 'conf',
            },
        )
        if '<div>Invalid authenticator</div>' in response:
            raise InvalidAuthenticatorError
        return self._parse_mobile_confirmations_response(response)

    async def mobile_confirm(self, confirmation: MobileConfirmation, login: str) -> bool:
        """
        Mobile confirm.
        """
        cookies = await self._storage.get(login)
        cookies.update({
            'mobileClient': 'ios',
            'mobileClientVersion': '2.0.20',
        })
        server_time = await self.get_server_time()
        confirmation_hash = self._get_confirmation_hash(
            server_time=server_time,
            identity_secret=self.authenticator(login).identity_secret,
            tag='allow',
        )
        response = await self._http.request(
            url='https://steamcommunity.com/mobileconf/ajaxop',
            method='GET',
            cookies=cookies,
            params={
                'op': 'allow',
                'p': self.authenticator(login).device_id,
                'a': str(self.steamid(login)),
                'k': confirmation_hash,
                't': server_time,
                'm': 'ios',
                'tag': 'allow',
                'cid': confirmation.confirmation_id,
                'ck': confirmation.confirmation_key,
            },
        )
        return json.loads(response)['success']

    async def mobile_confirm_by_tradeofferid(self, tradeofferid: int, login: str) -> bool:
        """
        Mobile confirm by tradeofferid.
        """
        confirmations = await self.get_mobile_confirmations(login)
        for confirmation in confirmations:
            if confirmation.tradeofferid == tradeofferid:
                return await self.mobile_confirm(confirmation, login)
        raise NotFoundMobileConfirmationError(f'Not found confirmation for {tradeofferid}')

    async def _login(self, request: LoginRequest, login: str) -> Tuple[LoginResult, Dict[str, str]]:
        """
        Authorization.
        """
        result, cookies = await self._do_login(request)

        for _ in range(3):
            if result.success:
                return result, cookies

            if result.is_credentials_incorrect():
                raise IncorrectCredentials

            if result.is_too_many_authorizations():
                raise TooManyAuthorizations

            if result.captcha_needed:
                request.captcha_text = await self._captcha_solver(
                    link=result.captcha_url,
                )
                request.captchagid = result.captcha_gid

            if result.requires_twofactor:
                shared_secret = self.authenticator(login).shared_secret
                request.twofactorcode = await self.get_steam_guard(
                    shared_secret=shared_secret,
                )

            result, cookies = await self._do_login(request)

        if not result.success:
            raise LoginError(result.message)

        return result, cookies

    async def _get_sessionid_from_steam(self) -> str:
        """Get sessionid cookie from Steam."""
        _, cookies = await self._http.request_with_cookie_return(
            method='GET',
            url='https://steamcommunity.com',
            cookies={
                'mobileClient': 'ios',
                'mobileClientVersion': '2.0.20',
            },
        )
        return cookies['sessionid']

    async def login_to_steam(self, login: str) -> None:
        """
        Login to Steam.
        """
        if await self.is_authorized(login):
            return

        sessionid = await self._get_sessionid_from_steam()

        keys = await self._getrsakey(login)
        if not keys.success:
            raise GetRsaError

        request = LoginRequest(
            password=keys.encrypt_password(self.password(login)),
            username=login,
            rsatimestamp=keys.timestamp,
        )

        result, cookies = await self._login(request, login)

        cookies.update({
            'sessionid': sessionid,
            'steamLogin': result.steam_login(),
            'steamLoginSecure': result.steam_login_secure(),
        })

        await self._storage.set(login=login, cookies=cookies)

    async def login_all(self, timeout_between_logins: Optional[float] = 1.0) -> None:
        """
        Login all accounts.
        """
        for login in list(self._accounts):
            await self.login_to_steam(login)
            if timeout_between_logins:
                await asyncio.sleep(timeout_between_logins)
