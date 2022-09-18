from enum import Enum


class OfferState(Enum):
    send = 'send'
    accept = 'accept'
    decline = 'decline'
    cancel = 'cancel'
