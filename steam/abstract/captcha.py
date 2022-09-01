from abc import ABC, abstractmethod


class CaptchaSolverAbstract(ABC):

    @abstractmethod
    async def __call__(self, captcha_url: str) -> str:
        ...
