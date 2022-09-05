from typing import Optional

from steam.errors.codes import STEAM_ERROR_CODES


class SteamError(Exception):

    def __init__(self, error_code: int, error_msg: Optional[str] = None):
        self.error_msg = error_msg
        self.error_code = error_code

    def __str__(self) -> str:
        return str({
            'error': STEAM_ERROR_CODES[self.error_code] if self.error_code in STEAM_ERROR_CODES else self.error_code,
            'msg': self.error_msg,
        })


class UnknownSteamError(SteamError):
    ...


class SteamWrongHttpStatusError(Exception):

    def __init__(self, http_status: int):
        self.http_status = http_status

    def __str__(self) -> str:
        return str({
            'msg': 'Wrong HTTP status from Steam',
            'http_status': self.http_status,
        })


class TooManySteamRequestsError(SteamWrongHttpStatusError):
    def __init__(self, http_status: int = 429):
        self.http_status = http_status


class UnauthorizedSteamRequestError(Exception):

    def __init__(self, url):
        self.url = url

    def __str__(self) -> str:
        return f'Unauthorized request to "{self.url}"'
