from typing import Optional


class SendOfferError(Exception):
    """Error sending exchange."""


class MobileConfirmationError(Exception):
    """Base mobile confirmation error."""


class NotFoundMobileConfirmationError(MobileConfirmationError):
    """No offer found pending mobile confirmation."""


class GetConfirmationsError(MobileConfirmationError):
    """Get confirmation error."""

    def __init__(self, message: Optional[str], detail: Optional[str]):
        self.message = message
        self.detail = detail

    def __str__(self) -> str:
        return f'Get mobile confirmations error message={self.message} detail={self.detail}'
