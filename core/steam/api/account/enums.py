from enum import Enum, IntEnum


class PrivacyLevel(Enum):
    Opened = 3
    OnlyForFriends = 2
    Hidden = 1


class CommentPermissionLevel(IntEnum):
    Opened = 1
    Hidden = 2
    OnlyForFriends = 0


class Language(Enum):
    schinese = 'schinese'
    tchinese = 'tchinese'
    japanese = 'japanese'
    koreana = 'koreana'
    thai = 'thai'
    bulgarian = 'bulgarian'
    czech = 'czech'
    danish = 'danish'
    german = 'german'
    english = 'english'
    spanish = 'spanish'
    latam = 'latam'
    greek = 'greek'
    french = 'french'
    italian = 'italian'
    hungarian = 'hungarian'
    dutch = 'dutch'
    norwegian = 'norwegian'
    polish = 'polish'
    portuguese = 'portuguese'
    brazilian = 'brazilian'
    romanian = 'romanian'
    russian = 'russian'
    finnish = 'finnish'
    swedish = 'swedish'
    turkish = 'turkish'
    vietnamese = 'vietnamese'
    ukrainian = 'ukrainian'
