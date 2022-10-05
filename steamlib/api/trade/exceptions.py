class SendOfferError(Exception):
    """Error sending exchange."""


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


class MobileConfirmationError(Exception):
    """Base mobile confirmation error."""


class NotFoundMobileConfirmationError(MobileConfirmationError):
    """No offer found pending mobile confirmation."""


class InvalidAuthenticatorError(MobileConfirmationError):
    """Invalid authenticator."""


class InvalidConfirmationPageError(MobileConfirmationError):
    """Invalid confirmation page."""
