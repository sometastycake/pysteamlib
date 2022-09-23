from typing import Dict

from lxml.html import HtmlElement, document_fromstring
from pysteamauth.auth import Steam

from steamlib.api.account.api import SteamAccount
from steamlib.api.store.purchase.schemas import (
    FinalizeTransactionResponse,
    FinalPriceRequest,
    FinalPriceResponse,
    PurshaseTransactionRequest,
    PurshaseTransactionResponse,
    TransactionStatusResponse,
)


class PurchaseGame:

    def __init__(self, steam: Steam, game: str, appid: int):
        self.game = game
        self.appid = appid
        self.steam = steam
        self.account_api = SteamAccount(steam)

    async def game_page(self) -> HtmlElement:
        """
        Get game page.

        :return: Parsed html page.
        """
        response = await self.steam.request(
            url=f'https://store.steampowered.com/app/{self.appid}',
        )
        return document_fromstring(response)

    async def get_data_for_cart(self) -> Dict:
        """
        Get data for cart.

        :return: Data for game adding to cart.
        """
        page = await self.game_page()
        result = {}
        for param in ('snr', 'originating_snr', 'action', 'sessionid', 'subid'):
            result[param] = page.cssselect(f'input[name="{param}"]')[0].attrib['value']
        return result

    async def add_to_cart(self) -> int:
        """
        Add game to cart.

        :return: Cart number.
        """
        response = await self.steam.request(
            method='POST',
            url='https://store.steampowered.com/cart/',
            data=await self.get_data_for_cart(),
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://store.steampowered.com',
                'Referer': f'https://store.steampowered.com/app/{self.appid}/{self.game}/',
            },
        )
        page: HtmlElement = document_fromstring(response)
        return int(page.cssselect('.cart_area_body input[name="cart"]')[0].attrib['value'])

    async def init_transaction(self, request: PurshaseTransactionRequest) -> PurshaseTransactionResponse:
        """
        Init purshase transaction.

        :return: Transaction data.
        """
        response = await self.steam.request(
            method='POST',
            url='https://store.steampowered.com/checkout/inittransaction/',
            data=request.dict(),
            headers={
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://store.steampowered.com',
                'X-Requested-With': 'XMLHttpRequest',
                'X-Prototype-Version:': '1.7',
            },
            response_model=PurshaseTransactionResponse,
        )
        result = PurshaseTransactionResponse.parse_raw(response)
        result.check_error()
        return result

    async def finalize_transaction(self, transid: str) -> FinalizeTransactionResponse:
        """
        Finalize transaction.

        :return: Finalize transaction status.
        """
        response = await self.steam.request(
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
            },
        )
        result = FinalizeTransactionResponse.parse_raw(response)
        result.check_error()
        return result

    async def transaction_status(self, transid: str) -> TransactionStatusResponse:
        """
        Check transaction status.

        :return: Transaction status.
        """
        response = await self.steam.request(
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
            },
        )
        result = TransactionStatusResponse.parse_raw(response)
        result.check_error()
        return result

    async def final_price(self, request: FinalPriceRequest) -> FinalPriceResponse:
        """
        Steam request "get_final_price".

        :return: Final price status.
        """
        response = await self.steam.request(
            url='https://store.steampowered.com/checkout/getfinalprice/',
            method='GET',
            params=request.dict(),
            headers={
                'Referer': 'https://store.steampowered.com/checkout/?purchasetype=self',
                'X-Prototype-Version': '1.7',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
            },
        )
        result = FinalPriceResponse.parse_raw(response)
        result.check_error()
        return result

    async def purchase(self) -> None:
        """
        Purshase game.
        """
        cart_number = await self.add_to_cart()
        transaction = await self.init_transaction(
            request=PurshaseTransactionRequest(
                gidShoppingCart=cart_number,
                sessionid=await self.steam.sessionid(),
            ),
        )
        await self.final_price(
            request=FinalPriceRequest(
                cart=cart_number,
                transid=transaction.transid,
            ),
        )
        await self.finalize_transaction(transaction.transid)
        await self.transaction_status(transaction.transid)
