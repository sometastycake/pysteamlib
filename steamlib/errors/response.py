from typing import TypeVar

from pysteamauth.errors import STEAM_ERROR_CODES, SteamError, UnknownSteamError

from steamlib.schemas import BaseSteamResponse

BaseSteamResponseType = TypeVar('BaseSteamResponseType', bound=BaseSteamResponse)


def check_steam_error_from_response(response: BaseSteamResponseType) -> None:
    error = response.success
    if error in (1, 22):
        return
    if error in STEAM_ERROR_CODES:
        raise SteamError(error_code=error, error_msg=response.errmsg)
    raise UnknownSteamError(error_code=error)
