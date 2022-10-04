import logging

from pysteamauth.auth import Steam
from pysteamauth.errors import SteamError

from steamlib.api import SteamAPI
from steamlib.api.account import NicknameHistory, PrivacyInfo
from steamlib.api.account.enums import CommentPermissionLevel, PrivacyLevel
from steamlib.api.account.exceptions import KeyRegistrationError, ProfileError
from steamlib.api.account.schemas import (
    AvatarResponse,
    PrivacyResponse,
    PrivacySettings,
    ProfileInfo,
    ProfileInfoResponse,
)


class AccountExample:

    def __init__(self, steam: Steam):
        self.steam = steam
        self.api = SteamAPI(steam)

    async def profile(self) -> None:
        current_profile_settings: ProfileInfo = await self.api.account.get_current_profile_info()
        current_profile_settings.real_name = 'Real name'
        current_profile_settings.personaName = 'Persona name'
        current_profile_settings.customURL = 'Custom_URL'
        try:
            profile_setup_result: ProfileInfoResponse = await self.api.account.set_profile_info(
                info=current_profile_settings,
            )
        except SteamError as error:
            logging.exception(error)
            return
        print('Profile setup result: %s' % profile_setup_result)

    async def privacy_settings(self) -> None:
        try:
            current_privacy_settings: PrivacyInfo = await self.api.account.get_current_privacy()
        except ProfileError as error:
            logging.exception(error)
            return
        print('Current privacy settings: %s' % current_privacy_settings)
        try:
            privacy_setup_result: PrivacyResponse = await self.api.account.set_privacy(PrivacyInfo(
                PrivacySettings=PrivacySettings(
                    PrivacyProfile=PrivacyLevel.Opened,
                    PrivacyInventory=PrivacyLevel.OnlyForFriends,
                    PrivacyInventoryGifts=PrivacyLevel.OnlyForFriends,
                    PrivacyOwnedGames=PrivacyLevel.OnlyForFriends,
                    PrivacyPlaytime=PrivacyLevel.OnlyForFriends,
                    PrivacyFriendsList=PrivacyLevel.Hidden,
                ),
                eCommentPermission=CommentPermissionLevel.Hidden,
            ))
        except SteamError as error:
            logging.exception(error)
            return
        print('Privacy setup result: %s' % privacy_setup_result)

    async def run(self) -> None:
        if not await self.steam.is_authorized():
            await self.steam.login_to_steam()

        await self.profile()
        await self.privacy_settings()

        nickname_history: NicknameHistory = await self.api.account.get_nickname_history()
        avatar_uploading_result: AvatarResponse = await self.api.account.upload_avatar('./avatar.jpeg')
        current_tradelink: str = await self.api.account.get_tradelink()
        new_tradelink: str = await self.api.account.register_tradelink()

        try:
            key: str = await self.api.account.register_api_key('example.com')
        except KeyRegistrationError as error:
            logging.exception(error)
            return
        print('New api key: %s' % key)
