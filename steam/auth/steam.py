import asyncio
import base64
import binascii
import hashlib
import hmac
import math
import time
from logging import getLogger
from struct import pack
from typing import Dict, List, Optional, Tuple, Type, TypeVar

from bitstring import BitArray

from steam.abstract.captcha import CaptchaSolverAbstract
from steam.abstract.request import RequestStrategyAbstract
from steam.abstract.storage import CookieStorageAbstract
from steam.auth.exc import (
    AccountAlreadyExistsError,
    GetRsaError,
    IncorrectCredentialsError,
    LoginError,
    NotFoundAuthenticatorError,
    TooManyAuthorizationsError,
)
from steam.auth.schemas import (
    RSA,
    AccountData,
    Authenticator,
    LoginRequest,
    LoginResult,
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

    def __init__(
        self,
        cookie_storage: Type[CookieStorageType] = BaseCookieStorage,
        captcha_solver: Type[CaptchaSolverType] = BaseAntigateCaptchaSolver,
        request_strategy: Type[RequestStrategyAbstract] = BaseRequestStrategy,
    ):
        self._http = request_strategy()
        self._storage = cookie_storage()
        self._captcha_solver = captcha_solver()
        self._accounts: Dict[str, AccountData] = {}
        self._logger = getLogger(__name__)

    @property
    def accounts(self) -> List[str]:
        return list(self._accounts)

    @property
    def http(self) -> RequestStrategyAbstract:
        """Get request strategy object."""
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

    async def is_authorized(self, login: str) -> bool:
        """
        Is alive authorization.
        """
        response = await self._http.request(
            url='https://steamcommunity.com/chat/clientjstoken',
            cookies=await self._storage.get(login),
        )
        return SteamAuthorizationStatus.parse_raw(response).logged_in

    async def _getrsakey(self, login: str) -> RSA:
        """
        Getting data for password encryption.
        """
        response = await self._http.request(
            method='POST',
            url='https://steamcommunity.com/login/getrsakey/',
            data={
                'donotcache': int(time.time()),
                'username': login,
            },
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

    def get_confirmation_hash(self, server_time: int, identity_secret: str, tag: str = 'conf') -> str:
        """
        Get mobile confirmation hash.

        :return: Mobile confirmation hash.
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

    async def _login(self, request: LoginRequest, login: str) -> Tuple[LoginResult, Dict[str, str]]:
        """
        Authorization processing.

        :return: Authorization result and Steam cookies.
        """
        result, cookies = await self._do_login(request)

        for _ in range(3):
            if result.success:
                return result, cookies

            if result.is_credentials_incorrect():
                raise IncorrectCredentialsError(login=login)

            if result.is_too_many_authorizations():
                raise TooManyAuthorizationsError(login=login)

            if result.captcha_needed:
                self._logger.debug(f'Captcha needed to {login}')

                request.captcha_text = await self._captcha_solver(
                    link=result.captcha_url,
                )
                request.captchagid = result.captcha_gid

            if result.requires_twofactor:
                self._logger.debug(f'2FA needed to {login}')

                shared_secret = self.authenticator(login).shared_secret
                request.twofactorcode = await self.get_steam_guard(
                    shared_secret=shared_secret,
                )

            result, cookies = await self._do_login(request)

        if not result.success:
            raise LoginError(login=login, msg=result.message)

        return result, cookies

    async def _get_sessionid_from_steam(self) -> str:
        """
        Get sessionid cookie from Steam.

        :return: Sessionid cookie.
        """
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
            self._logger.debug(f'{login} already authorized in Steam')
            return

        sessionid = await self._get_sessionid_from_steam()

        keys = await self._getrsakey(login)
        if not keys.success:
            raise GetRsaError(login=login)

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

        await self._storage.set(
            login=login,
            cookies=cookies,
        )
        self._logger.debug(f'{login} is authorized')

    async def login_all(self, timeout_between_logins: Optional[float] = 5.0) -> None:
        """
        Login all accounts.
        """
        for login in self._accounts:
            self._logger.debug(f'Authorization {login}')
            await self.login_to_steam(login)
            if timeout_between_logins:
                await asyncio.sleep(timeout_between_logins)
