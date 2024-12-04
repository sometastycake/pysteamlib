from typing import List, Optional

from pydantic import BaseModel, Field


class Asset(BaseModel):
    appid: str
    contextid: str
    amount: int = 1
    assetid: str = Field(regex=r'^\d+$')


class SendOfferRequest(BaseModel):
    partner: int = Field(description='Steam id to whom we send exchange')
    tradelink: str
    me: List[Asset] = Field(description='Items that we transfer')
    them: List[Asset] = Field(description='Items we receive')
    tradeoffermessage: str = ''


class MobileConfirmation(BaseModel):
    type: int
    type_name: str
    confirmation_id: int = Field(alias='id')
    creator_id: int
    confirmation_key: int = Field(alias='nonce')
    creation_time: int
    cancel: str
    accept: str
    icon: str
    multi: bool
    headline: Optional[str] = None
    summary: List[str] = []

    class Config:
        allow_population_by_field_name = True


class GetMobileConfirmationResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    detail: Optional[str] = None
    conf: List[MobileConfirmation] = []
