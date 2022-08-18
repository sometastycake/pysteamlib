from steam.steam import Steam


class SteamMarketApi:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def is_market_available(self) -> bool:
        response = await self.steam.request(
            url='https://steamcommunity.com/market/',
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
                'Upgrade-Insecure-Requests': '1',
            },
        )
        return 'The Market is unavailable for the following reason(s):' not in response
