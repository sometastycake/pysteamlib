from session import Session

from steam._api.market.schemas import ApplistResponse


class SteamPublic(Session):

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
