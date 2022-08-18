from session import Session
from steam.api.public.schemas import ServerTimeResponse


class SteamPublicAPI(Session):

    async def server_time(self) -> ServerTimeResponse:
        response = await self.session.post(
            url='https://api.steampowered.com/ITwoFactorService/QueryTime/v0001',
        )
        return ServerTimeResponse.parse_raw(await response.text())
