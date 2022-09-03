class LoginError(Exception):

    def __init__(self, login: str):
        self.login = login

    def __str__(self) -> str:
        return str({
            'exception': self.__class__.__name__,
            'login': self.login,
        })


class GetRsaError(LoginError):
    """Error in receiving keys for password encryption."""


class TooManyAuthorizations(LoginError):
    """Too many authorizations."""


class IncorrectCredentialsError(LoginError):
    """Incorrect user credentials."""


class NotFoundAuthenticatorError(Exception):
    """Authentication data not found in SteamAuth."""


class NotFoundAccountError(Exception):
    """Account not found in SteamAuth."""


class AccountAlreadyExistsError(Exception):
    """Account already exists in SteamAuth."""
