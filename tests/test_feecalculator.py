from jobcoin.jobcointransferinfo import JobCoinTransferInfo, TransferType
from jobcoin.jobcoinmixinfo import JobCoinMixInfo
from jobcoin.config import FEE_ADDRESS, TX_FEE_PERCENTAGE
from jobcoin.feecalculator import FeeCalculator
import uuid 

"""
Test that there are no fees that applies to INTERNAL transfers
so we can move money freely between house and deposit accounts
"""
def test_no_fee_for_internal_transfer():
    deposit_addr = uuid.uuid4().hex
    address_count = 1
    destination_addr = [uuid.uuid4().hex for _ in range(address_count)]
    mixinfo = JobCoinMixInfo(deposit_addr, destination_addr)

    txinfo = JobCoinTransferInfo(mixinfo, 6.25, TransferType.INTERNAL)

    fee = FeeCalculator().getTransferFeeInfo(txinfo)

    assert fee is None


"""
Test that the fees are calculated properly for all USER transfers
"""
def test_fee_calculated_for_user_transfer():
    deposit_addr = uuid.uuid4().hex
    address_count = 1
    destination_addr = [uuid.uuid4().hex for _ in range(address_count)]
    mixinfo = JobCoinMixInfo(deposit_addr, destination_addr)
    amount = 10.00
    txinfo = JobCoinTransferInfo(mixinfo, amount, TransferType.USER)

    fee = FeeCalculator().getTransferFeeInfo(txinfo)

    assert fee.amount == (amount * TX_FEE_PERCENTAGE)