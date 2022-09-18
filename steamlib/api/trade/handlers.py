import json
import re

from pysteamauth.errors import UnknownSteamError, check_steam_error

from steamlib.api.trade.exceptions import (
    AccountOverflowError,
    ProfileSettingsError,
    SteamNullResponseError,
    SteamServerDownError,
    TradeBanError,
    TradelinkError,
    TradeOffersLimitError,
)
from steamlib.api.trade.schemas import SendOfferResponse


def determine_error_code(steam_error: str) -> None:
    error = re.search(
        pattern=r'. \((\d+)\)',
        string=steam_error,
    )
    if error and error.groups():
        code = int(error.group(1))
        check_steam_error(code)


def determine_error(steam_error: str) -> None:
    errors = {
        'Trade URL is no longer valid': TradelinkError,
        'is not available to trade': ProfileSettingsError,
        'they have a trade ban': TradeBanError,
        'maximum number of items': AccountOverflowError,
        'sent too many trade offers': TradeOffersLimitError,
        'server may be down': SteamServerDownError,
    }
    for error in errors:
        if error in steam_error:
            raise errors[error]


def send_offer_response_handler(response: str) -> SendOfferResponse:
    """
    Send offer handler.
    """
    if not response or response == 'null':
        raise SteamNullResponseError
    content = json.loads(response)
    if 'strError' in content:
        error = content['strError']
        determine_error(error)
        determine_error_code(error)
        raise UnknownSteamError(error_code=error)
    else:
        return SendOfferResponse.parse_obj(content)


def cancel_offer_response_handler(response: str) -> None:
    """
    Cancel offer handler.
    """
    content = json.loads(response)
    if 'success' in content:
        check_steam_error(error=content['success'])


def decline_offer_response_handler(response: str) -> None:
    """
    Decline offer handler.
    """
    content = json.loads(response)
    if 'success' in content:
        check_steam_error(error=content['success'])


def accept_offer_response_handler(response: str) -> int:
    """
    Accept offer handler.
    """
    content = json.loads(response)
    if 'strError' in content:
        error = content['strError']
        determine_error(error)
        determine_error_code(error)
        raise UnknownSteamError(error_code=error)
    else:
        return content['tradeid']
