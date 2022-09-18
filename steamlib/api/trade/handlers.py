import json
import re

from pysteamauth.errors import UnknownSteamError, check_steam_error

from steamlib.api.trade.enums import OfferState
from steamlib.api.trade.exceptions import (
    AccountOverflowError,
    ProfileSettingsError,
    SteamNullResponseError,
    SteamServerDownError,
    TradeBanError,
    TradelinkError,
    TradeOffersLimitError,
)
from steamlib.api.trade.schemas import AcceptOfferResponse, SendOfferResponse


class OfferResponseHandler:

    def __init__(self, response: str, offer_state: OfferState):
        self.offer_state = offer_state
        self.response = response

    def _determine_error_code(self, steam_error: str) -> None:
        error = re.search(
            pattern=r'. \((\d+)\)',
            string=steam_error,
        )
        if error and error.groups():
            code = int(error.group(1))
            check_steam_error(code)

    def _determine_error(self, steam_error: str) -> None:
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

    def check_error(self) -> None:
        """
        Error response check.
        """
        if not self.response or self.response == 'null':
            raise SteamNullResponseError

        data = json.loads(self.response)

        if self.offer_state in (OfferState.send, OfferState.accept) and 'strError' in data:
            error = data['strError']
            self._determine_error(error)
            self._determine_error_code(error)
            raise UnknownSteamError(error_code=error)

        if self.offer_state in (OfferState.cancel, OfferState.decline) and 'success' in data:
            check_steam_error(error=data['success'])

    def send_offer(self) -> SendOfferResponse:
        self.check_error()
        return SendOfferResponse.parse_raw(self.response)

    def accept_offer(self) -> AcceptOfferResponse:
        self.check_error()
        return AcceptOfferResponse.parse_raw(self.response)

    def decline_offer(self) -> None:
        return self.check_error()

    def cancel_offer(self) -> None:
        return self.check_error()
