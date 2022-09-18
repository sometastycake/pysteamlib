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
    ...


class InvalidAuthenticatorError(Exception):
    ...


class InvalidConfirmationPageError(Exception):
    ...
