from typing import TypeVar

from steam.errors import STEAM_ERROR_CODES
from steam.exceptions import SteamError, UnknownSteamError
from steam.schemas import BaseSteamResponse

BaseSteamResponseType = TypeVar('BaseSteamResponseType', bound=BaseSteamResponse)


def check_steam_error_from_response(response: BaseSteamResponseType) -> BaseSteamResponseType:
    """
    Check steam response status.

    :param response: Steam response status.
    :return: Steam response.
    """
    error = response.success
    if error in (1, 22):
        return response
    if error in STEAM_ERROR_CODES:
        raise SteamError(error_code=error)
    raise UnknownSteamError(f'Unknown Steam error: "{error}"')
