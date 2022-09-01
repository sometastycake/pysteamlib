import base64
import time
from typing import Optional

import rsa
from pydantic import BaseModel, Field, validator


class Authenticator(BaseModel):
    shared_secret: str
    device_id: str
    identity_secret: str


class RSA(BaseModel):
    success: bool
    publickey_mod: Optional[str]
    publickey_exp: Optional[str]
    timestamp: Optional[int]
    token_gid: Optional[str]

    def encrypt_password(self, password: str) -> str:
        publickey_exp = int(self.publickey_exp, 16)  # type:ignore
        publickey_mod = int(self.publickey_mod, 16)  # type:ignore
        public_key = rsa.PublicKey(
            n=publickey_mod,
            e=publickey_exp,
        )
        encrypted_password = rsa.encrypt(
            message=password.encode('ascii'),
            pub_key=public_key,
        )
        return str(base64.b64encode(encrypted_password), 'utf8')


class OAuth(BaseModel):
    steamid: int
    account_name: str
    oauth_token: str
    wgtoken: str
    wgtoken_secure: str


class LoginResult(BaseModel):
    success: bool
    requires_twofactor: bool
    message: Optional[str]
    oauth: Optional[OAuth]
    login_complete: Optional[bool]
    captcha_needed: Optional[bool]
    captcha_gid: Optional[str]

    @property
    def captcha_url(self) -> str:
        return f'https://steamcommunity.com/login/rendercaptcha/?gid={self.captcha_gid}'

    def steam_login(self) -> str:
        if not self.oauth:
            raise ValueError('Not found OAuth data')
        return f'{self.oauth.steamid}%7C%7C{self.oauth.wgtoken}'

    def steam_login_secure(self) -> str:
        if not self.oauth:
            raise ValueError('Not found OAuth data')
        return f'{self.oauth.steamid}%7C%7C{self.oauth.wgtoken_secure}'

    @validator('oauth', pre=True)
    def _oauth(cls, value: Optional[str]) -> Optional[OAuth]:
        if not value:
            return None
        return OAuth.parse_raw(value)

    def is_credentials_incorrect(self) -> bool:
        if self.success or not self.message:
            return False
        msg = 'The account name or password that you have entered is incorrect'
        return msg in self.message

    def is_too_many_authorizations(self) -> bool:
        if self.success or not self.message:
            return False
        msg = 'There have been too many login failures from your network in a short time period.'
        return msg in self.message


class SteamAuthorizationStatus(BaseModel):
    logged_in: bool
    steamid: str
    accountid: int
    account_name: str
    token: str


class LoginRequest(BaseModel):
    donotcache: int = Field(default_factory=time.time)
    password: str
    username: str
    twofactorcode: str = ''
    emailauth: str = ''
    loginfriendlyname: str = '#login_emailauth_friendlyname_mobile'
    emailsteamid: str = ''
    rsatimestamp: int
    remember_login: str = '1'
    tokentype: str = '-1'
    captchagid: str = '-1'
    captcha_text: str = ''
    oauth_client_id: str = 'DE45CD61'
    oauth_scope: str = 'read_profile write_profile read_client write_client'


class MobileConfirmation(BaseModel):
    confirmation_id: int
    confirmation_key: int
    tradeofferid: int


class ServerTime(BaseModel):
    server_time: int
    skew_tolerance_seconds: int
    large_time_jink: int
    probe_frequency_seconds: int
    adjusted_time_probe_frequency_seconds: int
    hint_probe_frequency_seconds: int
    sync_timeout: int
    try_again_seconds: int
    max_attempts: int


class ServerTimeResponse(BaseModel):
    response: ServerTime


class AccountData(BaseModel):
    password: str
    steamid: int
    authenticator: Optional[Authenticator]
