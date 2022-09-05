import json
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from yarl import URL


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


class MobileConfirmation(BaseModel):
    confirmation_id: int
    confirmation_key: int
    tradeofferid: int
