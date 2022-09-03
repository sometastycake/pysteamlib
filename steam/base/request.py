from typing import Any, Dict, Optional, Tuple

import aiohttp

from steam.abstract.request import RequestStrategyAbstract


class BaseRequestStrategy(RequestStrategyAbstract):

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    def __del__(self):
        if self._session:
            self._session.connector.close()

    def _create_session(self) -> aiohttp.ClientSession:
        """
        Create aiohttp session.
        """
        return aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False),
            raise_for_status=True,
            cookie_jar=aiohttp.DummyCookieJar(),
        )

    async def _request(self,
            url: str,
            method: str = 'GET',
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> aiohttp.ClientResponse:
        if self._session is None:
            self._session = self._create_session()
        return await self._session.request(method, url, cookies=cookies, **kwargs)

    async def request(
            self,
            url: str,
            method: str = 'GET',
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> str:
        response = await self._request(url, method, cookies=cookies, **kwargs)
        return await response.text()

    async def request_with_cookie_return(
            self,
            url: str,
            method: str = 'GET',
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> Tuple[str, Dict[str, str]]:
        response = await self._request(url, method, cookies=cookies, allow_redirects=False, **kwargs)
        response_cookies = {}
        for name, value in response.cookies.items():
            response_cookies[name] = value.value
        return await response.text(), response_cookies
