import uuid
import pytest,contextlib
from multiprocessing import Queue
from jobcoin import config
from jobcoin.withdrawmanager import WithdrawManager
from jobcoin.jobcoinmixinfo import JobCoinMixInfo
from jobcoin.jobcointransferinfo import JobCoinTransferInfo, TransferType
from jobcoin.config import MESSAGE_HOUSE_ADDR_MISSING, MESSAGE_QUEUE_MISSING, MESSAGE_UNEXPECTED_ITEM_IN_QUEUE
import time

"""
Test that the expected error occurs when house address is missing
"""
def test_withdrawmanager_constructor_house_addr_error():
    with pytest.raises(ValueError) as e:
        mgr = WithdrawManager(None, None)
    
    assert str(e.value) == MESSAGE_HOUSE_ADDR_MISSING

"""
Test that the expected error occurs when queue is missing
"""
def test_withdrawmanager_constructor_queue_error():
    with pytest.raises(ValueError) as e:
        house_addr = uuid.uuid4().hex
        mgr = WithdrawManager(house_addr, None)
    
    assert str(e.value) == MESSAGE_QUEUE_MISSING

"""
Test that a withdrawmanager is created correctly from parameters
"""
def test_withdrawmanager_constructor_success():
    house_addr = uuid.uuid4().hex

    with_queue = Queue()

    mgr = WithdrawManager(house_addr, with_queue)
    mgr.stop_listeners()
    assert mgr.house_address == house_addr
    assert mgr.withdraw_queue == with_queue

"""
Test that a withdrawmanager errors out for wrong objects in queue
"""
def test_withdrawmanager_constructor_item_error():
    house_addr = uuid.uuid4().hex

    with_queue = Queue()

    with pytest.raises(ValueError) as e:
    
        mgr = WithdrawManager(house_addr, with_queue)
        with_queue.put("wrong data")
        mgr.listener_process.join()
        if mgr.listener_process.exception:
            (excep, trace) = mgr.listener_process.exception
            raise excep        

        mgr.stop_listeners()
    assert str(e.value) == MESSAGE_UNEXPECTED_ITEM_IN_QUEUE


"""
Test that a withdrawmanager is picking up items from the queue
"""
def test_withdrawmanager_queue_consumed():
    house_addr = uuid.uuid4().hex

    with_queue = Queue()

    jobmixinfo = JobCoinMixInfo("deposit", ["destination_1"])

    transfer_info = JobCoinTransferInfo(jobmixinfo, 1.37, TransferType.USER)
    jobmixinfo.amount = 12.37
    mgr = WithdrawManager(house_addr, with_queue)

    with_queue.put(transfer_info)
    time.sleep(1.0)
    #mgr.listener_process.join()
    mgr.stop_listeners()

    assert with_queue.empty()