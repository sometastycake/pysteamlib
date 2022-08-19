class LoginError(Exception):
    ...


class GetRsaError(LoginError):
    ...


class IncorrectCredentials(LoginError):
    ...


class WrongCaptcha(LoginError):
    ...


class NotFoundAntigateApiKey(LoginError):
    ...


class NotFoundSharedSecret(LoginError):
    ...


class CaptchaGidNotFound(LoginError):
    ...
