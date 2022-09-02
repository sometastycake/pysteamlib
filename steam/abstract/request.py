from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class RequestStrategyAbstract(ABC):

    @abstractmethod
    async def request(
            self,
            url: str,
            method: str = 'GET',
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> Any:
        ...

    @abstractmethod
    async def request_with_text_response(
            self,
            url: str,
            method: str,
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> str:
        ...

    @abstractmethod
    async def request_with_json_response(
            self,
            url: str,
            method: str,
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> Dict:
        ...

    @abstractmethod
    def get_cookies(self, domain: str = 'steamcommunity.com') -> Dict[str, str]:
        ...
