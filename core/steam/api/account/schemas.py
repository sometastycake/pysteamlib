from typing import Generator, List, Optional

from pydantic import BaseModel
from steam.api.account.enums import CommentPermissionLevel, PrivacyLevel
from steam.schemas import BaseSteamResponse


class PrivacySettings(BaseModel):
    PrivacyProfile: PrivacyLevel
    PrivacyInventory: PrivacyLevel
    PrivacyInventoryGifts: PrivacyLevel
    PrivacyOwnedGames: PrivacyLevel
    PrivacyPlaytime: PrivacyLevel
    PrivacyFriendsList: PrivacyLevel


class PrivacyInfo(BaseModel):
    PrivacySettings: PrivacySettings
    eCommentPermission: CommentPermissionLevel


class PrivacyResponse(BaseSteamResponse):
    Privacy: PrivacyInfo


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


class ProfileInfoResponse(BaseSteamResponse):
    errmsg: str


class Images(BaseModel):
    standart: str
    full: str
    medium: str

    class Config:
        fields = {
            'standart': '0',
        }


class AvatarResponse(BaseModel):
    success: bool
    images: Images
    hash: str
    message: str


class Nickname(BaseModel):
    newname: str
    timechanged: str


class NicknameHistory(BaseModel):
    __root__: List[Nickname]

    def __iter__(self) -> Generator[Nickname, None, None]:  # type:ignore
        for nickname in self.__root__:
            yield nickname
