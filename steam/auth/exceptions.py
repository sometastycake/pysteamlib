from typing import Optional


class LoginError(Exception):

    def __init__(self, login: str, msg: Optional[str] = None):
        self.msg = msg
        self.login = login

    def __str__(self) -> str:
        return str({
            'exception': self.__class__.__name__,
            'login': self.login,
            'msg': self.msg,
        })


class GetRsaError(LoginError):
    """Error in receiving keys for password encryption."""


class TooManyAuthorizationsError(LoginError):
    """Too many authorizations."""


class IncorrectCredentialsError(LoginError):
    """Incorrect user credentials."""


class NotFoundAuthenticatorError(Exception):
    """Authentication data not found in SteamAuth."""


class AccountAlreadyExistsError(Exception):
    """Account already exists in SteamAuth."""
