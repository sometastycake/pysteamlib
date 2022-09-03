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


class TooManyAuthorizations(Exception):
    """Too many authorizations."""
