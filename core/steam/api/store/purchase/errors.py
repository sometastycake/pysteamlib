class GamePurchaseError(Exception):
    """Game purchase error."""


class NotEnoughFundsForGame(GamePurchaseError):
    """Not enough funds for game."""


class NotSpecifiedGame(GamePurchaseError):
    """The game is not indicated when buying."""
