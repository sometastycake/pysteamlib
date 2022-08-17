class LoginError(Exception):

    def __init__(self, login: str):
        self.login = login

    def __str__(self):
        return f'<Error={self.__class__.__name__} login={self.login}>'


class GetRsaError(LoginError):
    ...


class IncorrectCredentials(LoginError):
    ...


class WrongCaptcha(LoginError):
    ...


class NotFoundAntigateApiKey(LoginError):
    ...


class CaptchaGidNotFound(LoginError):
    ...
