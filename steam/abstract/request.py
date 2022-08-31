from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class RequestStrategyAbstract(ABC):

    @abstractmethod
    async def request(self, url: str, method: str = 'GET', cookies: Optional[Dict] = None, **kwargs: Any) -> Any:
        ...
