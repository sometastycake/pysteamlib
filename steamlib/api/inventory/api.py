import json
from typing import Dict

from pysteamauth.auth import Steam

from steamlib.api.enums import Language

from .exceptions import NullInventoryError, PrivateInventoryError, UnknownInventoryError


class SteamInventory:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def _inventory(self, appid: str, contextid: int, start: int, language: Language) -> Dict:
        response: str = await self.steam.request(
            url=f'https://steamcommunity.com/profiles/{self.steam.steamid}/inventory/json/{appid}/{contextid}',
            params={
                'l': language.value,
                'start': start,
            },
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.9.5.20) Gecko/2812-12-10 04:56:28 Firefox/3.8',
            },
            raise_for_status=True,
        )
        if response == 'null':
            raise NullInventoryError(steamid=self.steam.steamid, appid=appid)
        return json.loads(response)

    async def get_inventory(self, appid: str, contextid: int, language: Language = Language.english) -> Dict:
        inventory: Dict = {
            'rgInventory': {},
            'rgDescriptions': {},
        }
        start = 0
        while True:
            response = await self._inventory(appid, contextid, start, language)
            if not response['success']:
                error = response.get('Error', '')
                if not error:
                    raise UnknownInventoryError(steamid=self.steam.steamid, appid=appid)
                if error == 'This profile is private.':
                    raise PrivateInventoryError(steamid=self.steam.steamid, appid=appid)
            inventory['rgInventory'].update(response['rgInventory'])
            inventory['rgDescriptions'].update(response['rgDescriptions'])
            if response.get('more'):
                start = response['more_start']
            else:
                break
        return inventory
