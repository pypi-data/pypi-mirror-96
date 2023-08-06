from .memoryHistoryStorageModel import MemoryHistoryStorageModel
import json
import os
import asyncio
from .models import format_date, convert_iso_time_to_date
from typing import List
from datetime import datetime
from copy import deepcopy


def stringify(obj: dict or List) -> str:
    """Helper function to convert an object to string and compress.

    Returns:
        Stringified and compressed object.
    """
    return json.dumps(obj).replace('": ', '":').replace('}, {', '},{').replace(', "', ',"')


class HistoryFileManager:
    """History storage file manager which saves and loads history on disk."""

    def __init__(self, account_id: str, application: str, history_storage: MemoryHistoryStorageModel = None):
        """Constructs the history file manager instance."""
        self._accountId = account_id
        self._application = application
        self._historyStorage = history_storage
        self._dealsSize = []
        self._startNewDealIndex = -1
        self._historyOrdersSize = []
        self._startNewOrderIndex = -1
        self.update_disk_storage_job = None
        self._isUpdating = False

    def start_update_job(self):
        """Starts a job to periodically save history on disk"""

        async def update_job():
            while True:
                await asyncio.sleep(60)
                await self.update_disk_storage()

        if not self.update_disk_storage_job:
            self.update_disk_storage_job = asyncio.create_task(update_job())

    def stop_update_job(self):
        """Stops a job to periodically save history on disk."""

        self.update_disk_storage_job.cancel()
        self.update_disk_storage_job = None

    def get_item_size(self, item: dict) -> int:
        """Helper function to calculate object size in bytes in utf-8 encoding.

        Returns:
            Size of object in bytes.
        """
        return len(stringify(item).encode('utf-8'))

    def set_start_new_order_index(self, index: int):
        """Sets the index of the earliest changed historyOrder record.

        Args:
            index: Index of the earliest changed record.
        """
        if self._startNewOrderIndex > index or self._startNewOrderIndex == -1:
            self._startNewOrderIndex = index

    def set_start_new_deal_index(self, index: int):
        """Sets the index of the earliest changed deal record.

        Args:
            index: Index of the earliest changed record.
        """
        if self._startNewDealIndex > index or self._startNewDealIndex == -1:
            self._startNewDealIndex = index

    async def get_history_from_disk(self):
        """Retrieves history from saved file.

        Returns:
            A coroutine resolving with an object with deals and historyOrders.
        """

        history = {
            'deals': [],
            'historyOrders': [],
            'lastDealTimeByInstanceIndex': {},
            'lastHistoryOrderTimeByInstanceIndex': {}
        }
        try:
            if os.path.isfile(f'.metaapi/{self._accountId}-{self._application}-config.bin'):
                config = json.loads(open(f'.metaapi/{self._accountId}-{self._application}-config.bin').read())
                history['lastDealTimeByInstanceIndex'] = config['lastDealTimeByInstanceIndex']
                history['lastHistoryOrderTimeByInstanceIndex'] = config['lastHistoryOrderTimeByInstanceIndex']
        except Exception as err:
            print(f'[{datetime.now().isoformat()}] Failed to read history storage config of '
                  f'account {self._accountId}', err)
            os.remove(f'.metaapi/{self._accountId}-{self._application}-config.bin')

        try:
            if os.path.isfile(f'.metaapi/{self._accountId}-{self._application}-deals.bin'):
                deals = json.loads(open(f'.metaapi/{self._accountId}-{self._application}-deals.bin').read())
                self._dealsSize = list(map(self.get_item_size, deals))
                for deal in deals:
                    convert_iso_time_to_date(deal)
                history['deals'] = deals
        except Exception as err:
            print(f'[{datetime.now().isoformat()}] Failed to read deals history storage of '
                  f'account {self._accountId}', err)
            os.remove(f'.metaapi/{self._accountId}-{self._application}-deals.bin')

        try:
            if os.path.isfile(f'.metaapi/{self._accountId}-{self._application}-historyOrders.bin'):
                history_orders = json.loads(open(f'.metaapi/{self._accountId}-{self._application}-historyOrders.bin')
                                            .read())
                self._historyOrdersSize = list(map(self.get_item_size, history_orders))
                for history_order in history_orders:
                    convert_iso_time_to_date(history_order)
                history['historyOrders'] = history_orders
        except Exception as err:
            print(f'[{datetime.now().isoformat()}] Failed to read historyOrders history storage of '
                  f'account {self._accountId}', err)
            os.remove(f'.metaapi/{self._accountId}-{self._application}-historyOrders.bin')
        return history

    async def update_disk_storage(self):
        """Saves unsaved history items to disk storage.

        Returns:
            A coroutine resolving when the history is saved to disk.
        """
        account_id = self._accountId
        application = self._application
        if not os.path.exists('.metaapi'):
            os.mkdir('.metaapi')

        async def replace_records(history_type, start_index: int, replace_items: List, size_array: List) -> List[int]:
            replace_items = self._prepare_save_data(replace_items)
            file_path = f'.metaapi/{account_id}-{application}-{history_type}.bin'
            file_size = os.path.getsize(file_path)
            if start_index == 0:
                f = open(file_path, 'w+')
                f.write(stringify(replace_items))
                f.close()
            else:
                f = open(file_path, 'a+')
                replaced_items = size_array[start_index:]
                start_position = file_size - len(replaced_items) - sum(replaced_items) - 1
                f.seek(start_position)
                f.truncate()
                f.close()
                f = open(file_path, "a+")
                f.write(',' + stringify(replace_items)[1:])
                f.close()
            return size_array[0:start_index] + list(map(self.get_item_size, replace_items))

        if not self._isUpdating:
            self._isUpdating = True
            try:
                await self._update_config()
                if self._startNewDealIndex != -1:
                    if not os.path.isfile(f'.metaapi/{account_id}-{application}-deals.bin'):
                        try:
                            f = open(f'.metaapi/{account_id}-{application}-deals.bin', "w+")
                            f.write(stringify(self._prepare_save_data(self._historyStorage.deals)))
                            f.close()
                        except Exception as err:
                            print(f'[{datetime.now().isoformat()}] Error saving deals on disk for account '
                                  f'{self._accountId}', err)
                        self._dealsSize = list(map(self.get_item_size,
                                                   self._prepare_save_data(self._historyStorage.deals)))
                    else:
                        replace_deals = self._historyStorage.deals[self._startNewDealIndex:]
                        self._dealsSize = await replace_records('deals', self._startNewDealIndex, replace_deals,
                                                                self._dealsSize)
                    self._startNewDealIndex = -1

                if self._startNewOrderIndex != -1:
                    if not os.path.isfile(f'.metaapi/{account_id}-{application}-historyOrders.bin'):
                        try:
                            f = open(f'.metaapi/{account_id}-{application}-historyOrders.bin', "w+")
                            f.write(stringify(self._prepare_save_data(self._historyStorage.history_orders)))
                            f.close()
                        except Exception as err:
                            print(f'[{datetime.now().isoformat()}] Error saving historyOrders on disk for '
                                  f'account {account_id}', err)
                        self._historyOrdersSize = list(map(
                            self.get_item_size, self._prepare_save_data(self._historyStorage.history_orders)))
                    else:
                        replace_orders = self._historyStorage.history_orders[self._startNewOrderIndex:]
                        self._historyOrdersSize = await replace_records('historyOrders', self._startNewOrderIndex,
                                                                        replace_orders, self._historyOrdersSize)
                    self._startNewOrderIndex = -1
            except Exception as err:
                print(f'[{datetime.now().isoformat()}] Error updating disk storage for '
                      f'account {account_id}', err)
            self._isUpdating = False

    async def _update_config(self):
        """Updates stored config for account."""
        account_id = self._accountId
        history_storage = self._historyStorage
        file_path = f'.metaapi/{account_id}-{self._application}-config.bin'
        try:
            config = {
                'lastDealTimeByInstanceIndex': history_storage.last_deal_time_by_instance_index,
                'lastHistoryOrderTimeByInstanceIndex': history_storage.last_history_order_time_by_instance_index
            }
            f = open(file_path, 'w+')
            f.write(stringify(config))
            f.close()
        except Exception as err:
            print(f'[{datetime.now().isoformat()}] Error updating disk storage config for '
                  f'account {account_id}', err)

    async def delete_storage_from_disk(self):
        """Deletes storage files from disk.

        Returns:
            A coroutine resolving when the history is deleted from disk.
        """
        if os.path.isfile(f'.metaapi/{self._accountId}-{self._application}-config.bin'):
            os.remove(f'.metaapi/{self._accountId}-{self._application}-config.bin')
        if os.path.isfile(f'.metaapi/{self._accountId}-{self._application}-deals.bin'):
            os.remove(f'.metaapi/{self._accountId}-{self._application}-deals.bin')
        if os.path.isfile(f'.metaapi/{self._accountId}-{self._application}-historyOrders.bin'):
            os.remove(f'.metaapi/{self._accountId}-{self._application}-historyOrders.bin')

    def _prepare_save_data(self, arr: List[dict]):
        arr = deepcopy(arr)

        def convert_dates(item):
            for key in item:
                if isinstance(item[key], datetime):
                    item[key] = format_date(item[key])
                elif isinstance(item[key], dict):
                    convert_dates(item[key])

        for item in arr:
            convert_dates(item)
        return arr
