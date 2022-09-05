from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple


class RequestStrategyAbstract(ABC):

    @abstractmethod
    async def request(
            self,
            url: str,
            method: str = 'GET',
            raise_for_status: bool = True,
            **kwargs: Any,
    ) -> str:
        ...

    async def request_with_cookie_return(
            self,
            url: str,
            method: str = 'GET',
            **kwargs: Any,
    ) -> Tuple[str, Dict[str, str]]:
        ...
