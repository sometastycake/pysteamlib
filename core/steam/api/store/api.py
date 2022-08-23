from session import Session
from steam.api.store.schemas import GamePrice
from steam.auth.steam import Steam


class SteamStore(Session):

    def __init__(self, steam: Steam):
        super().__init__()
        self.steam = steam

    async def game_price(self, appid: str) -> GamePrice:
        """
        Get game price.

        :return: Game price.
        """
        response = await self.session.get(
            url='https://store.steampowered.com/api/appdetails',
            params={
                'appids': appid,
                'cc': 'us',
                'filters': 'price_overview',
            },
        )
        content = await response.json()
        return GamePrice.parse_obj(content[appid])
