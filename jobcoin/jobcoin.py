from . import config
from .jobcoinmixinfo import JobCoinMixInfo
from multiprocessing import Queue

from jobcoin.depositmanager import DepositManager
from jobcoin.withdrawmanager import WithdrawManager

from .config import MESSAGE_HOUSE_ADDR_MISSING, MESSAGE_QUEUE_MISSING


"""
JobCoin class helps initiate the mixing action.
Different clients such as terminal CLI and/or our web/mobile API 
can use this class to submit coinmix operations to our system via a unified method.
It uses a Queue to submit mixing jobs which will be picked up by another process (depositmanager.py)
This way we are decoupling submission of jobs and processing of them so we can increase/decrease capacity 
of submit workers or pickup workers independently from each other.
"""
class JobCoin():

    """
    Initiate JobCoin object with the house address we want to use
    """
    def __init__(self, house_address, queue):
        if not house_address:
            raise ValueError(MESSAGE_HOUSE_ADDR_MISSING)

        if not queue:
            raise ValueError(MESSAGE_QUEUE_MISSING)

        self.house_address = house_address
        self.deposit_queue = queue

    """
    Submit the job info to the queue
    """
    def start_mixing(self, jobcoinmixinfo):
        self.deposit_queue.put(jobcoinmixinfo)
    