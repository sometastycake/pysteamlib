from pysteamauth.auth import Steam

from .schemas import PriceHistoryResponse


class SteamMarket:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def is_market_available(self) -> bool:
        response: str = await self.steam.request(
            url='https://steamcommunity.com/market/',
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.9.5.20) Gecko/2812-12-10 04:56:28 Firefox/3.8',
            },
            cookies={
                'Steam_Language': 'english',
            },
        )
        return 'The Market is unavailable for the following reason(s):' not in response

    async def price_history(self, appid: str, market_hash_name: str) -> PriceHistoryResponse:
        response: str = await self.steam.request(
            url='https://steamcommunity.com/market/pricehistory/',
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.9.5.20) Gecko/2812-12-10 04:56:28 Firefox/3.8',
            },
            params={
                'country': 'US',
                'currency': '1',
                'appid': appid,
                'market_hash_name': market_hash_name,
            },
        )
        return PriceHistoryResponse.parse_raw(response)
