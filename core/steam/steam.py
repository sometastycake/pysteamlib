import base64
import binascii
import hashlib
import hmac
import math
import time
from logging import getLogger
from struct import pack
from typing import Any, Optional, Type, TypeVar

from config import config
from pydantic import BaseModel
from session import Session
from steam.api.public.api import SteamPublicAPI
from steam.captcha import AntigateCaptchaSolver
from steam.decorators import repeat_login

from core.steam.errors import (
    CaptchaGidNotFound,
    GetRsaError,
    IncorrectCredentials,
    NotFoundAntigateApiKey,
    NotFoundSharedSecret,
    WrongCaptcha,
)
from core.steam.schemas import LoginRequest, LoginResult, SteamAuthorizationStatus, SteamRSA
from core.steam.storage.abstract import CookieStorage

StorageType = TypeVar('StorageType', bound=CookieStorage)
ResponseModelType = TypeVar('ResponseModelType', bound=BaseModel)


class Steam(Session):
    """
    Steam Authorization class.
    """
    SGCodes = [
        50, 51, 52, 53, 54, 55, 56, 57, 66, 67, 68, 70, 71,
        72, 74, 75, 77, 78, 80, 81, 82, 84, 86, 87, 88, 89,
    ]

    def __init__(
            self,
            login: str,
            password: str,
            storage: Type[StorageType],
            shared_secret: Optional[str] = None,
    ):
        """
        Steam Authorization.

        :param login: Steam login.
        :param password: Steam password.
        :param storage: Cookie storage.
        :param shared_secret: Secret for Steam Guard generate.
        """
        super().__init__()
        self.logger = getLogger(__name__)
        self.login = login
        self.password = password
        self.storage = storage(self.login)
        self.public_api = SteamPublicAPI()
        self.shared_secret = shared_secret

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
            only_content: bool = True,
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
        if only_content:
            if response_model is not None:
                return response_model.parse_raw(await response.text())
            return await response.text()
        return response

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

    async def get_steam_guard(self) -> str:
        """
        Calculating Steam Guard code.
        """
        server_time = (await self.public_api.server_time()).response.server_time

        data = binascii.unhexlify(
            hmac.new(
                key=base64.b64decode(self.shared_secret),
                msg=pack('!L', 0) + pack('!L', math.floor(server_time // 30)),
                digestmod=hashlib.sha1,
            ).hexdigest(),
        )

        value = data[19] & 0xF
        code_point = (
            (data[value] & 0x7F) << 24 |
            (data[value + 1] & 0xFF) << 16 |
            (data[value + 2] & 0xFF) << 8 |
            (data[value + 3] & 0xFF)
        )

        code = ''
        for _ in range(5):
            code += chr(self.SGCodes[code_point % len(self.SGCodes)])
            code_point //= len(self.SGCodes)

        return code

    @repeat_login(retry=3)
    async def handle_do_login_request(self, request: LoginRequest) -> bool:
        """
        Authorization.
        """
        result = await self.do_login(request)

        if result.is_credentials_incorrect():
            raise IncorrectCredentials(login=self.login)

        if result.captcha_needed:
            self.logger.debug('Captcha needed %s' % self.login)

            if not result.captcha_gid:
                raise CaptchaGidNotFound(login=self.login)

            if not config.antigate_api_key:
                raise NotFoundAntigateApiKey(login=self.login)

            request.captcha_text = await AntigateCaptchaSolver(result.captcha_url).solve()
            request.captchagid = result.captcha_gid

        if result.requires_twofactor:
            if not self.shared_secret:
                raise NotFoundSharedSecret(login=self.login)
            request.twofactorcode = await self.get_steam_guard()

        if result.is_wrong_captcha():
            raise WrongCaptcha(login=self.login)

        return result.success

    async def login_to_steam(self) -> None:
        """
        Login to Steam.
        """
        self.logger.debug('Login to %s' % self.login)

        if await self.is_authorized():
            self.logger.debug('Account %s already authorized' % self.login)
            return

        keys = await self.getrsakey()
        if not keys.success:
            raise GetRsaError(login=self.login)

        await self.handle_do_login_request(
            request=LoginRequest(
                donotcache=str(int(time.time())),
                password=str(keys.encrypt_password(self.password), 'utf8'),
                username=self.login,
                captchagid='-1',
                captcha_text='',
                rsatimestamp=str(keys.timestamp),
            ),
        )
        await self.storage.set(self.get_cookies('steamcommunity.com'))
