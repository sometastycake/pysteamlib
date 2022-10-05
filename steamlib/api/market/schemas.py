from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class Sale(BaseModel):
    sale: datetime = Field(description='Date of sale')
    price: Decimal = Field(description='Sale price')
    weight: int = Field(description='Amount of sold items')


class PriceHistoryResponse(BaseModel):
    success: bool
    price_prefix: str
    price_suffix: str
    prices: Optional[List[Sale]]

    @validator('prices', pre=True)
    def _prices(cls, value) -> Optional[List]:  # noqa:U100
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
