from typing import Optional

from pydantic import BaseModel


class BaseSteamResponse(BaseModel):
    success: int
    errmsg: Optional[str]
