import asyncio
from functools import wraps
from typing import Any, Callable, Optional

from aiohttp import ClientResponseError
from antigate import AntiGateError

from steam.errors import LoginError, WrongCaptcha


def repeat_login(retry: int, timeout: int = 3) -> Callable:
    def decorator(function: Callable) -> Callable:
        @wraps(function)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            exception: Optional[BaseException] = None
            for _ in range(retry):
                try:
                    result = await function(*args, **kwargs)
                except (WrongCaptcha, LoginError, AntiGateError, ClientResponseError) as error:
                    exception = error
                    await asyncio.sleep(timeout)
                else:
                    if not result:
                        continue
                    return result
            if exception is None:
                raise LoginError
            raise exception
        return wrapper
    return decorator
