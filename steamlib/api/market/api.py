from pysteamauth.auth import Steam
from pysteamauth.errors import UnauthorizedSteamRequestError

from steamlib.api.market.schemas import PriceHistoryResponse


class SteamMarket:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def is_market_available(self) -> bool:
        """
        Is market available.
        """
        url = 'https://steamcommunity.com/market/'

        response: str = await self.steam.request(
            url=url,
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                'Upgrade-Insecure-Requests': '1',
            },
            cookies={
                'Steam_Language': 'english',
            },
        )
        if str(self.steam.steamid) not in response:
            raise UnauthorizedSteamRequestError(f'Unauthorized request to "{url}"')

        return 'The Market is unavailable for the following reason(s):' not in response

    async def price_history(self, appid: str, market_hash_name: str) -> PriceHistoryResponse:
        """
        Price history.
        """
        url = 'https://steamcommunity.com/market/pricehistory/'

        response: str = await self.steam.request(
            url=url,
            params={
                'country': 'US',
                'currency': '1',
                'appid': appid,
                'market_hash_name': market_hash_name,
            },
        )
        if response == '[]':
            raise UnauthorizedSteamRequestError(f'Unauthorized request to "{url}"')

        return PriceHistoryResponse.parse_raw(response)
