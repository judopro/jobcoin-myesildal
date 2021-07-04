
from .config import MESSAGE_DEPOSIT_ADDR_MISSING, MESSAGE_DESTINATION_ADDR_MISSING

"""
Represents the data structure for a JobCoin mix transaction

Deposit Address: where we expect user to send the amount
Destination Address: (list) where we will distribute the amount deposited to above addresses in this list
"""
class JobCoinMixInfo():

    def __init__(self, deposit_address:str, destination_addresses:[str]):
        if not deposit_address:
            raise ValueError(MESSAGE_DEPOSIT_ADDR_MISSING)

        if not destination_addresses or len(destination_addresses) == 0:
            raise ValueError(MESSAGE_DESTINATION_ADDR_MISSING)

        self.deposit_address = deposit_address
        self.destination_addresses = destination_addresses

    def __repr__(self):
        return """{} -> {}
        """.format(self.deposit_address, self.destination_addresses)