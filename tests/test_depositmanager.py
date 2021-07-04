import uuid
import pytest,contextlib
from multiprocessing import Queue
from jobcoin import config
from jobcoin.depositmanager import DepositManager
from jobcoin.jobcoinmixinfo import JobCoinMixInfo
from jobcoin.config import MESSAGE_HOUSE_ADDR_MISSING, MESSAGE_QUEUE_MISSING, MESSAGE_UNEXPECTED_ITEM_IN_QUEUE
import time

"""
Test that the expected error occurs when house address is missing
"""
def test_depositmanager_constructor_house_addr_error():
    with pytest.raises(ValueError) as e:
        mgr = DepositManager(None, None, None)
    
    assert str(e.value) == MESSAGE_HOUSE_ADDR_MISSING

"""
Test that the expected error occurs when queue is missing
"""
def test_depositmanager_constructor_queue_error():
    with pytest.raises(ValueError) as e:
        house_addr = uuid.uuid4().hex
        mgr = DepositManager(house_addr, None, None)
    
    assert str(e.value) == MESSAGE_QUEUE_MISSING

"""
Test that a depositmanager is created correctly from parameters
"""
def test_depositmanager_constructor_success():
    house_addr = uuid.uuid4().hex

    dep_queue = Queue()
    with_queue = Queue()

    mgr = DepositManager(house_addr, dep_queue, with_queue)
    mgr.stop_listeners()
    assert mgr.house_address == house_addr
    assert mgr.deposit_queue == dep_queue

"""
Test that a depositmanager errors out for wrong objects in queue
"""
def test_depositmanager_constructor_item_error():
    house_addr = uuid.uuid4().hex

    dep_queue = Queue()
    with_queue = Queue()

    with pytest.raises(ValueError) as e:
    
        mgr = DepositManager(house_addr, dep_queue, with_queue)
        dep_queue.put("wrong data")
        mgr.listener_process.join()
        if mgr.listener_process.exception:
            (excep, trace) = mgr.listener_process.exception
            raise excep        

        mgr.stop_listeners()
    assert str(e.value) == MESSAGE_UNEXPECTED_ITEM_IN_QUEUE


"""
Test that a depositmanager is picking up items from the queue
"""
def test_depositmanager_queue_consumed():
    house_addr = uuid.uuid4().hex

    dep_queue = Queue()
    with_queue = Queue()

    jobmixinfo = JobCoinMixInfo("deposit", ["destination_1"])

    mgr = DepositManager(house_addr, dep_queue, with_queue)

    dep_queue.put(jobmixinfo)
    time.sleep(1.0)
    mgr.stop_listeners()

    assert dep_queue.empty()