import time
from logging import getLogger
from typing import Any, Optional, Type, TypeVar

from config import config
from pydantic import BaseModel
from session import Session
from steam.captcha import AntigateCaptchaSolver
from steam.decorators import repeat_login

from core.steam.errors import (
    CaptchaGidNotFound,
    GetRsaError,
    IncorrectCredentials,
    LoginError,
    NotFoundAntigateApiKey,
    WrongCaptcha,
)
from core.steam.schemas import LoginRequest, LoginResult, SteamAuthorizationStatus, SteamRSA
from core.steam.storage.abstract import CookieStorage

StorageType = TypeVar('StorageType', bound=CookieStorage)
ResponseModelType = TypeVar('ResponseModelType', bound=BaseModel)


class Steam(Session):
    """
    Steam Authorization class.
    It works only for accounts without Steam Guard (2FA).
    """
    def __init__(self, login: str, password: str, storage: Type[StorageType]):
        """
        Steam Authorization.

        :param login: Steam login.
        :param password: Steam password.
        :param storage: Cookie storage.
        """
        super().__init__()
        self.logger = getLogger(__name__)
        self.login = login
        self.password = password
        self.storage = storage(self.login)

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
            return False

        if result.is_wrong_captcha():
            raise WrongCaptcha(login=self.login)

        if not result.success:
            raise LoginError(login=self.login)

        self.logger.debug('Login is success %s' % self.login)

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
