from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, validator


class Sale(BaseModel):
    sale: datetime
    price: Decimal
    weight: int


class PriceHistoryResponse(BaseModel):
    success: bool
    price_prefix: str
    price_suffix: str
    prices: Optional[List[Sale]]

    @validator('prices', pre=True)
    def _prices(cls, value) -> Optional[List]:
        if not value:
            return None
        prices = []
        for date_of_sale, price, weight in value:
            prices.append(
                Sale(
                    sale=datetime.strptime(date_of_sale.split(':')[0], '%b %d %Y %H'),
                    price=price,
                    weight=weight,
                ),
            )
        return prices


class Appid(BaseModel):
    appid: int
    name: str


class Applist(BaseModel):
    apps: List[Appid]


class ApplistResponse(BaseModel):
    applist: Applist

    @validator('applist')
    def _applist(cls, value: Applist) -> Applist:
        appid_by_name = {}
        for appid in value.apps:
            if appid.name:
                appid_by_name[appid.name] = appid.appid
        setattr(cls, 'appid_by_name', appid_by_name)
        return value

    def get_appid_by_name(self, name: str) -> int:
        return getattr(self, 'appid_by_name')[name]
