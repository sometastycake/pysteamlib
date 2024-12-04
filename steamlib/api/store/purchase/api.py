from typing import Dict

from lxml.html import HtmlElement, document_fromstring
from pysteamauth.auth import Steam

from .schemas import (
    FinalizeTransactionResponse,
    FinalPriceRequest,
    FinalPriceResponse,
    PurshaseTransactionRequest,
    PurshaseTransactionResponse,
    TransactionStatusResponse,
)


class PurchaseGame:

    def __init__(self, steam: Steam, appid: str):
        self.appid = appid
        self.steam = steam

    async def game_page(self) -> HtmlElement:
        response: str = await self.steam.request(
            url=f'https://store.steampowered.com/app/{self.appid}/',
        )
        return document_fromstring(response)

    async def get_data_for_cart(self) -> Dict:
        page: HtmlElement = await self.game_page()
        result = {}
        for param in ('snr', 'originating_snr', 'action', 'sessionid', 'subid'):
            result[param] = page.cssselect(f'input[name="{param}"]')[0].attrib['value']
        return result

    async def add_to_cart(self) -> int:
        cart_data = await self.get_data_for_cart()
        response: str = await self.steam.request(
            method='POST',
            url='https://store.steampowered.com/cart/',
            data=cart_data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://store.steampowered.com',
                'Referer': f'https://store.steampowered.com/app/{self.appid}',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.9.5.20) Gecko/2812-12-10 04:56:28 Firefox/3.8',
            },
        )
        page: HtmlElement = document_fromstring(response)
        return int(page.cssselect('.cart_area_body input[name="cart"]')[0].attrib['value'])

    async def init_transaction(self, request: PurshaseTransactionRequest) -> PurshaseTransactionResponse:
        response: str = await self.steam.request(
            method='POST',
            url='https://store.steampowered.com/checkout/inittransaction/',
            data=request.dict(),
            headers={
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://store.steampowered.com',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Prototype-Version:': '1.7',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.9.5.20) Gecko/2812-12-10 04:56:28 Firefox/3.8',
            },
        )
        return PurshaseTransactionResponse.parse_raw(response)

    async def finalize_transaction(self, transid: str) -> FinalizeTransactionResponse:
        response: str = await self.steam.request(
            method='POST',
            url='https://store.steampowered.com/checkout/finalizetransaction/',
            data={
                'transid': transid,
                'CardCVV2': '',
            },
            headers={
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://store.steampowered.com',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Prototype-Version:': '1.7',
                'Referer': 'https://store.steampowered.com/checkout/?purchasetype=self',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.9.5.20) Gecko/2812-12-10 04:56:28 Firefox/3.8',
            },
        )
        return FinalizeTransactionResponse.parse_raw(response)

    async def transaction_status(self, transid: str) -> TransactionStatusResponse:
        response: str = await self.steam.request(
            method='POST',
            url='https://store.steampowered.com/checkout/transactionstatus/',
            data={
                'count': '1',
                'transid': transid,
            },
            headers={
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://store.steampowered.com',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Prototype-Version:': '1.7',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.9.5.20) Gecko/2812-12-10 04:56:28 Firefox/3.8',
            },
        )
        return TransactionStatusResponse.parse_raw(response)

    async def final_price(self, request: FinalPriceRequest) -> FinalPriceResponse:
        response: str = await self.steam.request(
            url='https://store.steampowered.com/checkout/getfinalprice/',
            method='GET',
            params=request.dict(),
            headers={
                'Referer': 'https://store.steampowered.com/checkout/?purchasetype=self',
                'X-Prototype-Version': '1.7',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.9.5.20) Gecko/2812-12-10 04:56:28 Firefox/3.8',
            },
        )
        return FinalPriceResponse.parse_raw(response)

    async def purchase(self) -> TransactionStatusResponse:
        cart_number: int = await self.add_to_cart()
        transaction: PurshaseTransactionResponse = await self.init_transaction(
            request=PurshaseTransactionRequest(
                gidShoppingCart=cart_number,
                sessionid=await self.steam.sessionid(domain='store.steampowered.com'),
            ),
        )
        await self.final_price(
            request=FinalPriceRequest(
                cart=cart_number,
                transid=transaction.transid,
            ),
        )
        await self.finalize_transaction(transaction.transid)
        return await self.transaction_status(transaction.transid)
