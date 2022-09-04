import json

from steam.api.trade.exceptions import SteamNullResponseError
from steam.api.trade.schemas import SendOfferResponse, SteamOfferError
from steam.errors.codes import STEAM_ERROR_CODES
from steam.errors.exceptions import SteamError, UnknownSteamError


def send_offer_response_handler(response: str) -> SendOfferResponse:
    """
    Send offer handler.
    """
    if not response or response == 'null':
        raise SteamNullResponseError
    content = json.loads(response)
    if 'strError' in content:
        error = SteamOfferError.parse_obj(content)
        error.determine_error()
        error.determine_error_code()
        raise UnknownSteamError(content['strError'])
    else:
        return SendOfferResponse.parse_obj(content)


def cancel_offer_response_handler(response: str) -> None:
    """
    Cancel offer handler.
    """
    content = json.loads(response)
    if 'success' in content:
        error = content['success']
        if error in STEAM_ERROR_CODES:
            raise SteamError(error_code=error)
        raise UnknownSteamError(error_code=error)


def decline_offer_response_handler(response: str) -> None:
    """
    Decline offer handler.
    """
    content = json.loads(response)
    if 'success' in content:
        error = content['success']
        if error in STEAM_ERROR_CODES:
            raise SteamError(error_code=error)
        raise UnknownSteamError(error_code=error)


def accept_offer_response_handler(response: str) -> int:
    """
    Accept offer handler.
    """
    content = json.loads(response)
    if 'strError' in content:
        error = SteamOfferError.parse_obj(content)
        error.determine_error_code()
        raise UnknownSteamError(content['strError'])
    else:
        return content['tradeid']
