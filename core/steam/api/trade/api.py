from steam.api.account.api import SteamAccountAPI
from steam.api.trade.callbacks import send_offer_handler, cancel_offer_handler
from steam.api.trade.schemas import SendOfferRequest, SendOfferResponse
from steam.auth.steam import Steam


class SteamTradeAPI:

    def __init__(self, steam: Steam):
        self.steam = steam
        self.account_api = SteamAccountAPI(steam)

    async def send_offer(self, request: SendOfferRequest) -> SendOfferResponse:
        """
        Send offer.

        :param request: Send offer request data.
        :return: Offer status.
        """
        return await self.steam.request(
            method='POST',
            url='https://steamcommunity.com/tradeoffer/new/send',
            data=request.to_request(),
            headers={
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://steamcommunity.com',
                'Referer': request.tradelink(),
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/'
                              '537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            },
            callback=send_offer_handler,
            raise_for_status=False,
        )

    async def cancel_offer(self, tradeofferid: int) -> None:
        """
        Cancel offer.

        :param tradeofferid: Tradeofferid.
        """
        return await self.steam.request(
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
            callback=cancel_offer_handler,
        )
