from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping, Optional, Tuple


class RequestStrategyAbstract(ABC):

    @abstractmethod
    async def request(
            self,
            url: str,
            method: str = 'GET',
            cookies: Optional[Mapping[str, str]] = None,
            params: Optional[Mapping[str, str]] = None,
            headers: Optional[Mapping[str, str]] = None,
            **kwargs: Any,
    ) -> str:
        ...

    async def request_with_cookie_return(
            self,
            url: str,
            method: str = 'GET',
            cookies: Optional[Mapping[str, str]] = None,
            params: Optional[Mapping[str, str]] = None,
            headers: Optional[Mapping[str, str]] = None,
            **kwargs: Any,
    ) -> Tuple[str, Dict[str, str]]:
        ...
