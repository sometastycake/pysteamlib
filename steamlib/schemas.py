from typing import Optional

from pydantic import BaseModel
from pysteamauth.errors import check_steam_error


class BaseSteamResponse(BaseModel):
    success: int
    errmsg: Optional[str]

    def check_error(self) -> None:
        check_steam_error(
            error=self.success,
            error_msg=self.errmsg,
        )
