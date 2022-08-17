from typing import Dict

import aiohttp


class Session:

    def __init__(self):
        self.session = aiohttp.ClientSession(
            raise_for_status=True,
            connector=aiohttp.TCPConnector(ssl=False),
            timeout=aiohttp.ClientTimeout(total=10),
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/536.0 '
                              '(KHTML, like Gecko) Chrome/34.0.825.0 Safari/536.0',
            },
        )

    def __del__(self):
        self.session.connector.close()

    def clear_cookies(self) -> None:
        """
        Clear cookies.
        """
        self.session.cookie_jar.clear()

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
