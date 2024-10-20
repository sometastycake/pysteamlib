import json

from pysteamauth.auth import Steam

from .exceptions import NotFoundMobileConfirmationError
from .handlers import OfferResponseHandler
from .schemas import (
    AcceptOfferResponse,
    MobileConfirmation,
    MobileConfirmationResponse,
    SendOfferRequest,
    SendOfferResponse,
)


class SteamTrade:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def send_offer(self, request: SendOfferRequest) -> SendOfferResponse:
        if not request.sessionid:
            request.sessionid = await self.steam.sessionid()
        response: str = await self.steam.request(
            method='POST',
            url='https://steamcommunity.com/tradeoffer/new/send',
            data=request.to_request(),
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': request.tradelink(self.steam.partner_id),
            },
        )
        return OfferResponseHandler(response).send_offer()

    async def cancel_offer(self, tradeofferid: int) -> None:
        response: str = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/tradeoffer/{tradeofferid}/cancel',
            data={
                'sessionid': await self.steam.sessionid(),
            },
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid}/tradeoffers/sent/',
            },
        )
        return OfferResponseHandler(response).cancel_offer()

    async def decline_offer(self, tradeofferid: int) -> None:
        response: str = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/tradeoffer/{tradeofferid}/decline',
            data={
                'sessionid': await self.steam.sessionid(),
            },
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid}/tradeoffers/',
            },
        )
        return OfferResponseHandler(response).decline_offer()

    async def accept_offer(self, tradeofferid: int, partner_steamid: int) -> AcceptOfferResponse:
        response: str = await self.steam.request(
            method='POST',
            url=f'https://steamcommunity.com/tradeoffer/{tradeofferid}/accept',
            data={
                'sessionid': await self.steam.sessionid(),
                'serverid': '1',
                'tradeofferid': str(tradeofferid),
                'partner': str(partner_steamid),
                'captcha': '',
            },
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/tradeoffer/{tradeofferid}/',
            },
        )
        return OfferResponseHandler(response).accept_offer()

    async def get_mobile_confirmations(self) -> MobileConfirmationResponse:
        server_time: int = await self.steam.get_server_time()
        confirmation_hash: str = self.steam.get_confirmation_hash(
            server_time=server_time,
        )
        response: str = await self.steam.request(
            url='https://steamcommunity.com/mobileconf/getlist',
            method='GET',
            cookies={
                'mobileClient': 'ios',
                'mobileClientVersion': '2.0.20',
                'steamid': str(self.steam.steamid),
                'Steam_Language': 'english',
            },
            params={
                'p': self.steam.device_id,
                'a': str(self.steam.steamid),
                'k': confirmation_hash,
                't': server_time,
                'm': 'react',
                'tag': 'conf',
            },
        )
        return MobileConfirmationResponse.parse_raw(response)

    async def mobile_confirm(self, confirmation: MobileConfirmation) -> bool:
        server_time: int = await self.steam.get_server_time()
        confirmation_hash: str = self.steam.get_confirmation_hash(
            server_time=server_time,
            tag='allow',
        )
        response: str = await self.steam.request(
            url='https://steamcommunity.com/mobileconf/ajaxop',
            method='GET',
            cookies={
                'mobileClient': 'ios',
                'mobileClientVersion': '2.0.20',
            },
            params={
                'op': 'allow',
                'p': self.steam.device_id,
                'a': str(self.steam.steamid),
                'k': confirmation_hash,
                't': server_time,
                'm': 'react',
                'tag': 'allow',
                'cid': confirmation.confirmation_id,
                'ck': confirmation.confirmation_key,
            },
        )
        return json.loads(response)['success']

    async def mobile_confirm_by_creator_id(self, creator_id: int) -> bool:
        """
        For trade offers creator_id is trade offer id
        """
        confirmations: MobileConfirmationResponse = await self.get_mobile_confirmations()
        for confirmation in confirmations.conf:
            if confirmation.creator_id == creator_id:
                return await self.mobile_confirm(confirmation)
        raise NotFoundMobileConfirmationError(f'Not found confirmation for {creator_id}')
