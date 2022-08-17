from functools import wraps
from logging import getLogger
from typing import Any, Callable, Optional

from aiohttp import ClientResponseError
from antigate import AntiGateError
from steam.errors import LoginError, WrongCaptcha


def repeat_login(retry: int) -> Callable:
    def decorator(function: Callable) -> Callable:
        @wraps(function)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            exception: Optional[BaseException] = None
            for _ in range(retry):
                try:
                    result = await function(*args, **kwargs)
                except ClientResponseError as error:
                    getLogger().debug('Wrong HTTP status from Steam %s ' % error.status)
                    raise
                except (WrongCaptcha, LoginError, AntiGateError) as error:
                    getLogger().debug(str(error))
                    exception = error
                else:
                    if not result:
                        continue
                    return result
            if exception is None:
                raise LoginError
            raise exception
        return wrapper
    return decorator
