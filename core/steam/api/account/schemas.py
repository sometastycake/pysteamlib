from typing import Optional

from pydantic import BaseModel
from steam.api.account.enums import CommentPermissionLevel, PrivacyLevel


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


class PrivacyResponse(BaseModel):
    success: int
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


class ProfileInfoResponse(BaseModel):
    success: int
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
