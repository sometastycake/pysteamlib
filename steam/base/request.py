from typing import Any, Dict, Optional, Tuple

import aiohttp

from steam.abstract.request import RequestStrategyAbstract
from steam.errors.exceptions import SteamWrongHttpStatusError, TooManySteamRequestsError, UnauthorizedSteamRequestError


class BaseRequestStrategy(RequestStrategyAbstract):

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    def __del__(self):
        if self._session:
            self._session.connector.close()

    def _create_session(self) -> aiohttp.ClientSession:
        """
        Create aiohttp session.
        Aiohttp session saves and stores cookies.
        It writes cookies from responses after each request that specified
        in Set-Cookie header. This is undesirable behavior, so by using DummyCookies we disable
        autosave of cookies within the aiohttp session.

        :return: aiohttp.ClientSession object.
        """
        return aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False),
            cookie_jar=aiohttp.DummyCookieJar(),
        )

    async def _request(
            self,
            url: str,
            method: str = 'GET',
            raise_for_status: bool = True,
            **kwargs: Any,
    ) -> aiohttp.ClientResponse:
        if self._session is None:
            self._session = self._create_session()
        response = await self._session.request(method, url, **kwargs)
        if raise_for_status and not response.ok:
            if response.status == 429:
                raise TooManySteamRequestsError
            if response.status == 401:
                raise UnauthorizedSteamRequestError(url=url)
            raise SteamWrongHttpStatusError(http_status=response.status)
        return response

    async def request(
            self,
            url: str,
            method: str = 'GET',
            raise_for_status: bool = True,
            **kwargs: Any,
    ) -> str:
        response = await self._request(url, method, raise_for_status, **kwargs)
        return await response.text()

    async def request_with_cookie_return(
            self,
            url: str,
            method: str = 'GET',
            **kwargs: Any,
    ) -> Tuple[str, Dict[str, str]]:
        response = await self._request(url, method, allow_redirects=False, **kwargs)
        return await response.text(), {
            k: v.value for k, v in response.cookies.items()
        }
