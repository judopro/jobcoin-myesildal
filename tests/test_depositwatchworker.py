import uuid
import pytest,contextlib
from multiprocessing import Queue
from jobcoin import config
from jobcoin.depositwatchworker import DepositWatchWorker
from jobcoin.jobcointransferinfo import JobCoinTransferInfo, TransferType
from jobcoin.jobcoinmixinfo import JobCoinMixInfo
from jobcoin.jobcoinapiproxy import JobCoinApiProxyImpl, JobCoinApiProxyMock
from jobcoin.config import MESSAGE_TIMEOUT, API_BASE_URL, MESSAGE_HOUSE_ADDR_MISSING, MESSAGE_MIXINFO_MISSING
import time

"""
Test that the expected error occurs when house address is missing
"""
def test_depositwatchworker_constructor_house_addr_error():
    with pytest.raises(ValueError) as e:
        mgr = DepositWatchWorker(None, None, None)
    
    assert str(e.value) == MESSAGE_HOUSE_ADDR_MISSING

"""
Test that the expected error occurs when queue is missing
"""
def test_depositwatchworker_constructor_info_error():
    with pytest.raises(ValueError) as e:
        house_addr = uuid.uuid4().hex
        mgr = DepositWatchWorker(house_addr, None, None)
    
    assert str(e.value) == MESSAGE_MIXINFO_MISSING

"""
Test that a depositwatchworker is created correctly from parameters
"""
def test_depositwatchworker_constructor_success():
    house_addr = uuid.uuid4().hex

    info = JobCoinMixInfo("deposit", ["destination_1"])

    wrk = DepositWatchWorker(house_addr, info, Queue())
    wrk.stop_listeners()
    assert wrk.house_address == house_addr
    assert wrk.jobcoinmixinfo == info


"""
Test that a depositwatchworker is created correctly from parameters
"""
def test_depositwatchworker_constructor_success():
    house_addr = uuid.uuid4().hex

    info = JobCoinMixInfo("deposit", ["destination_1"])

    proxy = JobCoinApiProxyMock(API_BASE_URL)
    wrk = DepositWatchWorker(house_addr, info, Queue(), proxy)
    wrk.stop_listeners()
    assert wrk.house_address == house_addr
    assert wrk.jobcoinmixinfo == info

"""
Test that a depositwatchworker is created correctly from parameters
"""
def test_depositwatchworker_constructor_success():
    house_addr = uuid.uuid4().hex

    info = JobCoinMixInfo("deposit", ["destination_1"])

    proxy = JobCoinApiProxyMock(API_BASE_URL)
    wrk = DepositWatchWorker(house_addr, info, Queue(), proxy)
    wrk.stop_listeners()
    assert wrk.house_address == house_addr
    assert wrk.jobcoinmixinfo == info

"""
Test that a depositwatchworker times out after specified limits
"""
def test_depositwatchworker_timeout_error():
    house_addr = uuid.uuid4().hex

    info = JobCoinMixInfo("deposit", ["destination_1"])

    proxy = JobCoinApiProxyMock(API_BASE_URL, False, False)
    
    with pytest.raises(ValueError) as e:
        wrk = DepositWatchWorker(house_addr, info, Queue(), proxy)
        wrk.listener_process.join()
        if wrk.listener_process.exception:
            (excep, trace) = wrk.listener_process.exception
            raise excep

    assert str(e.value) == MESSAGE_TIMEOUT


"""
Test that a depositwatchworker processes when a deposit is found
"""
def test_depositwatchworker_deposit_found():
    house_addr = uuid.uuid4().hex

    info = JobCoinMixInfo("deposit", ["destination_1"])

    proxy = JobCoinApiProxyMock(API_BASE_URL, True, True)
    queue = Queue()

    wrk = DepositWatchWorker(house_addr, info, queue, proxy)

    wrk.listener_process.join()
    if wrk.listener_process.exception:
        (excep, trace) = wrk.listener_process.exception
        raise excep

    t1 = queue.get()
    t2 = queue.get()

    assert t1.type == TransferType.INTERNAL and t1.jobcoinmixinfo.destination_addresses == [house_addr]
    assert t2.type == TransferType.USER and t2.jobcoinmixinfo.destination_addresses == info.destination_addresses

    assert wrk.listener_process.exitcode == 0