import json
import re
from typing import Dict

from pysteamauth.errors import check_steam_error

from .exceptions import (
    AccountOverflowError,
    ProfileSettingsError,
    SteamServerDownError,
    TradeBanError,
    TradelinkError,
    TradeOffersLimitError,
)
from .schemas import AcceptOfferResponse, SendOfferResponse


class OfferResponseHandler:

    # Errors when sending an exchange
    errors = [
        ('Trade URL is no longer valid', TradelinkError, 'Trade URL is no longer valid'),
        ('is not available to trade', ProfileSettingsError, 'Account is not available for trade offers'),
        ('they have a trade ban', TradeBanError, 'User has a trade ban'),
        ('maximum number of items', AccountOverflowError, 'Maximum number of items per account'),
        ('sent too many trade offers', TradeOffersLimitError, 'Too many exchange offers have been sent'),
        ('server may be down', SteamServerDownError, 'Steam server may be down'),
    ]

    def __init__(self, response: str):
        self.response = response

    def _determine_error_code(self, steam_error: str) -> None:
        error = re.search(
            pattern=r'Please try again later. \((\d+)\)',
            string=steam_error,
        )
        if error and error.groups():
            code = int(error.group(1))
            check_steam_error(code)

    def _determine_error(self, steam_error: str) -> None:
        for _error, _exception, _exception_message in self.errors:
            if _error in steam_error:
                raise _exception(_exception_message)

    def _check_error_for_send_and_accept(self, response: Dict) -> None:
        error = response.get('strError')
        if isinstance(error, str):
            self._determine_error(error)
            self._determine_error_code(error)

    def _check_error_for_cancel_and_decline(self, response: Dict) -> None:
        success = response.get('success')
        if isinstance(success, int):
            check_steam_error(error=success)

    def send_offer(self) -> SendOfferResponse:
        self._check_error_for_send_and_accept(
            response=json.loads(self.response),
        )
        return SendOfferResponse.parse_raw(self.response)

    def accept_offer(self) -> AcceptOfferResponse:
        self._check_error_for_send_and_accept(
            response=json.loads(self.response),
        )
        return AcceptOfferResponse.parse_raw(self.response)

    def decline_offer(self) -> None:
        return self._check_error_for_cancel_and_decline(
            response=json.loads(self.response),
        )

    def cancel_offer(self) -> None:
        return self._check_error_for_cancel_and_decline(
            response=json.loads(self.response),
        )
