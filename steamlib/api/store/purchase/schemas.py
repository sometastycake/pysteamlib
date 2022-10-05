from typing import Optional

from pydantic import BaseModel

from steamlib.schemas import BaseSteamResponse


class PurshaseTransactionRequest(BaseModel):
    gidShoppingCart: int
    gidReplayOfTransID: int = -1
    PaymentMethod: str = 'steamaccount'
    abortPendingTransactions: int = 0
    bHasCardInfo: int = 0
    CardNumber: str = ''
    CardExpirationYear: str = ''
    CardExpirationMonth: str = ''
    FirstName: str = ''
    LastName: str = ''
    Address: str = ''
    AddressTwo: str = ''
    Country: str = ''
    City: str = ''
    State: str = ''
    PostalCode: str = ''
    Phone: str = ''
    ShippingFirstName: str = ''
    ShippingLastName: str = ''
    ShippingAddress: str = ''
    ShippingAddressTwo: str = ''
    ShippingCountry: str = ''
    ShippingCity: str = ''
    ShippingState: str = ''
    ShippingPostalCode: str = ''
    ShippingPhone: str = ''
    bIsGift: int = 0
    GifteeAccountID: int = 0
    GifteeEmail: str = ''
    GifteeName: str = ''
    GiftMessage: str = ''
    Sentiment: str = ''
    Signature: str = ''
    ScheduledSendOnDate: int = 0
    BankAccount: str = ''
    BankCode: str = ''
    BankIBAN: str = ''
    BankBIC: str = ''
    TPBankID: str = ''
    bSaveBillingAddress: int = 1
    gidPaymentID: str = ''
    bUseRemainingSteamAccount: int = 1
    bPreAuthOnly: int = 0
    sessionid: str


class PurshaseTransactionResponse(BaseSteamResponse):
    purchaseresultdetail: int
    paymentmethod: int
    transid: str
    transactionprovider: Optional[int]
    paymentmethodcountrycode: Optional[str]
    pendingpurchasepaymentmethod: Optional[int]


class FinalizeTransactionResponse(BaseSteamResponse):
    purchaseresultdetail: int
    bShowBRSpecificCreditCardError: Optional[bool]


class PurchaseReceipt(BaseModel):
    paymentmethod: int
    purchasestatus: int
    resultdetail: int
    baseprice: str
    totaldiscount: str
    tax: str
    shipping: str
    packageid: int
    transactiontime: int
    transactionid: str
    currencycode: int
    formattedTotal: str
    rewardPointsBalance: str


class TransactionStatusResponse(BaseSteamResponse):
    purchaseresultdetail: int
    purchasereceipt: PurchaseReceipt
    strReceiptPageHTML: str
    bShowBRSpecificCreditCardError: bool


class FinalPriceRequest(BaseModel):
    count: int = 1
    transid: str
    purchasetype: str = 'self'
    microtxnid: int = -1
    cart: int
    gidReplayOfTransID: int = -1


class FinalPriceResponse(BaseSteamResponse):
    purchaseresultdetail: int
    base: str
    tax: str
    discount: str
    shipping: str
    importfee: str
    currencycode: int
    taxtype: int
    providerpaymentmethod: int
    walletcreditchanged: int
    hitminprovideramount: int
    requirecvv: int
    walletcreditlineitems: str
    useexternalredirect: int
    steamAccountTotal: str
    total: int
    steamAccountBalance: str
    formattedProviderRemaining: str
    storeCountryCode: str
    priceOfASubChanged: bool
