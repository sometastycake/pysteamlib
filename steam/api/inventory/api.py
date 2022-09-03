import json
from typing import Dict

from steam.api.inventory.exc import NullInventoryError, PrivateInventoryError, UnknownInventoryError
from steam.auth.steam import Steam


class SteamInventory:

    def __init__(self, steam: Steam):
        self.steam = steam

    async def _inventory(self, steamid: int, appid: str, contextid: int = 2, start: int = 0) -> Dict:
        """
        Get inventory from Steam.

        :return: Inventory.
        """
        response = await self.steam.http.request(
            url=f'https://steamcommunity.com/profiles/{steamid}/inventory/json/{appid}/{contextid}',
            params={
                'l': 'english',
                'start': start,
            },
            headers={
                'Content-Type': 'application/json',
            },
        )
        if response == 'null':
            raise NullInventoryError(steamid=steamid, appid=appid)
        return json.loads(response)

    async def get_inventory(self, steamid: int, appid: str, contextid: int = 2):
        """
        Get inventory.

        :return: Inventory.
        """
        inventory: Dict = {
            'rgInventory': {},
            'rgDescriptions': {},
        }
        start = 0
        while True:
            response = await self._inventory(steamid, appid, contextid, start)
            if not response['success']:
                error = response.get('Error', '')
                if not error:
                    raise UnknownInventoryError(steamid=steamid, appid=appid)
                if error == 'This profile is private.':
                    raise PrivateInventoryError(steamid=steamid, appid=appid)
            inventory['rgInventory'].update(response['rgInventory'])
            inventory['rgDescriptions'].update(response['rgDescriptions'])
            if response['more']:
                start = response['more_start']
            else:
                break
        return inventory
