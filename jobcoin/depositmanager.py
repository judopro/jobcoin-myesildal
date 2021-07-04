from multiprocessing import  Queue
from jobcoin.jobcoinmixinfo import JobCoinMixInfo
from jobcoin.depositwatchworker import DepositWatchWorker
from jobcoin.process import Process
from jobcoin.config import MESSAGE_HOUSE_ADDR_MISSING, MESSAGE_QUEUE_MISSING, MESSAGE_UNEXPECTED_ITEM_IN_QUEUE

"""
DepositManager listens to a queue for new deposit watch jobs in the background process
Once a watch job is found, it spans a new process DepositWatchWorker which will actually monitor the transfer
DepositManager will keep listening to the queue and spanning new DepositWatchWorkers as necessary
In the future this could be simply run from a terminal as a stand alone process and scale independently.
"""
class DepositManager():

    """
    Initiate JobCoinManager object with the house address and queue we want to use
    """
    def __init__(self, house_address, deposit_queue, withdraw_queue):
        if not house_address:
            raise ValueError(MESSAGE_HOUSE_ADDR_MISSING)

        if not deposit_queue:
            raise ValueError(MESSAGE_QUEUE_MISSING)
        
        if not withdraw_queue:
            raise ValueError(MESSAGE_QUEUE_MISSING)

        self.house_address = house_address
        self.deposit_queue = deposit_queue
        self.withdraw_queue = withdraw_queue
        
        self.listener_process = Process(target=self.start_listening_queue)
        self.listener_process.start()        


    """
    In a loop listen to the queue, 
    Queue.get() is a blocking operation that will return when an item is available
    Once an item is received and new Watcher process is spanned
    We go back to waiting for another item in the queue
    """
    def start_listening_queue(self):
        while True:
            mixinfo = self.deposit_queue.get()

            if not isinstance(mixinfo, JobCoinMixInfo):        
                raise ValueError(MESSAGE_UNEXPECTED_ITEM_IN_QUEUE)

            deposit_watcher = DepositWatchWorker(self.house_address, mixinfo, self.withdraw_queue)

    """
    Stop the subprocess that is in constant loop above
    """
    def stop_listeners(self):
        self.listener_process.terminate()