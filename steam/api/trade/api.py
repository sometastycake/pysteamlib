import json
from typing import List

from lxml.html import HtmlElement, document_fromstring

from steam.api.trade.exceptions import InvalidAuthenticatorError, NotFoundMobileConfirmationError
from steam.api.trade.handlers import (
    _accept_offer_response_handler,
    _cancel_offer_response_handler,
    _decline_offer_response_handler,
    _send_offer_response_handler,
)
from steam.api.trade.schemas import MobileConfirmation, SendOfferRequest, SendOfferResponse
from steam.auth.steam import Steam


class SteamTrade:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def send_offer(self, request: SendOfferRequest, login: str) -> SendOfferResponse:
        """
        Send offer.
        """
        response: str = await self.steam.http.request(
            method='POST',
            url='https://steamcommunity.com/tradeoffer/new/send',
            data=request.to_request(),
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': request.tradelink(),
            },
            raise_for_status=False,
            cookies=await self.steam.cookies(login),
        )
        return _send_offer_response_handler(response)

    async def cancel_offer(self, tradeofferid: int, login: str) -> None:
        """
        Cancel offer.
        """
        response = await self.steam.http.request(
            method='POST',
            url=f'https://steamcommunity.com/tradeoffer/{tradeofferid}/cancel',
            data={
                'sessionid': await self.steam.sessionid(login),
            },
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/tradeoffers/sent/',
            },
            raise_for_status=False,
            cookies=await self.steam.cookies(login),
        )
        return _cancel_offer_response_handler(response)

    async def decline_offer(self, tradeofferid: int, login: str) -> None:
        """
        Decline offer.

        :param tradeofferid: Tradeofferid.
        """
        response = await self.steam.http.request(
            method='POST',
            url=f'https://steamcommunity.com/tradeoffer/{tradeofferid}/decline',
            data={
                'sessionid': await self.steam.sessionid(login),
            },
            headers={
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': f'https://steamcommunity.com/profiles/{self.steam.steamid(login)}/tradeoffers/',
            },
            raise_for_status=False,
            cookies=await self.steam.cookies(login),
        )
        return _decline_offer_response_handler(response)

    async def accept_offer(self, tradeofferid: int, partner_steamid: int, login: str) -> int:
        """
        Accept offer.

        :return: Tradeid.
        """
        response = await self.steam.http.request(
            method='POST',
            url=f'https://steamcommunity.com/tradeoffer/{tradeofferid}/accept',
            data={
                'sessionid': await self.steam.sessionid(login),
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
            raise_for_status=False,
            login=login,
        )
        return _accept_offer_response_handler(response)

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

    async def get_mobile_confirmations(self, login: str) -> List[MobileConfirmation]:
        """
        Get mobile confirmations.
        """
        cookies = await self.steam.cookies(login)
        cookies.update({
            'mobileClient': 'ios',
            'mobileClientVersion': '2.0.20',
            'steamid': str(self.steam.steamid(login)),
            'Steam_Language': 'english',
        })
        server_time = await self.steam.get_server_time()
        confirmation_hash = self.steam.get_confirmation_hash(
            server_time=server_time,
            identity_secret=self.steam.authenticator(login).identity_secret,
        )
        response = await self.steam.http.request(
            url='https://steamcommunity.com/mobileconf/conf',
            method='GET',
            cookies=cookies,
            params={
                'p': self.steam.authenticator(login).device_id,
                'a': str(self.steam.steamid(login)),
                'k': confirmation_hash,
                't': server_time,
                'm': 'ios',
                'tag': 'conf',
            },
        )
        if '<div>Invalid authenticator</div>' in response:
            raise InvalidAuthenticatorError
        return self._parse_mobile_confirmations_response(response)

    async def mobile_confirm(self, confirmation: MobileConfirmation, login: str) -> bool:
        """
        Mobile confirm.
        """
        cookies = await self.steam.cookies(login)
        cookies.update({
            'mobileClient': 'ios',
            'mobileClientVersion': '2.0.20',
        })
        server_time = await self.steam.get_server_time()
        confirmation_hash = self.steam.get_confirmation_hash(
            server_time=server_time,
            identity_secret=self.steam.authenticator(login).identity_secret,
            tag='allow',
        )
        response = await self.steam.http.request(
            url='https://steamcommunity.com/mobileconf/ajaxop',
            method='GET',
            cookies=cookies,
            params={
                'op': 'allow',
                'p': self.steam.authenticator(login).device_id,
                'a': str(self.steam.steamid(login)),
                'k': confirmation_hash,
                't': server_time,
                'm': 'ios',
                'tag': 'allow',
                'cid': confirmation.confirmation_id,
                'ck': confirmation.confirmation_key,
            },
        )
        return json.loads(response)['success']

    async def mobile_confirm_by_tradeofferid(self, tradeofferid: int, login: str) -> bool:
        """
        Mobile confirm by tradeofferid.
        """
        confirmations = await self.get_mobile_confirmations(login)
        for confirmation in confirmations:
            if confirmation.tradeofferid == tradeofferid:
                return await self.mobile_confirm(confirmation, login)
        raise NotFoundMobileConfirmationError(f'Not found confirmation for {tradeofferid}')
