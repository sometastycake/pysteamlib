from typing import Dict

from session import Session

from steam._api.inventory.exceptions import PrivateInventoryError, UnknownInventoryError


class SteamInventory(Session):

    async def _inventory(self, steamid: int, appid: str, contextid: int = 2, start: int = 0) -> Dict:
        """
        Get inventory from Steam.

        :return: Inventory.
        """
        response = await self.session.get(
            url=f'https://steamcommunity.com/profiles/{steamid}/inventory/json/{appid}/{contextid}',
            params={
                'l': 'english',
                'start': start,
            },
            headers={
                'Content-Type': 'application/json',
            },
        )
        return await response.json()

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
                    raise UnknownInventoryError
                if error == 'This profile is private.':
                    raise PrivateInventoryError
            inventory['rgInventory'].update(response['rgInventory'])
            inventory['rgDescriptions'].update(response['rgDescriptions'])
            if response['more']:
                start = response['more_start']
            else:
                break
        return inventory
