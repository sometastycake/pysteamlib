from typing import Dict, Optional

from pydantic import BaseModel, root_validator
from pysteamauth.errors import check_steam_error


class BaseSteamResponse(BaseModel):
    success: int
    errmsg: Optional[str]

    @root_validator
    def _check_error(cls, values: Dict) -> Dict:  # noqa:U100
        if values.get('success'):
            check_steam_error(
                error=values.get('success'),
                error_msg=values.get('errmsg'),
            )
        return values
