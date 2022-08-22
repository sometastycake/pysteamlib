import aiofiles.os
from antigate import AntiGate
from session import Session

from core.config import config


class AntigateCaptchaSolver(Session):
    """antigate.com"""

    def _solve(self, path_to_file: str) -> str:
        answer = AntiGate(
            api_key=config.antigate_api_key,
            captcha_file=path_to_file,
            send_config={
                'min_len': '6',
                'max_len': '6',
                'regsense': '1',
            },
        )
        return str(answer).replace('&amp;', '&')

    @classmethod
    async def get_image(cls, link: str) -> bytes:
        response = await cls.session.get(link)
        return await response.content.read()

    async def solve(self, link: str) -> str:
        async with aiofiles.tempfile.NamedTemporaryFile(delete=True) as file:
            image = await self.get_image(link)
            await file.write(image)
            return self._solve(str(file.name))
