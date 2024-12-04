import json
from typing import Any, Dict, Union

from pysteamauth.auth import Steam
from yarl import URL

from .exceptions import GetConfirmationsError, NotFoundMobileConfirmationError, SendOfferError
from .schemas import GetMobileConfirmationResponse, SendOfferRequest


class SteamTrade:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def send_offer(self, request: SendOfferRequest) -> Dict:
        params = URL(request.tradelink).query
        if 'partner' not in params:
            raise ValueError('Partner parameter is missing in tradelink')
        if 'token' not in params:
            raise ValueError('Token parameter is missing in tradelink')
        response: str = await self.steam.request(
            method='POST',
            url='https://steamcommunity.com/tradeoffer/new/send',
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': request.tradelink,
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.9.5.20) Gecko/2812-12-10 04:56:28 Firefox/3.8',
            },
            data={
                'captcha': '',
                'serverid': '1',
                'partner': request.partner,
                'tradeoffermessage': request.tradeoffermessage,
                'sessionid': await self.steam.sessionid(),
                'trade_offer_create_params': json.dumps({
                    'trade_offer_access_token': params['token'],
                }),
                'json_tradeoffer': json.dumps({
                    'newversion': True,
                    'version': 2,
                    'me': {
                        'currency': [],
                        'ready': False,
                        'assets': [asset.dict() for asset in request.me],
                    },
                    'them': {
                        'currency': [],
                        'ready': False,
                        'assets': [asset.dict() for asset in request.them],
                    },
                }),
            },
        )
        if response == 'null':
            raise SendOfferError('Send offer error')
        return json.loads(response)

    async def accept_offer(self, tradeofferid: Union[int, str], partner_steamid: int) -> Dict:
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
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.9.5.20) Gecko/2812-12-10 04:56:28 Firefox/3.8',
            },
        )
        return json.loads(response)

    async def cancel_offer(self, tradeofferid: Union[int, str]) -> Any:
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
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.9.5.20) Gecko/2812-12-10 04:56:28 Firefox/3.8',
            },
        )
        return json.loads(response)

    async def decline_offer(self, tradeofferid: Union[int, str]) -> Any:
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
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.9.5.20) Gecko/2812-12-10 04:56:28 Firefox/3.8',
            },
        )
        return json.loads(response)

    async def get_mobile_confirmations(self) -> GetMobileConfirmationResponse:
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
        return GetMobileConfirmationResponse.parse_raw(response)

    async def mobile_confirm(self, confirmation_id: int, confirmation_key: int) -> Dict:
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
                'cid': confirmation_id,
                'ck': confirmation_key,
            },
        )
        return json.loads(response)

    async def mobile_confirm_by_creator_id(self, creator_id: Union[int, str]) -> Dict:
        """
        For trade offers creator_id is trade offer id
        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise TypeError('Invalid value of creator_id')
        confirmations = await self.get_mobile_confirmations()
        if confirmations.success is False:
            raise GetConfirmationsError(
                message=confirmations.message,
                detail=confirmations.detail,
            )
        for confirmation in confirmations.conf:
            if confirmation.creator_id == int(creator_id):
                return await self.mobile_confirm(
                    confirmation_id=confirmation.confirmation_id,
                    confirmation_key=confirmation.confirmation_key,
                )
        raise NotFoundMobileConfirmationError(f'Not found confirmation for creator_id={creator_id}')
