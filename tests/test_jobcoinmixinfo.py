import uuid
import pytest
from jobcoin import config
from jobcoin.jobcoinmixinfo import JobCoinMixInfo
from jobcoin.config import MESSAGE_DEPOSIT_ADDR_MISSING, MESSAGE_DESTINATION_ADDR_MISSING


"""
Test that the expected error occurs when deposit address is missing
"""
def test_jobcoinmix_constructor_deposit_addr_error():
    with pytest.raises(ValueError) as e:
        mixinfo = JobCoinMixInfo(None, None)
    
    assert str(e.value) == MESSAGE_DEPOSIT_ADDR_MISSING

"""
Test that the expected error occurs when destination address is missing
"""
def test_jobcoinmix_constructor_destination_addr_error():
    with pytest.raises(ValueError) as e:
        deposit_addr = uuid.uuid4().hex
        mixinfo = JobCoinMixInfo(deposit_addr, None)
    
    assert str(e.value) == MESSAGE_DESTINATION_ADDR_MISSING

"""
Test that a jobcoin info is created correctly from parameters
"""
def test_jobcoinmix_constructor_success():
    deposit_addr = uuid.uuid4().hex

    address_count = 3
    destination_addr = [uuid.uuid4().hex for _ in range(address_count)]

    mixinfo = JobCoinMixInfo(deposit_addr, destination_addr)

    assert mixinfo.deposit_address == deposit_addr
    assert mixinfo.destination_addresses == destination_addr