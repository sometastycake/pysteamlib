from steam._api.account.api import SteamAccount  # noqa
from steam._api.inventory.api import SteamInventory  # noqa
from steam._api.market.api import SteamMarket  # noqa
from steam._api.public.api import SteamPublic  # noqa
from steam._api.store.api import SteamStore  # noqa
from steam._api.support.api import SteamSupport  # noqa
from steam._api.trade.api import SteamTrade  # noqa
from steam.auth.steam import Steam


class SteamAPI:

    def __init__(self, steam: Steam):
        self.steam = steam
        self._account = SteamAccount(steam)
        self._inventory = SteamInventory()
        self._market = SteamMarket(steam)
        self._public = SteamPublic()
        self._store = SteamStore(steam)
        self._support = SteamSupport(steam)
        self._trade = SteamTrade(steam, self._account)

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
    def public(self) -> SteamPublic:
        return self._public

    @property
    def store(self) -> SteamStore:
        return self._store

    @property
    def support(self) -> SteamSupport:
        return self._support

    @property
    def trade(self) -> SteamTrade:
        return self._trade
