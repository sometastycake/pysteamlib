import json

from steam.api.trade.errors import SteamNullResponseError
from steam.api.trade.schemas import SendOfferErrorResponse, SendOfferResponse


def send_offer_handler(response: str) -> SendOfferResponse:
    """
    Send offer handler.

    :param response: Send offer response from Steam.
    :return: SendOfferResponse
    """
    if not response or response == 'null':
        raise SteamNullResponseError
    content = json.loads(response)
    if 'strError' in content:
        error = SendOfferErrorResponse.parse_obj(content)
        error.determine_error()
    else:
        return SendOfferResponse.parse_obj(content)
