# Asynchronous python library for work with Steam

[![pypi: package](https://img.shields.io/badge/pypi-0.0.3-blue)](https://pypi.org/project/pysteamlib/)
[![Python: versions](
https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)]()


## Install

```bash
pip install pysteamlib
```

## Usage

### Account API

```python
from steamlib.api import SteamAPI
from steamlib.api.account import PrivacyInfo
from steamlib.api.account.schemas import ProfileInfo

async def usage(api: SteamAPI):

    current_tradelink: str = await api.account.get_tradelink()
    new_tradelink: str = await api.account.register_tradelink()
    privacy_settings: PrivacyInfo = await api.account.get_current_privacy()
    profile_info: ProfileInfo = await api.account.get_current_profile_info()
    api_key: str = await api.account.register_api_key('example.com')
```

### Trade API

```python
from steamlib.api import SteamAPI
from steamlib.api.trade import Asset, JsonTradeoffer, Me, SendOfferRequest, SendOfferResponse, Them, TradeOfferParams


async def usage(api: SteamAPI):

    response: SendOfferResponse = await api.trade.send_offer(
        request=SendOfferRequest(
            partner=steamid64,
            json_tradeoffer=JsonTradeoffer(
                me=Me(
                    assets=[Asset(appid='730', contextid='2', assetid='123456789')]
                ),
                them=Them(
                    assets=[Asset(appid='730', contextid='2', assetid='987654321')],
                ),
            ),
            sessionid=sessionid,
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

## License

MIT