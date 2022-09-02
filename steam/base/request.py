from typing import Any, Dict, Optional, Tuple

import aiohttp

from steam.abstract.request import RequestStrategyAbstract


class BaseRequestStrategy(RequestStrategyAbstract):

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    def __del__(self):
        if self._session:
            self._session.connector.close()

    async def request(
            self,
            url: str,
            method: str = 'GET',
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> Any:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                raise_for_status=True,
            )
        return await self._session.request(method, url, cookies=cookies, **kwargs)

    async def request_with_text_response(
            self,
            url: str,
            method: str,
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> str:
        response = await self.request(
            url=url,
            method=method,
            cookies=cookies,
            **kwargs,
        )
        return await response.text()

    async def request_with_json_response(
            self,
            url: str,
            method: str,
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> Dict:
        response = await self.request(
            url=url,
            method=method,
            cookies=cookies,
            **kwargs,
        )
        return await response.json()

    def get_cookies(self, domain: str = 'steamcommunity.com') -> Dict[str, str]:
        """
        Aiohttp session saves and stores cookies.
        It writes cookies from responses after each request that specified
        in Set-Cookie header.
        """
        cookies = {}
        for cookie in self._session.cookie_jar:
            if cookie['domain'] == domain:
                cookies[cookie.key] = cookie.value
        return cookies
