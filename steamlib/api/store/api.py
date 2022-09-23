import json

from pysteamauth.auth import Steam

from steamlib.api.store.purchase.api import PurchaseGame
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

    async def purchase_game(self, game: str, appid: int) -> None:
        """
        Purchage game.
        """
        await PurchaseGame(self.steam, game, appid).purchase()
