from decimal import Decimal

from pydantic import BaseModel


class GamePriceOverview(BaseModel):
    currency: str
    initial: Decimal
    final: Decimal
    discount_percent: Decimal
    initial_formatted: str
    final_formatted: str


class GamePriceData(BaseModel):
    price_overview: GamePriceOverview


class GamePrice(BaseModel):
    success: bool
    data: GamePriceData
