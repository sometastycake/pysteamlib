import aiofiles.os
import aiohttp
from antigate import AntiGate

from steam.config import config


def _solve(path_to_file: str) -> str:
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


async def _get_image(link: str) -> bytes:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        response = await session.get(link)
        return await response.content.read()


async def solve_captcha_through_antigate(link: str) -> str:
    async with aiofiles.tempfile.NamedTemporaryFile(delete=True) as file:
        image = await _get_image(link)
        await file.write(image)
        return _solve(str(file.name))
