import json

from steam.api.trade.errors import SteamNullResponseError
from steam.api.trade.schemas import SendOfferErrorResponse, SendOfferResponse
from steam.errors import STEAM_ERROR_CODES
from steam.exceptions import SteamError, UnknownSteamError


def send_offer_handler(response: str) -> SendOfferResponse:
    """
    Send offer handler.
    """
    if not response or response == 'null':
        raise SteamNullResponseError
    content = json.loads(response)
    if 'strError' in content:
        error = SendOfferErrorResponse.parse_obj(content)
        error.determine_error()
    else:
        return SendOfferResponse.parse_obj(content)


def cancel_offer_handler(response: str) -> None:
    """
    Cancel offer handler.
    """
    content = json.loads(response)
    if 'success' in content:
        error = content['success']
        if error in STEAM_ERROR_CODES:
            raise SteamError(error_code=error)
        raise UnknownSteamError


def decline_offer_handler(response: str) -> None:
    """
    Decline offer handler.
    """
    content = json.loads(response)
    if 'success' in content:
        error = content['success']
        if error in STEAM_ERROR_CODES:
            raise SteamError(error_code=error)
        raise UnknownSteamError
