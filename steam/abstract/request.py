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
    ) -> str:
        ...

    async def request_with_cookie_return(
            self,
            url: str,
            method: str = 'GET',
            cookies: Optional[Dict] = None,
            **kwargs: Any,
    ) -> Tuple[str, Dict[str, str]]:
        ...
