from steam.api.account.api import SteamAccount
from steam.api.inventory.api import SteamInventory
from steam.api.market.api import SteamMarket
from steam.api.store.api import SteamStore
from steam.api.support.api import SteamSupport
from steam.api.trade.api import SteamTrade
from steam.auth.steam import Steam


class SteamAPI:

    def __init__(self, steam: Steam):
        self._account = SteamAccount(steam)
        self._inventory = SteamInventory(steam)
        self._market = SteamMarket(steam)
        self._store = SteamStore(steam)
        self._support = SteamSupport(steam)
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
    def support(self) -> SteamSupport:
        return self._support

    @property
    def trade(self) -> SteamTrade:
        return self._trade
