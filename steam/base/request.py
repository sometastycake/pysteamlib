from typing import Any, Dict, Optional, Tuple

import aiohttp


class BaseRequestStrategy:

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    def __del__(self):
        if self._session:
            self._session.connector.close()

    async def request(
            self,
            url: str,
            method: str,
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> Any:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                raise_for_status=True,
                cookie_jar=aiohttp.DummyCookieJar(),
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

    async def request_with_return_cookie(
            self,
            url: str,
            method: str = 'GET',
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> Tuple[str, Dict[str, str]]:
        response = await self.request(
            url=url,
            method=method,
            cookies=cookies,
            allow_redirects=False,
            **kwargs,
        )
        cookies = {
            k: v.value for k, v in response.cookies.items()
        }
        return await response.text(), cookies
