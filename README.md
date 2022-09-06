# Asynchronous python library for work with Steam


## Usage

```
steam = Steam()

# Authenticator data is using for calculating Steam Guard code and mobile confirmations
steam.add_account(
    login='login',
    details=AccountData(
        password='password',
        steamid=123456789,
        authenticator=Authenticator(
            shared_secret='shared_secret',
            device_id='device_id',
            identity_secret='identity_secret',
        )
    )
)
await steam.login_all()
```


## Example sending of exchange

```
api = SteamAPI(steam)

# Sending offer
response = await api.trade.send_offer(
    request=SendOfferRequest(
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
    ),
    login=login,
)

# Confirmation offer in mobile app
if response.needs_mobile_confirmation:
    await api.trade.mobile_confirm_by_tradeofferid(response.tradeofferid, login)
    
# Cancelling offer
await api.trade.cancel_offer(response.tradeofferid, login)
```