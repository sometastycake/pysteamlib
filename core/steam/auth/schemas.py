import base64
from typing import Optional

import rsa
from pydantic import BaseModel, Field


class AuthenticatorData(BaseModel):
    shared_secret: str


class SteamRSA(BaseModel):
    success: bool
    publickey_mod: Optional[str]
    publickey_exp: Optional[str]
    timestamp: Optional[int]
    token_gid: Optional[str]

    def encrypt_password(self, password: str) -> bytes:
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
        return base64.b64encode(encrypted_password)


class LoginResult(BaseModel):
    success: bool
    requires_twofactor: bool
    message: Optional[str]
    clear_password_field: Optional[bool]
    captcha_needed: Optional[bool]
    captcha_gid: Optional[str]

    def is_credentials_incorrect(self) -> bool:
        if self.success or not self.message:
            return False
        msg = 'The account name or password that you have entered is incorrect'
        return msg in self.message

    def is_wrong_captcha(self) -> bool:
        if self.success or not self.message:
            return False
        msg = 'Please verify your humanity by re-entering the characters in the captcha.'
        return msg in self.message

    @property
    def captcha_url(self) -> str:
        return f'https://steamcommunity.com/login/rendercaptcha/?gid={self.captcha_gid}'


class SteamAuthorizationStatus(BaseModel):
    logged_in: bool
    steamid: str
    accountid: int
    account_name: str
    token: str


class LoginRequest(BaseModel):
    donotcache: int
    password: str
    username: str
    twofactorcode: str = Field(default='')
    emailauth: str = Field(default='')
    loginfriendlyname: str = Field(default='#login_emailauth_friendlyname_mobile')
    captchagid: str
    captcha_text: str
    emailsteamid: str = Field(default='')
    rsatimestamp: int
    remember_login: str = Field(default='0')
    tokentype: str = Field(default='-1')
    oauth_scope: str = Field(default='read_profile write_profile read_client write_client')
