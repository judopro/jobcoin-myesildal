import uuid
import pytest
from jobcoin import config
from jobcoin.jobcointransferinfo import JobCoinMixInfo
from jobcoin.jobcointransferinfo import JobCoinTransferInfo, TransferType
from jobcoin.config import MESSAGE_MIXINFO_MISSING, MESSAGE_AMOUNT_MISSING


"""
Test that the expected error occurs when mix info is missing
"""
def test_jobcointransfer_constructor_mixinfo_error():
    with pytest.raises(ValueError) as e:
        txinfo = JobCoinTransferInfo(None, 0.0, TransferType.USER)
    
    assert str(e.value) == MESSAGE_MIXINFO_MISSING

"""
Test that the expected error occurs when amount is missing
"""
def test_jobcointransfer_constructor_amount_error():
    with pytest.raises(ValueError) as e:
        deposit_addr = uuid.uuid4().hex
        address_count = 3
        destination_addr = [uuid.uuid4().hex for _ in range(address_count)]
        mixinfo = JobCoinMixInfo(deposit_addr, destination_addr)
    
        txinfo = JobCoinTransferInfo(mixinfo, 0.0, TransferType.USER)
    assert str(e.value) == MESSAGE_AMOUNT_MISSING

"""
Test that a jobcoin transfer info is created correctly from parameters
"""
def test_jobcointransfer_constructor_success():
    deposit_addr = uuid.uuid4().hex

    address_count = 3
    destination_addr = [uuid.uuid4().hex for _ in range(address_count)]

    mixinfo = JobCoinMixInfo(deposit_addr, destination_addr)

    amount = 7.99
    txinfo = JobCoinTransferInfo(mixinfo, amount, TransferType.USER)

    assert txinfo.jobcoinmixinfo.deposit_address == deposit_addr
    assert txinfo.jobcoinmixinfo.destination_addresses == destination_addr
    assert txinfo.amount == amount
    assert txinfo.type == TransferType.USER