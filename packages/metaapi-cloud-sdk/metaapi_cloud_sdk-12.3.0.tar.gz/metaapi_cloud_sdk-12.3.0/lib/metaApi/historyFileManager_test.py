from asyncio import sleep, gather
from ..metaApi.historyFileManager import HistoryFileManager
from .memoryHistoryStorageModel import MemoryHistoryStorageModel
import pytest
import json
import os
from mock import AsyncMock, patch
from datetime import datetime
from copy import deepcopy
from .models import date
import shutil
file_manager: HistoryFileManager or None = None
storage = None
test_deal = None
test_deal2 = None
test_deal3 = None
test_order = None
test_order2 = None
test_order3 = None
test_config = None


class MockStorage(MemoryHistoryStorageModel):

    def __init__(self):
        super().__init__()
        self._deals = []
        self._historyOrders = []
        self._lastDealTimeByInstanceIndex = {}
        self._lastHistoryOrderTimeByInstanceIndex = {}

    @property
    def deals(self):
        return self._deals

    @property
    def history_orders(self):
        return self._historyOrders

    @property
    def last_deal_time_by_instance_index(self) -> dict:
        return self._lastDealTimeByInstanceIndex

    @property
    def last_history_order_time_by_instance_index(self) -> dict:
        return self._lastHistoryOrderTimeByInstanceIndex

    async def clear(self):
        pass

    def last_deal_time(self):
        pass

    def last_history_order_time(self):
        pass

    def on_deal_added(self, deal):
        pass

    def on_history_order_added(self, order):
        pass


async def read_history_storage_file():
    """Helper function to read saved history storage."""
    history = {
        'deals': [],
        'historyOrders': [],
        'lastDealTimeByInstanceIndex': {},
        'lastHistoryOrderTimeByInstanceIndex': {}
    }
    if os.path.isfile('.metaapi/accountId-application-config.bin'):
        config = json.loads(open('.metaapi/accountId-application-config.bin').read())
        history['lastDealTimeByInstanceIndex'] = config['lastDealTimeByInstanceIndex']
        history['lastHistoryOrderTimeByInstanceIndex'] = config['lastHistoryOrderTimeByInstanceIndex']
    if os.path.isfile('.metaapi/accountId-application-deals.bin'):
        history['deals'] = json.loads(open('.metaapi/accountId-application-deals.bin').read())
    if os.path.isfile('.metaapi/accountId-application-historyOrders.bin'):
        history['historyOrders'] = json.loads(open('.metaapi/accountId-application-historyOrders.bin').read())
    return history


@pytest.fixture(scope="module", autouse=True)
def run_around_module():
    if not os.path.exists('.metaapi'):
        os.mkdir('.metaapi')
    yield
    shutil.rmtree('.metaapi')


@pytest.fixture(autouse=True)
async def run_around_tests():
    global storage
    storage = MockStorage()
    global file_manager
    file_manager = HistoryFileManager('accountId', 'application', storage)
    global test_deal
    test_deal = {'id': '37863643', 'type': 'DEAL_TYPE_BALANCE', 'magic': 0, 'time':
                 datetime.fromtimestamp(100).isoformat(),
                 'commission': 0, 'swap': 0, 'profit': 10000, 'platform': 'mt5', 'comment': 'Demo deposit 1'}
    global test_deal2
    test_deal2 = {'id': '37863644', 'type': 'DEAL_TYPE_SELL', 'magic': 1, 'time':
                  datetime.fromtimestamp(200).isoformat(),
                  'commission': 0, 'swap': 0, 'profit': 10000, 'platform': 'mt5', 'comment': 'Demo deposit 2'}
    global test_deal3
    test_deal3 = {'id': '37863645', 'type': 'DEAL_TYPE_BUY', 'magic': 2, 'time':
                  datetime.fromtimestamp(300).isoformat(),
                  'commission': 0, 'swap': 0, 'profit': 10000, 'platform': 'mt5', 'comment': 'Demo deposit 3'}
    global test_order
    test_order = {'id': '61210463', 'type': 'ORDER_TYPE_SELL', 'state': 'ORDER_STATE_FILLED', 'symbol': 'AUDNZD',
                  'magic': 0, 'time': datetime.fromtimestamp(50).isoformat(), 'doneTime':
                  datetime.fromtimestamp(100).isoformat(), 'currentPrice': 1, 'volume': 0.01, 'currentVolume': 0,
                  'positionId': '61206630', 'platform': 'mt5', 'comment': 'AS_AUDNZD_5YyM6KS7Fv:'}
    global test_order2
    test_order2 = {'id': '61210464', 'type': 'ORDER_TYPE_BUY_LIMIT', 'state': 'ORDER_STATE_FILLED', 'symbol': 'AUDNZD',
                   'magic': 1, 'time': datetime.fromtimestamp(75).isoformat(), 'doneTime':
                   datetime.fromtimestamp(200).isoformat(), 'currentPrice': 1, 'volume': 0.01, 'currentVolume': 0,
                   'positionId': '61206631', 'platform': 'mt5', 'comment': 'AS_AUDNZD_5YyM6KS7Fv:'}
    global test_order3
    test_order3 = {'id': '61210465', 'type': 'ORDER_TYPE_BUY', 'state': 'ORDER_STATE_FILLED', 'symbol': 'AUDNZD',
                   'magic': 2, 'time': datetime.fromtimestamp(100).isoformat(), 'doneTime':
                   datetime.fromtimestamp(300).isoformat(), 'currentPrice': 1, 'volume': 0.01, 'currentVolume': 0,
                   'positionId': '61206632', 'platform': 'mt5', 'comment': 'AS_AUDNZD_5YyM6KS7Fv:'}
    global test_config
    test_config = {
        'lastDealTimeByInstanceIndex': {'0': 1000000000000},
        'lastHistoryOrderTimeByInstanceIndex': {'0': 1000000000010}
    }
    yield
    if os.path.isfile('.metaapi/accountId-application-deals.bin'):
        os.remove('.metaapi/accountId-application-deals.bin')
    if os.path.isfile('.metaapi/accountId-application-historyOrders.bin'):
        os.remove('.metaapi/accountId-application-historyOrders.bin')


