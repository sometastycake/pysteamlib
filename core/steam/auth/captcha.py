import aiofiles.os
from antigate import AntiGate
from session import Session

from core.config import config


class AntigateCaptchaSolver(Session):
    """antigate.com"""

    def __init__(self, link: str):
        super().__init__()
        self.link = link

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

    async def get_image(self) -> bytes:
        async with await self.session.get(self.link) as response:
            content = response.content
            return await content.read()

    async def solve(self) -> str:
        async with aiofiles.tempfile.NamedTemporaryFile(delete=True) as file:
            image = await self.get_image()
            await file.write(image)
            return self._solve(str(file.name))
