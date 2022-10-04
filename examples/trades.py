from typing import List

from pysteamauth.auth import Steam
from yarl import URL

from steamlib.api import SteamAPI
from steamlib.api.trade import (
    AcceptOfferResponse,
    Asset,
    JsonTradeoffer,
    Me,
    SendOfferRequest,
    SendOfferResponse,
    Them,
    TradeOfferParams,
)


class SendOfferExample:

    def __init__(self, sender: Steam, receiver: Steam):
        self.sender = sender
        self.receiver = receiver
        self.sender_api = SteamAPI(sender)
        self.receiver_api = SteamAPI(receiver)

    async def get_tradelink_token_of_receiver(self) -> str:
        return URL(
            val=await self.receiver_api.account.get_tradelink()
        ).query.get('token')

    async def send_offer(self, receiver_assets: List[Asset], sender_assets: List[Asset]) -> SendOfferResponse:
        return await self.sender_api.trade.send_offer(
            request=SendOfferRequest(
                partner=self.receiver.steamid,
                json_tradeoffer=JsonTradeoffer(
                    me=Me(
                        assets=sender_assets,
                    ),
                    them=Them(
                        assets=receiver_assets,
                    ),
                ),
                sessionid=await self.sender.sessionid(),
                trade_offer_create_params=TradeOfferParams(
                    trade_offer_access_token=await self.get_tradelink_token_of_receiver(),
                ),
            ),
        )

    async def mobile_confirm(self, api: SteamAPI, tradeofferid: int) -> bool:
        return await api.trade.mobile_confirm_by_tradeofferid(
            tradeofferid=tradeofferid,
        )

    async def trade(self, receiver_assets: List[Asset], sender_assets: List[Asset]) -> None:

        if not await self.sender.is_authorized():
            await self.sender.login_to_steam()
        if not await self.receiver.is_authorized():
            await self.receiver.login_to_steam()

        # Send offer to Steam
        status_of_send_offer: SendOfferResponse = await self.send_offer(
            receiver_assets=receiver_assets,
            sender_assets=sender_assets,
        )
        tradeofferid = status_of_send_offer.tradeofferid

        # Confirm send offer in mobile app
        if status_of_send_offer.needs_mobile_confirmation:
            confirmation: bool = await self.mobile_confirm(
                api=self.sender_api,
                tradeofferid=tradeofferid,
            )
            if not confirmation:
                raise RuntimeError('Confirmation failed from the sender side')

        # Accept offer from the receiver side
        status_of_accept_offer: AcceptOfferResponse = await self.receiver_api.trade.accept_offer(
            tradeofferid=tradeofferid,
            partner_steamid=self.sender.steamid
        )
        # Confirm sending own assets in mobile app
        if status_of_accept_offer.needs_mobile_confirmation:
            confirmation: bool = await self.mobile_confirm(
                api=self.receiver_api,
                tradeofferid=tradeofferid,
            )
            if not confirmation:
                raise RuntimeError('Confirmation failed from the receiver side')
