from typing import List

from pydantic import BaseModel


class AuthenticatorData(BaseModel):
    shared_secret: str


class SteamAuthorizationStatus(BaseModel):
    logged_in: bool
    steamid: str
    accountid: int
    account_name: str
    token: str


class TransferParams(BaseModel):
    nonce: str
    auth: str


class TransferInfoItem(BaseModel):
    url: str
    params: TransferParams


class FinalizeLoginStatus(BaseModel):
    steamID: str
    redir: str
    transfer_info: List[TransferInfoItem]
    primary_domain: str
