import uuid
import pytest,contextlib
from multiprocessing import Queue
from jobcoin import config
from jobcoin.withdrawworker import WithdrawWorker
from jobcoin.jobcoinmixinfo import JobCoinMixInfo
from jobcoin.jobcointransferinfo import JobCoinTransferInfo, TransferType
from jobcoin.jobcoinapiproxy import JobCoinApiProxyImpl, JobCoinApiProxyMock
from jobcoin.config import MESSAGE_INSUFFICIENT_FUNDS,MESSAGE_TRANSFERINFO_MISSING, MESSAGE_TIMEOUT, API_BASE_URL, MESSAGE_HOUSE_ADDR_MISSING, MESSAGE_MIXINFO_MISSING
import time

"""
Test that the expected error occurs when house address is missing
"""
def test_withdrawworker_constructor_house_addr_error():
    with pytest.raises(ValueError) as e:
        mgr = WithdrawWorker(None, None)
    
    assert str(e.value) == MESSAGE_HOUSE_ADDR_MISSING

"""
Test that the expected error occurs when queue is missing
"""
def test_withdrawworker_constructor_info_error():
    with pytest.raises(ValueError) as e:
        house_addr = uuid.uuid4().hex
        mgr = WithdrawWorker(house_addr, None)
    
    assert str(e.value) == MESSAGE_TRANSFERINFO_MISSING

"""
Test that a withdrawworker is created correctly from parameters
"""
def test_withdrawworker_constructor_success():
    house_addr = uuid.uuid4().hex

    info = JobCoinMixInfo("deposit", ["destination_1"])
    transfer_info = JobCoinTransferInfo(info, 1.23, TransferType.USER)

    wrk = WithdrawWorker(house_addr, transfer_info)
    wrk.stop_listeners()
    assert wrk.house_address == house_addr
    assert wrk.jobcoinmixinfo == info


"""
Test that a withdrawworker is created correctly from parameters
"""
def test_withdrawworker_constructor_success():
    house_addr = uuid.uuid4().hex

    info = JobCoinMixInfo("deposit", ["destination_1"])
    transfer_info = JobCoinTransferInfo(info, 1.23, TransferType.USER)

    proxy = JobCoinApiProxyMock(API_BASE_URL)
    wrk = WithdrawWorker(house_addr, transfer_info, proxy)
    wrk.stop_listeners()
    assert wrk.house_address == house_addr
    assert wrk.jobcoinmixinfo == info

"""
Test that a withdrawworker is created correctly from parameters
"""
def test_withdrawworker_constructor_success():
    house_addr = uuid.uuid4().hex

    info = JobCoinMixInfo("deposit", ["destination_1"])
    transfer_info = JobCoinTransferInfo(info, 1.23, TransferType.USER)

    proxy = JobCoinApiProxyMock(API_BASE_URL)
    wrk = WithdrawWorker(house_addr, transfer_info, proxy)
    wrk.stop_listeners()
    assert wrk.house_address == house_addr
    assert wrk.jobcointransferinfo == transfer_info

"""
Test that a withdrawworker times out after specified limits
"""
def test_withdrawworker_balance_error():
    house_addr = uuid.uuid4().hex

    info = JobCoinMixInfo("deposit", ["destination_1"])
    transfer_info = JobCoinTransferInfo(info, 100.23, TransferType.USER)
    
    proxy = JobCoinApiProxyMock(API_BASE_URL, False, False)
    
    with pytest.raises(ValueError) as e:
        wrk = WithdrawWorker(house_addr, transfer_info, proxy)
        wrk.subprocess.join()
        if wrk.subprocess.exception:
            (excep, trace) = wrk.subprocess.exception
            raise excep

    assert str(e.value) == MESSAGE_INSUFFICIENT_FUNDS


"""
Test that a withdrawworker processes the withdrawal request
"""
def test_withdrawworker_withdraw_done():
    house_addr = uuid.uuid4().hex

    info = JobCoinMixInfo("deposit", ["destination_1"])
    transfer_info = JobCoinTransferInfo(info, 1.23, TransferType.USER)

    proxy = JobCoinApiProxyMock(API_BASE_URL, True, True)

    wrk = WithdrawWorker(house_addr, transfer_info, proxy)

    wrk.subprocess.join()
    if wrk.subprocess.exception:
        (excep, trace) = wrk.subprocess.exception
        raise excep

    assert wrk.subprocess.exitcode == 0
