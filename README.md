# Asynchronous python library for work with Steam

[![pypi: package](https://img.shields.io/badge/pypi-1.0.0-blue)](https://pypi.org/project/pysteamlib/)
[![Python: versions](
https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)]()


## Install

```bash
pip install pysteamlib
```

## Usage


### Getting started

```python
from pysteamauth.auth import Steam
from steamlib.api import SteamAPI

steam = Steam(
    login='login',
    password='password',
    shared_secret='shared_secret',
    identity_secret='identity_secret',
    device_id='device_id',
)
await steam.login_to_steam()
api = SteamAPI(steam)
```

### Account API

```python
from steamlib.api import SteamAPI
from steamlib.api.account import PrivacyInfo
from steamlib.api.account.schemas import ProfileInfo

async def usage(api: SteamAPI):

    # Get current tradelink
    current_tradelink: str = await api.account.get_tradelink()
    
    # Register new tradelink
    new_tradelink: str = await api.account.register_tradelink()
    
    # Privacy settings
    privacy_settings: PrivacyInfo = await api.account.get_current_privacy()
    
    # Get profile info
    profile_info: ProfileInfo = await api.account.get_current_profile_info()
    
    # Register api key
    api_key: str = await api.account.register_api_key('example.com')
```

### Trade API

```python
from steamlib.api import SteamAPI
from steamlib.api.trade import Asset, JsonTradeoffer, SendOfferRequest


async def usage(api: SteamAPI):

    response = await api.trade.send_offer(
        request=SendOfferRequest(
            partner=steamid,
            tradelink='tradelink',
            me=[
                Asset(
                    appid='appid',
                    contextid='contextid',
                    amount=1,
                    assetid='assetid',
                ),
            ],
            them=[],
        ),
    )
    if error := response.get('strError'):
        print('Send offer error:', error)
        return
    tradeofferid = response['tradeofferid']
    await api.trade.mobile_confirm_by_creator_id(tradeofferid)
    await api.trade.cancel_offer(tradeofferid)
```

## License

MIT