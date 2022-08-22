import base64
import binascii
import hashlib
import hmac
import math
import time
from struct import pack
from typing import Any, Optional, Type, TypeVar

from config import config
from pydantic import BaseModel
from session import Session
from steam.api.public.api import SteamAPI
from steam.auth.captcha import AntigateCaptchaSolver
from steam.auth.exceptions import (
    CaptchaGidNotFound,
    GetRsaError,
    IncorrectCredentials,
    LoginError,
    NotFoundAntigateApiKey,
    NotFoundAuthenticatorData,
    WrongCaptcha,
)
from steam.auth.schemas import AuthenticatorData, LoginRequest, LoginResult, SteamAuthorizationStatus, SteamRSA
from steam.auth.storage import BaseStorage

from core.steam.storage.abstract import CookieStorage

StorageType = TypeVar('StorageType', bound=CookieStorage)
ResponseModelType = TypeVar('ResponseModelType', bound=BaseModel)


class Steam(Session):
    """
    Steam authorization class.
    """
    steam_guard_codes = [
        50, 51, 52, 53, 54, 55, 56, 57, 66, 67, 68, 70, 71,
        72, 74, 75, 77, 78, 80, 81, 82, 84, 86, 87, 88, 89,
    ]

    def __init__(
        self,
        login: str,
        password: str,
        storage: Type[StorageType] = BaseStorage,
        authenticator: Optional[AuthenticatorData] = None,
    ):
        """
        Steam authorization.

        :param login: Steam login.
        :param password: Steam password.
        :param storage: Cookie storage.
        :param authenticator: Steam authenticator data.
        """
        self.login = login
        self.password = password
        self.storage = storage(self.login)
        self.authenticator = authenticator

    async def sessionid(self) -> str:
        """
        Sessionid cookie.
        """
        return (await self.storage.get())['sessionid']

    async def request(
            self,
            url: str,
            method: str = 'GET',
            response_model: Optional[Type[ResponseModelType]] = None,
            **kwargs: Any,
    ) -> Any:
        """
        Request with Steam session.
        """
        response = await self.session.request(
            url=url,
            method=method,
            cookies=await self.storage.get(),
            **kwargs,
        )
        if response_model is not None:
            return response_model.parse_raw(await response.text())
        return await response.text()

    async def is_authorized(self) -> bool:
        """
        Is alive authorization.
        """
        response = await self.request(
            url='https://steamcommunity.com/chat/clientjstoken',
            response_model=SteamAuthorizationStatus,
        )
        return response.logged_in

    async def getrsakey(self) -> SteamRSA:
        """
        Getting data for password encryption.
        """
        return await self.request(
            method='POST',
            url='https://steamcommunity.com/login/getrsakey/',
            data={
                'donotcache': int(time.time()),
                'username': self.login,
            },
            response_model=SteamRSA,
        )

    async def do_login(self, request: LoginRequest) -> LoginResult:
        """
        Authorization request.
        """
        return await self.request(
            method='POST',
            url='https://steamcommunity.com/login/dologin/',
            data=request.dict(),
            response_model=LoginResult,
        )

    @classmethod
    async def get_steam_guard(cls, shared_secret: str) -> str:
        """
        Calculating Steam Guard code.
        """
        server_time = (await SteamAPI.server_time()).response.server_time

        data = binascii.unhexlify(
            hmac.new(
                key=base64.b64decode(shared_secret),
                msg=pack('!L', 0) + pack('!L', math.floor(server_time // 30)),
                digestmod=hashlib.sha1,
            ).hexdigest(),
        )

        value = data[19] & 0xF
        code_point = (
            (data[value] & 0x7F) << 24 |       # noqa:W504
            (data[value + 1] & 0xFF) << 16 |   # noqa:W504
            (data[value + 2] & 0xFF) << 8 |    # noqa:W504
            (data[value + 3] & 0xFF)
        )

        code = ''
        for _ in range(5):
            code += chr(cls.steam_guard_codes[code_point % len(cls.steam_guard_codes)])
            code_point //= len(cls.steam_guard_codes)

        return code

    async def _login(self, request: LoginRequest):
        """
        Authorization.
        """
        result = await self.do_login(request)
        for _ in range(3):
            if result.success:
                return
            if result.is_credentials_incorrect():
                raise IncorrectCredentials

            if result.captcha_needed:
                if not result.captcha_gid:
                    raise CaptchaGidNotFound

                if not config.antigate_api_key:
                    raise NotFoundAntigateApiKey

                request.captcha_text = await AntigateCaptchaSolver().solve(result.captcha_url)
                request.captchagid = result.captcha_gid

            elif result.requires_twofactor:
                if not self.authenticator:
                    raise NotFoundAuthenticatorData
                request.twofactorcode = await Steam.get_steam_guard(
                    shared_secret=self.authenticator.shared_secret,
                )

            result = await self.do_login(request)

        if not result.success:
            if result.is_wrong_captcha():
                raise WrongCaptcha
            raise LoginError(result.message)

    async def login_to_steam(self) -> None:
        """
        Login to Steam.
        """
        if await self.is_authorized():
            return

        keys = await self.getrsakey()
        if not keys.success:
            raise GetRsaError

        request = LoginRequest(
            donotcache=int(time.time()),
            password=keys.encrypt_password(self.password),
            username=self.login,
            rsatimestamp=keys.timestamp,
        )

        await self._login(request)
        await self.storage.set(self.get_cookies('steamcommunity.com'))
