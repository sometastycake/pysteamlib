from typing import Dict, Optional

import aiohttp


class _classproperty:

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class Session:

    _session: Optional[aiohttp.ClientSession] = None

    @_classproperty
    def session(cls) -> aiohttp.ClientSession:
        if cls._session is None:
            cls._session = aiohttp.ClientSession(
                raise_for_status=True,
                connector=aiohttp.TCPConnector(ssl=False, force_close=True),
                timeout=aiohttp.ClientTimeout(total=10),
            )
        return cls._session

    def __del__(self):
        if self._session and not self._session.closed:
            self._session.connector.close()

    def get_cookies(self, domain: str) -> Dict[str, str]:
        """
        Aiohttp session saves and stores cookies.
        It writes cookies from responses after each request that specified
        in Set-Cookie header.
        """
        cookies = {}
        for cookie in self.session.cookie_jar:
            if cookie['domain'] == domain:
                cookies[cookie.key] = cookie.value
        return cookies
