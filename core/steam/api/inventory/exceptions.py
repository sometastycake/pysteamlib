class InventoryError(Exception):
    ...


class UnknownInventoryError(InventoryError):
    ...


class PrivateInventoryError(InventoryError):
    ...
