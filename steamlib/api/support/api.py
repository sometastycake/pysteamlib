from pysteamauth.auth import Steam


class SteamSupport:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def login_history(self):
        ...