class TestHistoryFileManager:

    @pytest.mark.asyncio
    async def test_start_stop_job(self):
        """Should start and stop job."""

        with patch.object(file_manager, 'update_disk_storage', new_callable=AsyncMock):
            with patch('lib.metaApi.historyFileManager.asyncio.sleep', new=lambda x: sleep(x/120)):
                file_manager.update_disk_storage = AsyncMock()
                file_manager.start_update_job()
                await sleep(0.6)
                assert file_manager.update_disk_storage.call_count == 1
                await sleep(0.6)
                assert file_manager.update_disk_storage.call_count == 2
                file_manager.stop_update_job()
                await sleep(0.6)
                assert file_manager.update_disk_storage.call_count == 2
                file_manager.start_update_job()
                await sleep(0.7)
                assert file_manager.update_disk_storage.call_count == 3
                file_manager.stop_update_job()

    @pytest.mark.asyncio
    async def test_read_history(self):
        """Should read history from file."""

        f = open('.metaapi/accountId-application-deals.bin', "w+")
        f.write(json.dumps([test_deal]))
        f.close()

        f = open('.metaapi/accountId-application-historyOrders.bin', "w+")
        f.write(json.dumps([test_order]))
        f.close()

        f = open('.metaapi/accountId-application-config.bin', "w+")
        f.write(json.dumps(test_config))
        f.close()

        history = await file_manager.get_history_from_disk()
        expected_deal = deepcopy(test_deal)
        expected_deal['time'] = date(expected_deal['time'])
        assert history['deals'] == [expected_deal]
        expected_order = deepcopy(test_order)
        expected_order['time'] = date(expected_order['time'])
        expected_order['doneTime'] = date(expected_order['doneTime'])
        assert history['historyOrders'] == [expected_order]
        assert history['lastDealTimeByInstanceIndex'] == test_config['lastDealTimeByInstanceIndex']
        assert history['lastHistoryOrderTimeByInstanceIndex'] == test_config['lastHistoryOrderTimeByInstanceIndex']

    @pytest.mark.asyncio
    async def test_save_items(self):
        """Should save items in a file."""

        storage._deals = [test_deal]
        storage._historyOrders = [test_order]
        storage._lastDealTimeByInstanceIndex = {'0': 1000000000000}
        storage._lastHistoryOrderTimeByInstanceIndex = {'0': 1000000000010}
        file_manager.set_start_new_deal_index(0)
        file_manager.set_start_new_order_index(0)
        await file_manager.update_disk_storage()
        saved_data = await read_history_storage_file()
        assert saved_data['deals'] == [test_deal]
        assert saved_data['historyOrders'] == [test_order]
        assert saved_data['lastDealTimeByInstanceIndex'] == {'0': 1000000000000}
        assert saved_data['lastHistoryOrderTimeByInstanceIndex'] == {'0': 1000000000010}

    @pytest.mark.asyncio
    async def test_replace_nth_item(self):
        """Should replace Nth item in a file."""

        storage._deals = [test_deal, test_deal2]
        storage._historyOrders = [test_order, test_order2]
        file_manager.set_start_new_deal_index(0)
        file_manager.set_start_new_order_index(0)
        await file_manager.update_disk_storage()
        test_deal2['magic'] = 100
        test_order2['magic'] = 100
        file_manager.set_start_new_deal_index(1)
        file_manager.set_start_new_order_index(1)
        await file_manager.update_disk_storage()
        saved_data = await read_history_storage_file()
        assert saved_data['deals'] == [test_deal, test_deal2]
        assert saved_data['historyOrders'] == [test_order, test_order2]

    @pytest.mark.asyncio
    async def test_replace_all_items(self):
        """Should replace all items in a file."""

        storage._deals = [test_deal, test_deal2]
        storage._historyOrders = [test_order, test_order2]
        file_manager.set_start_new_deal_index(0)
        file_manager.set_start_new_order_index(0)
        await file_manager.update_disk_storage()
        test_deal['magic'] = 100
        test_deal2['magic'] = 100
        test_order['magic'] = 100
        test_order2['magic'] = 100
        file_manager.set_start_new_deal_index(0)
        file_manager.set_start_new_order_index(0)
        await file_manager.update_disk_storage()
        saved_data = await read_history_storage_file()
        assert saved_data['deals'] == [test_deal, test_deal2]
        assert saved_data['historyOrders'] == [test_order, test_order2]

    @pytest.mark.asyncio
    async def test_append_new_object(self):
        """Should append a new object to already saved ones."""

        storage._deals = [test_deal, test_deal2]
        storage._historyOrders = [test_order, test_order2]
        file_manager.set_start_new_deal_index(0)
        file_manager.set_start_new_order_index(0)
        await file_manager.update_disk_storage()
        storage._deals = [test_deal, test_deal2, test_deal3]
        storage._historyOrders = [test_order, test_order2, test_order3]
        file_manager.set_start_new_deal_index(2)
        file_manager.set_start_new_order_index(2)
        await file_manager.update_disk_storage()
        saved_data = await read_history_storage_file()
        assert saved_data['deals'] == [test_deal, test_deal2, test_deal3]
        assert saved_data['historyOrders'] == [test_order, test_order2, test_order3]

    @pytest.mark.asyncio
    async def test_not_corrupt(self):
        """Should not corrupt the disk storage if update called multiple times."""
        storage._deals = [test_deal, test_deal2]
        storage._historyOrders = [test_order, test_order2]
        storage._lastDealTimeByInstanceIndex = {'0': 1000000000000}
        storage._lastHistoryOrderTimeByInstanceIndex = {'0': 1000000000010}
        file_manager.set_start_new_deal_index(0)
        file_manager.set_start_new_order_index(0)
        await file_manager.update_disk_storage()
        storage._deals = [test_deal, test_deal2, test_deal3]
        storage._historyOrders = [test_order, test_order2, test_order3]
        storage._lastDealTimeByInstanceIndex = {'0': 1000000000000}
        storage._lastHistoryOrderTimeByInstanceIndex = {'0': 1000000000010}
        file_manager.set_start_new_deal_index(2)
        file_manager.set_start_new_order_index(2)
        await gather(*[
            file_manager.update_disk_storage(),
            file_manager.update_disk_storage(),
            file_manager.update_disk_storage(),
            file_manager.update_disk_storage(),
            file_manager.update_disk_storage()
        ])
        json.loads(open('.metaapi/accountId-application-historyOrders.bin').read())
        json.loads(open('.metaapi/accountId-application-deals.bin').read())
        json.loads(open('.metaapi/accountId-application-config.bin').read())

    @pytest.mark.asyncio
    async def test_remove_history(self):
        """Should remove history from disk."""

        open('.metaapi/accountId-application-deals.bin', "w+").close()
        open('.metaapi/accountId-application-historyOrders.bin', "w+").close()
        open('.metaapi/accountId-application-config.bin', "w+").close()
        assert os.path.isfile('.metaapi/accountId-application-deals.bin')
        assert os.path.isfile('.metaapi/accountId-application-historyOrders.bin')
        assert os.path.isfile('.metaapi/accountId-application-config.bin')
        await file_manager.delete_storage_from_disk()
        assert not os.path.isfile('.metaapi/accountId-application-deals.bin')
        assert not os.path.isfile('.metaapi/accountId-application-historyOrders.bin')
        assert not os.path.isfile('.metaapi/accountId-application-config.bin')

    @pytest.mark.asyncio
    async def test_remove_history_if_not_exists(self):
        """Should do nothing on remove history if files don't exist."""

        assert not os.path.isfile('.metaapi/accountId-application-deals.bin')
        assert not os.path.isfile('.metaapi/accountId-application-historyOrders.bin')
        assert not os.path.isfile('.metaapi/accountId-application-config.bin')
        await file_manager.delete_storage_from_disk()
