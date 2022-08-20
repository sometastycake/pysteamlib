from steam.api.trade.callbacks import send_offer_handler
from steam.api.trade.schemas import SendOfferRequest, SendOfferResponse
from steam.auth.steam import Steam


class SteamTradeAPI:

    def __init__(self, steam: Steam):
        self.steam = steam

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
