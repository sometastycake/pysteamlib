from pysteamauth.auth import Steam

from steamlib.api.store.purchase import TransactionStatusResponse
from steamlib.api.store.purchase.api import PurchaseGame


class SteamStore:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def purchase_game(self, appid: str) -> TransactionStatusResponse:
        return await PurchaseGame(self.steam, appid).purchase()
