from typing import TypeVar

from steam.errors import STEAM_ERROR_CODES
from steam.exceptions import SteamError, UnknownSteamError
from steam.schemas import BaseSteamResponse

BaseSteamResponseType = TypeVar('BaseSteamResponseType', bound=BaseSteamResponse)


def _check_steam_error(error: int) -> None:
    if error in (1, 22):
        return
    if error in STEAM_ERROR_CODES:
        raise SteamError(error_code=error)
    raise UnknownSteamError(error_code=error)


def _check_steam_error_from_response(response: BaseSteamResponseType) -> None:
    error = response.success
    if error in (1, 22):
        return
    if error in STEAM_ERROR_CODES:
        raise SteamError(error_code=error, error_msg=response.errmsg)
    raise UnknownSteamError(error_code=error)
