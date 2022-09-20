from enum import Enum, IntEnum


class PrivacyLevel(Enum):
    Opened = 3
    OnlyForFriends = 2
    Hidden = 1


class CommentPermissionLevel(IntEnum):
    Opened = 1
    Hidden = 2
    OnlyForFriends = 0
