# Asynchronous python library for work with Steam


## Usage

```
steam = Steam()

# Authenticator data is using for calculating Steam Guard code and mobile confirmations
# If the SG is disabled, then the authenticator data you can lower it

authenticator = Authenticator(
    shared_secret='shared_secret',
    device_id='device_id',
    identity_secret='identity_secret',
)

steam.add_account(
    login='login',
    details=AccountData(
        password='password',
        steamid=123456789,
        authenticator=authenticator
    )
)
await steam.login_all()
```


## Example sending of exchange

```
api = SteamAPI(steam)

# Exchange request scheme
request = SendOfferRequest(
    partner=123456789,
    json_tradeoffer=JsonTradeoffer(
        me=Me(
            assets=[
                Asset(appid='730', contextid='6', assetid='123456789'),
            ],
        ),
        them=Them(
            assets=[
                Asset(appid='730', contextid='2', assetid='123456789'),
            ],
        ),
    ),
    sessionid=await steam.sessionid(login),
    trade_offer_create_params=TradeOfferParams(
        trade_offer_access_token='token'
    ),
)

# Sending offer
response = await api.trade.send_offer(request, login)

# Confirmation offer in mobile app
if response.needs_mobile_confirmation:
    await api.trade.mobile_confirm_by_tradeofferid(response.tradeofferid, login)
    
# Cancelling offer
await api.trade.cancel_offer(response.tradeofferid, login)
```

## Cookie storage

Library uses default cookie storage `BaseCookieStorage`, which stores Steam cookies in application memory.
But you can write own cookie storage. For example, redis storage:

```
class RedisCookieStorage(CookieStorageAbstract):

    redis = Redis()

    async def get(self, login: str) -> Dict:
        cookies = await self.redis.get(login)
        if not cookies:
            return {}
        return json.loads(cookies)

    async def set(self, login: str, cookies: Dict):
        await self.redis.set(login, json.dumps(cookies))

    async def clear(self, login: str) -> None:
        await self.redis.delete(*[login])

steam = Steam(cookie_storage=RedisCookieStorage)
```