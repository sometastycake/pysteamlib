import json
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator
from yarl import URL


class Asset(BaseModel):
    appid: str
    contextid: str
    amount: int = 1
    assetid: str = Field(regex=r'^\d+$')


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

    @validator('trade_offer_access_token', pre=True)
    def _trade_offer_access_token(cls, trade_offer_access_token: str) -> str:  # noqa:U100
        if not trade_offer_access_token:
            raise RuntimeError('Trade offer access token is empty')
        return trade_offer_access_token


class SendOfferRequest(BaseModel):
    captcha: str = ''
    serverid: str = '1'
    partner: int = Field(description='User to whom we send the exchange')
    json_tradeoffer: JsonTradeoffer = Field(description='Tradeoffer items')
    tradeoffermessage: str = ''
    sessionid: str = Field(description='Sessionid cookie value')
    trade_offer_create_params: TradeOfferParams = Field(
        description='Trade link token of the user to whom we are sending the exchange',
    )

    @validator('json_tradeoffer')
    def _json_tradeoffer(cls, json_tradeoffer: JsonTradeoffer) -> JsonTradeoffer:  # noqa:U100
        if not json_tradeoffer.me.assets and not json_tradeoffer.them.assets:
            raise RuntimeError('Empty trade offer')
        return json_tradeoffer

    def tradelink(self, partner_id: int) -> str:
        params = {
            'partner': str(partner_id),
            'token': self.trade_offer_create_params.trade_offer_access_token,
        }
        return str(URL('https://steamcommunity.com/tradeoffer/new/').with_query(params))

    def to_request(self) -> Dict:
        data = self.dict()
        data['json_tradeoffer'] = json.dumps(data['json_tradeoffer'])
        data['trade_offer_create_params'] = json.dumps(data['trade_offer_create_params'])
        return data


class SendOfferResponse(BaseModel):
    tradeofferid: int
    needs_mobile_confirmation: Optional[bool]
    needs_email_confirmation: Optional[bool]
    email_domain: Optional[str]


class AcceptOfferResponse(BaseModel):
    tradeid: Optional[int]
    needs_mobile_confirmation: Optional[bool]
    needs_email_confirmation: Optional[bool]
    email_domain: Optional[str]


class MobileConfirmation(BaseModel):
    confirmation_id: int
    confirmation_key: int
    tradeofferid: int
