from steam.api.trade.handlers import (
    _accept_offer_response_handler,
    _cancel_offer_response_handler,
    _decline_offer_response_handler,
    _send_offer_response_handler,
)
from steam.api.trade.schemas import SendOfferRequest, SendOfferResponse
from steam.auth.steam import Steam


class SteamTrade:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def send_offer(self, request: SendOfferRequest, login: str) -> SendOfferResponse:
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
            raise_for_status=False,
            login=login,
        )
        return _send_offer_response_handler(response)

    async def cancel_offer(self, tradeofferid: int, login: str) -> None:
        """
        Cancel offer.
        """
        response = await self.steam.request(
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
            login=login,
        )
        return _cancel_offer_response_handler(response)

    async def decline_offer(self, tradeofferid: int, login: str) -> None:
        """
        Decline offer.

        :param tradeofferid: Tradeofferid.
        """
        response = await self.steam.request(
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
            login=login,
        )
        return _decline_offer_response_handler(response)

    async def accept_offer(self, tradeofferid: int, partner_steamid: int, login: str) -> int:
        """
        Accept offer.

        :return: Tradeid.
        """
        response = await self.steam.request(
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
