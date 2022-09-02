from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple


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
            method: str = 'GET',
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> Any:
        ...

    @abstractmethod
    async def request_with_json_response(
            self,
            url: str,
            method: str = 'GET',
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> Dict:
        ...

    @abstractmethod
    async def request_with_return_cookie(
            self,
            url: str,
            method: str = 'GET',
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> Tuple[str, Dict[str, str]]:
        ...
