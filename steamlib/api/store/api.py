import json

from pysteamauth.auth import Steam

from steamlib.api.store.schemas import GamePrice


class SteamStore:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def game_price(self, appid: str) -> GamePrice:
        """
        Get game price.

        :return: Game price.
        """
        response = await self.steam.request(
            url='https://store.steampowered.com/api/appdetails',
            params={
                'appids': appid,
                'cc': 'us',
                'filters': 'price_overview',
            },
        )
        content = json.loads(response)
        return GamePrice.parse_obj(content[appid])
