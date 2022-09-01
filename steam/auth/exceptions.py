class LoginError(Exception):
    ...


class GetRsaError(LoginError):
    ...


class IncorrectCredentials(LoginError):
    """Incorrect user credentials."""


class NotFoundAuthenticatorError(Exception):
    """Authentication data not found in SteamAuth."""


class NotFoundAccountError(Exception):
    """Account not found in SteamAuth."""


class AccountAlreadyExistsError(Exception):
    """Account already exists in SteamAuth."""


class NotFoundMobileConfirmationError(Exception):
    """Error when searching for exchanges waiting for mobile confirmation."""


class InvalidAuthenticatorError(Exception):
    """Invalid authenticator."""


class TooManyLoginError(Exception):
    ...


class CaptchaGidNotFound(Exception):
    ...


class NotFoundAntigateApiKey(Exception):
    ...
