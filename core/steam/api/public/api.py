from session import Session
from steam.api.market.schemas import ApplistResponse
from steam.api.public.schemas import ServerTimeResponse


class SteamAPI(Session):

    @classmethod
    async def server_time(cls) -> ServerTimeResponse:
        """
        Steam server time.
        It uses for Steam Guard calculating.

        :return: Server time.
        """
        response = await cls.session.post(
            url='https://api.steampowered.com/ITwoFactorService/QueryTime/v0001',
        )
        return ServerTimeResponse.parse_raw(await response.text())

    @classmethod
    async def get_app_list(cls) -> ApplistResponse:
        """
        All Steam apps.

        :return: Apps.
        """
        response = await cls.session.get(
            url='https://api.steampowered.com/ISteamApps/GetAppList/v0002/',
            params={
                'format': 'json',
            },
        )
        return ApplistResponse.parse_raw(await response.text())
