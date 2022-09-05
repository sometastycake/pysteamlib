import json
import re
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from yarl import URL

from steam.api.trade.exceptions import (
    AccountOverflowError,
    ProfileSettingsError,
    SteamServerDownError,
    TradeBanError,
    TradelinkError,
    TradeOffersLimitError,
)
from steam.errors.codes import STEAM_ERROR_CODES
from steam.errors.exceptions import SteamError


class Asset(BaseModel):
    appid: str = Field(description='Appid of Steam game')
    contextid: str
    amount: int = 1
    assetid: str = Field(description='Assetid of item')


class Me(BaseModel):
    assets: List[Asset] = []
    currency: List = []
    ready: bool = False


class Them(BaseModel):
    assets: List[Asset] = []
    currency: List = []
    ready: bool = False


class JsonTradeoffer(BaseModel):
    newversion: bool = True
    version: int = 2
    me: Me = Me()
    them: Them = Them()


class TradeOfferParams(BaseModel):
    trade_offer_access_token: str = Field(description='User tradelink token')


class SendOfferRequest(BaseModel):
    captcha: str = ''
    serverid: str = '1'
    partner: int = Field(description='User to whom we send the exchange')
    json_tradeoffer: JsonTradeoffer
    tradeoffermessage: str = ''
    sessionid: str
    trade_offer_create_params: TradeOfferParams = Field(
        description='Trade link token of the user to whom we are sending the exchange',
    )

    def tradelink(self) -> str:
        """
        Get user tradelink.
        """
        params = {
            'partner': str(self.partner - 76561197960265728),
            'token': self.trade_offer_create_params.trade_offer_access_token,
        }
        return str(URL('https://steamcommunity.com/tradeoffer/new/').with_query(params))

    def to_request(self) -> Dict:
        """
        Prepare data to request.
        """
        data = self.dict()
        data['json_tradeoffer'] = json.dumps(data['json_tradeoffer'])
        data['trade_offer_create_params'] = json.dumps(data['trade_offer_create_params'])
        return data


class SendOfferResponse(BaseModel):
    tradeofferid: int
    needs_mobile_confirmation: Optional[bool]
    needs_email_confirmation: Optional[bool]
    email_domain: Optional[str]


class SteamOfferError(BaseModel):
    strError: str

    def determine_error_code(self) -> None:
        error = re.search(
            pattern=r'. \((\d+)\)',
            string=self.strError,
        )
        if error and error.groups():
            code = int(error.group(1))
            if code in STEAM_ERROR_CODES:
                raise SteamError(error_code=code)

    def determine_error(self) -> None:
        errors = {
            'Trade URL is no longer valid': TradelinkError,
            'is not available to trade': ProfileSettingsError,
            'they have a trade ban': TradeBanError,
            'maximum number of items': AccountOverflowError,
            'sent too many trade offers': TradeOffersLimitError,
            'server may be down': SteamServerDownError,
        }
        for error in errors:
            if error in self.strError:
                raise errors[error]


class MobileConfirmation(BaseModel):
    confirmation_id: int
    confirmation_key: int
    tradeofferid: int
