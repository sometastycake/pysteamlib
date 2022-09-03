from steam.api.market.schemas import PriceHistoryResponse
from steam.auth.steam import Steam


class SteamMarket:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def is_market_available(self, login: str) -> bool:
        """
        Is market available.
        """
        cookies = await self.steam.cookies(login)
        cookies.update({
            'Steam_Language': 'english',
        })
        response = await self.steam.http.request(
            url='https://steamcommunity.com/market/',
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                'Upgrade-Insecure-Requests': '1',
            },
            cookies=cookies,
        )
        return 'The Market is unavailable for the following reason(s):' not in response

    async def price_history(self, appid: str, market_hash_name: str, login: str) -> PriceHistoryResponse:
        """
        Price history.
        """
        response = await self.steam.http.request(
            url='https://steamcommunity.com/market/pricehistory/',
            params={
                'country': 'US',
                'currency': '1',
                'appid': appid,
                'market_hash_name': market_hash_name,
            },
            raise_for_status=False,
            cookies=await self.steam.cookies(login),
        )
        return PriceHistoryResponse.parse_raw(response)
