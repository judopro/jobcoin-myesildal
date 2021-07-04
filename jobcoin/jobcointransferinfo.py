
from .config import MESSAGE_MIXINFO_MISSING, MESSAGE_AMOUNT_MISSING
from jobcoin.jobcoinmixinfo import JobCoinMixInfo

from enum import Enum

class TransferType(Enum):
    INTERNAL = 0
    USER = 1


"""
Represents the data structure for a JobCoin transfer

JobCoinMixInfo : Has the Deposit Address and Destination Address
Amount: amount to be transferred between accounts in mixinfo
Type: The type of transfer whether user initiated or internal
"""
class JobCoinTransferInfo():

    def __init__(self, jobcoinmixinfo:JobCoinMixInfo, amount:float, type:TransferType):
        if not jobcoinmixinfo:
            raise ValueError(MESSAGE_MIXINFO_MISSING)

        if amount == 0.0:
            raise ValueError(MESSAGE_AMOUNT_MISSING)

        self.jobcoinmixinfo = jobcoinmixinfo
        self.amount = amount
        self.type = type


    def __repr__(self):
        return """{} -> {} {} {}
        """.format(self.jobcoinmixinfo.deposit_address, self.jobcoinmixinfo.destination_addresses, self.amount, self.type)