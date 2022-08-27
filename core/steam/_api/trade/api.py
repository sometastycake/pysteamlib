from steam._api.account.api import SteamAccount
from steam._api.trade.handlers import (
    _accept_offer_response_handler,
    _cancel_offer_response_handler,
    _decline_offer_response_handler,
    _send_offer_response_handler,
)
from steam._api.trade.schemas import SendOfferRequest, SendOfferResponse
from steam.auth.steam import Steam


class SteamTrade:

    def __init__(self, steam: Steam, account_api: SteamAccount):
        self.steam = steam
        self.account_api = account_api

    async def send_offer(self, request: SendOfferRequest) -> SendOfferResponse:
        """
        Send offer.

        :param request: Send offer request data.
        :return: Offer status.
        """
        response = await self.steam.request(
            method='POST',
            url='https://steamcommunity.com/tradeoffer/new/send',
            data=request.to_request(),
            headers={
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': request.tradelink(),
            },
            raise_for_status=False,
        )
        return _send_offer_response_handler(response)

    async def cancel_offer(self, tradeofferid: int) -> None:
        """
        Cancel offer.

        :param tradeofferid: Tradeofferid.
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
                'Referer': f'https://steamcommunity.com/profiles/{await self.account_api.steamid}/tradeoffers/sent/',
            },
            raise_for_status=False,
        )
        return _cancel_offer_response_handler(response)

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
                'Referer': f'https://steamcommunity.com/profiles/{await self.account_api.steamid}/tradeoffers/',
            },
            raise_for_status=False,
        )
        return _decline_offer_response_handler(response)

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
            raise_for_status=False,
        )
        return _accept_offer_response_handler(response)
