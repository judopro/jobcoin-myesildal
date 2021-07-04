from jobcoin.jobcointransferinfo import JobCoinTransferInfo, TransferType
from jobcoin.jobcoinmixinfo import JobCoinMixInfo
from jobcoin.config import FEE_ADDRESS, TX_FEE_PERCENTAGE

"""
Central fee calculation part of our system. 
At beginning - we simply charge a flat fee percentage for all user transactions
and make sure to not apply any fees to internal transactions
"""
class FeeCalculator():
    
    def __init__(self):
        pass

    """
    Determine fee to charge based on transfer type
    In the future we can have different transaction fee percentages based on 
    30 day transaction volume of sender addresses etc...
    """
    def get_transfer_fee_info(self, transfer_info):
        if transfer_info.type == TransferType.INTERNAL:
            return None
        
        fee_amount = transfer_info.amount * TX_FEE_PERCENTAGE
        fee_mixinfo = JobCoinMixInfo(transfer_info.jobcoinmixinfo.deposit_address, [FEE_ADDRESS])
        fee_transferinfo = JobCoinTransferInfo(fee_mixinfo, fee_amount, TransferType.INTERNAL)

        return fee_transferinfo
        