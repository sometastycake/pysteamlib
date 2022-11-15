# Asynchronous python library for work with Steam

[![pypi: package](https://img.shields.io/badge/pypi-0.0.2-blue)](https://pypi.org/project/pysteamlib/)
[![Imports: isort](https://img.shields.io/badge/imports-isort-success)](https://pycqa.github.io/isort/)
[![Linter: flake8](https://img.shields.io/badge/linter-flake8-success)](https://github.com/PyCQA/flake8)
[![Mypy: checked](https://img.shields.io/badge/mypy-checked-success)](https://github.com/python/mypy)
[![Python: versions](
https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)]()


## Install

```bash
pip install pysteamlib
```

## Usage

```python
from typing import Dict

from pysteamauth.auth import Steam
from steamlib.api import SteamAPI
from steamlib.api.account import PrivacyInfo
from steamlib.api.account.schemas import ProfileInfo
from steamlib.api.store.purchase import TransactionStatusResponse
from steamlib.api.trade import Asset, JsonTradeoffer, Me, SendOfferRequest, SendOfferResponse, Them, TradeOfferParams


async def usage(steam: Steam) -> None:

    if not await steam.is_authorized():
        await steam.login_to_steam()

    api = SteamAPI(steam)

    # Store
    purchase_status: TransactionStatusResponse = await api.store.purchase_game(appid='808080')

    # Account
    current_tradelink: str = await api.account.get_tradelink()
    new_tradelink: str = await api.account.register_tradelink()
    privacy_settings: PrivacyInfo = await api.account.get_current_privacy()
    profile_info: ProfileInfo = await api.account.get_current_profile_info()
    api_key: str = await api.account.register_api_key('example.com')

    # Inventory
    inventory: Dict = await api.inventory.get_inventory(appid='730', contextid=2)

    # Trade
    response: SendOfferResponse = await api.trade.send_offer(
        request=SendOfferRequest(
            partner=76561111111111111,
            json_tradeoffer=JsonTradeoffer(
                me=Me(
                    assets=[Asset(appid='730', contextid='2', assetid='111111111111')]
                ),
                them=Them(
                    assets=[Asset(appid='730', contextid='2', assetid='111111111111')],
                ),
            ),
            sessionid=await steam.sessionid(),
            trade_offer_create_params=TradeOfferParams(
                trade_offer_access_token='token',
            ),
        ),
    )
    
    if response.needs_mobile_confirmation:
        confirmation_result: bool = await api.trade.mobile_confirm_by_tradeofferid(
            tradeofferid=response.tradeofferid,
        )
```
