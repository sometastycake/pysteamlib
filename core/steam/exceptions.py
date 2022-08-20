from steam.errors import STEAM_ERROR_CODES


class SteamError(Exception):

    def __init__(self, error_code: int):
        self.error_code = error_code

    def __str__(self) -> str:
        return f'Error code "{STEAM_ERROR_CODES[self.error_code]}"'


class UnknownSteamError(Exception):
    ...
