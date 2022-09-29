from pysteamauth.auth import Steam

from steamlib.api.account.api import SteamAccount
from steamlib.api.inventory.api import SteamInventory
from steamlib.api.market.api import SteamMarket
from steamlib.api.store.api import SteamStore
from steamlib.api.trade.api import SteamTrade


class SteamAPI:

    def __init__(self, steam: Steam):
        self._account = SteamAccount(steam)
        self._inventory = SteamInventory(steam)
        self._market = SteamMarket(steam)
        self._store = SteamStore(steam)
        self._trade = SteamTrade(steam)

    @property
    def account(self) -> SteamAccount:
        return self._account

    @property
    def inventory(self) -> SteamInventory:
        return self._inventory

    @property
    def market(self) -> SteamMarket:
        return self._market

    @property
    def store(self) -> SteamStore:
        return self._store

    @property
    def trade(self) -> SteamTrade:
        return self._trade
