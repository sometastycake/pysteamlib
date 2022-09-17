class UnauthorizedSteamRequestError(Exception):

    def __init__(self, url: str):
        self.url = url

    def __str__(self) -> str:
        return f'Unauthorized request to "{self.url}"'
