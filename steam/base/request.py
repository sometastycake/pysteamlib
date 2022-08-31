from typing import Any, Dict, Optional

import aiohttp


class BaseRequestStrategy:

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    def __del__(self):
        if self._session:
            self._session.connector.close()

    async def request(self, url: str, method: str, cookies: Optional[Dict] = None, **kwargs: Any) -> Any:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                raise_for_status=True,
                cookie_jar=aiohttp.DummyCookieJar(),
            )
        return await self._session.request(method, url, cookies=cookies, **kwargs)
