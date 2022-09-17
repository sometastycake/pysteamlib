import json
from typing import List

from lxml.html import HtmlElement, document_fromstring
from pysteamauth.auth import Steam

from steamlib.api.trade.exceptions import InvalidAuthenticatorError, NotFoundMobileConfirmationError
from steamlib.api.trade.handlers import (
    accept_offer_response_handler,
    cancel_offer_response_handler,
    decline_offer_response_handler,
    send_offer_response_handler,
)
from steamlib.api.trade.schemas import MobileConfirmation, SendOfferRequest, SendOfferResponse


class SteamTrade:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def send_offer(self, request: SendOfferRequest) -> SendOfferResponse:
        """
        Send offer.
        """
        response: str = await self.steam.request(
            method='POST',
            url='https://steamcommunity.com/tradeoffer/new/send',
            data=request.to_request(),
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': request.tradelink(),
            },
        )
        return send_offer_response_handler(response)

    async def cancel_offer(self, tradeofferid: int) -> None:
        """
        Cancel offer.
        """
        response = await self.steam.request(
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
        return cancel_offer_response_handler(response)

    async def decline_offer(self, tradeofferid: int) -> None:
        """
        Decline offer.

        :param tradeofferid: Tradeofferid.
        """
        response = await self.steam.request(
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
        return decline_offer_response_handler(response)

    async def accept_offer(self, tradeofferid: int, partner_steamid: int) -> int:
        """
        Accept offer.

        :return: Tradeid.
        """
        response = await self.steam.request(
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
                'Referer': f'https://steamcommunity.com/tradeoffer/{tradeofferid}/'
            },
        )
        return accept_offer_response_handler(response)

    def _parse_mobile_confirmations_response(self, response: str) -> List[MobileConfirmation]:
        """
        Parse mobile confirmations response.
        """
        page: HtmlElement = document_fromstring(response)
        raw_confirmations: List[HtmlElement] = page.cssselect('#mobileconf_list > .mobileconf_list_entry')
        if not raw_confirmations:
            return []
        confirmations = []
        for confirmation in raw_confirmations:
            confirmations.append(MobileConfirmation(
                confirmation_id=int(confirmation.attrib['data-confid']),
                confirmation_key=int(confirmation.attrib['data-key']),
                tradeofferid=int(confirmation.attrib['data-creator']),
            ))
        return confirmations

    async def get_mobile_confirmations(self) -> List[MobileConfirmation]:
        """
        Get mobile confirmations.
        """
        cookies = await self.steam.cookies()
        server_time = await self.steam.get_server_time()
        confirmation_hash = self.steam.get_confirmation_hash(
            server_time=server_time,
        )
        response = await self.steam.request(
            url='https://steamcommunity.com/mobileconf/conf',
            method='GET',
            cookies={
                **cookies,
                'mobileClient': 'ios',
                'mobileClientVersion': '2.0.20',
                'steamid': str(self.steam.steamid),
                'Steam_Language': 'english',
            },
            params={
                'p': self.steam.authenticator.device_id,
                'a': str(self.steam.steamid),
                'k': confirmation_hash,
                't': server_time,
                'm': 'ios',
                'tag': 'conf',
            },
        )
        if '<div>Invalid authenticator</div>' in response:
            raise InvalidAuthenticatorError
        return self._parse_mobile_confirmations_response(response)

    async def mobile_confirm(self, confirmation: MobileConfirmation) -> bool:
        """
        Mobile confirm.
        """
        cookies = await self.steam.cookies()
        server_time = await self.steam.get_server_time()
        confirmation_hash = self.steam.get_confirmation_hash(
            server_time=server_time,
            tag='allow',
        )
        response = await self.steam.request(
            url='https://steamcommunity.com/mobileconf/ajaxop',
            method='GET',
            cookies={
                **cookies,
                'mobileClient': 'ios',
                'mobileClientVersion': '2.0.20',
            },
            params={
                'op': 'allow',
                'p': self.steam.authenticator.device_id,
                'a': str(self.steam.steamid),
                'k': confirmation_hash,
                't': server_time,
                'm': 'ios',
                'tag': 'allow',
                'cid': confirmation.confirmation_id,
                'ck': confirmation.confirmation_key,
            },
        )
        return json.loads(response)['success']

    async def mobile_confirm_by_tradeofferid(self, tradeofferid: int) -> bool:
        """
        Mobile confirm by tradeofferid.
        """
        confirmations = await self.get_mobile_confirmations()
        for confirmation in confirmations:
            if confirmation.tradeofferid == tradeofferid:
                return await self.mobile_confirm(confirmation)
        raise NotFoundMobileConfirmationError(f'Not found confirmation for {tradeofferid}')