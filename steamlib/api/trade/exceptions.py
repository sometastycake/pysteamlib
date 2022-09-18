class SendOfferError(Exception):
    """Error sending exchange."""


class SteamNullResponseError(SendOfferError):
    """If response from Steam is null."""


class SteamServerDownError(SendOfferError):
    """Steam servers may be down."""


class TradeOffersLimitError(SendOfferError):
    """Trade offers limit."""


class AccountOverflowError(SendOfferError):
    """Account overflow."""


class TradeBanError(SendOfferError):
    """Account have a trade ban."""


class ProfileSettingsError(SendOfferError):
    """Incorrect profile settings."""


class TradelinkError(SendOfferError):
    """Tradelink may be incorrect."""


class NotFoundMobileConfirmationError(Exception):
    """No offer found pending mobile confirmation."""


class InvalidAuthenticatorError(Exception):
    """Invalid authenticator."""


class InvalidConfirmationPageError(Exception):
    """Invalid confirmation page."""
