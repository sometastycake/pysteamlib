class SendOfferError(Exception):
    ...


class SteamNullResponseError(SendOfferError):
    ...


class SteamServerDownError(SendOfferError):
    ...


class TradeOffersLimitError(SendOfferError):
    ...


class AccountOverflowError(SendOfferError):
    ...


class TradeBanError(SendOfferError):
    ...


class ProfileSettingsError(SendOfferError):
    ...


class TradelinkError(SendOfferError):
    ...


class NotFoundMobileConfirmationError(Exception):
    """Error when searching for exchanges waiting for mobile confirmation."""


class InvalidAuthenticatorError(Exception):
    """Invalid authenticator."""
