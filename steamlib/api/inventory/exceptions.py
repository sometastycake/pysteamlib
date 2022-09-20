class InventoryError(Exception):

    def __init__(self, steamid: int, appid: str):
        self.steamid = steamid
        self.appid = appid

    def __str__(self) -> str:
        return str({
            'appid': self.appid,
            'steamid': self.steamid,
        })


class NullInventoryError(InventoryError):
    ...


class PrivateInventoryError(InventoryError):
    ...


class UnknownInventoryError(InventoryError):
    ...
