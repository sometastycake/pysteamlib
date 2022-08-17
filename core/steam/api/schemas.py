from typing import Optional

from pydantic import BaseModel
from steam.api.errors import ErrorSetProfileInfo


class ProfileInfo(BaseModel):
    weblink_1_title: Optional[str] = ''
    weblink_1_url: Optional[str] = ''
    weblink_2_title: Optional[str] = ''
    weblink_2_url: Optional[str] = ''
    weblink_3_title: Optional[str] = ''
    weblink_3_url: Optional[str] = ''
    personaName: Optional[str] = ''
    real_name: Optional[str] = ''
    customURL: Optional[str] = ''
    country: Optional[str] = ''
    state: Optional[str] = ''
    city: Optional[str] = ''
    summary: Optional[str] = ''
    hide_profile_awards: str = '0'


class ProfileInfoResponse(BaseModel):
    success: int
    errmsg: str

    def check_response(self) -> None:
        if self.errmsg:
            raise ErrorSetProfileInfo(self.errmsg)
