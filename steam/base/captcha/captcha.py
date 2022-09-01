import aiofiles.os
import aiohttp
from antigate import AntiGate

from steam.abstract.captcha import CaptchaSolverAbstract
from steam.base.captcha.exc import NotFoundAntigateApiKey
from steam.config import config


class BaseAntigateCaptchaSolver(CaptchaSolverAbstract):

    def _solve(self, path_to_file: str) -> str:
        if not config.ANTIGATE_API_KEY:
            raise NotFoundAntigateApiKey

        answer = AntiGate(
            api_key=config.ANTIGATE_API_KEY,
            captcha_file=path_to_file,
            send_config={
                'min_len': '6',
                'max_len': '6',
                'regsense': '1',
            },
        )
        return str(answer).replace('&amp;', '&')

    async def _get_image(self, link: str) -> bytes:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            response = await session.get(link)
            return await response.content.read()

    async def __call__(self, link: str) -> str:
        async with aiofiles.tempfile.NamedTemporaryFile(delete=True) as file:
            image = await self._get_image(link)
            await file.write(image)
            return self._solve(str(file.name))
