from multiprocessing import  Queue
from jobcoin.jobcoinmixinfo import JobCoinMixInfo
from jobcoin.jobcointransferinfo import JobCoinTransferInfo, TransferType
from jobcoin.withdrawworker import WithdrawWorker
from jobcoin.process import Process
from jobcoin.config import MESSAGE_HOUSE_ADDR_MISSING, MESSAGE_QUEUE_MISSING, MESSAGE_UNEXPECTED_ITEM_IN_QUEUE

"""
WithdrawManager listens to a queue for new withdrawal jobs in the background process
Once a withdrawal job is found, it spans a new process WithdrawWorker which will actually do the transfer
WithdrawManager will keep listening to the queue and spanning new WithdrawWorker as necessary
In the future this could be simply run from a terminal as a stand alone process and scale independently.
"""
class WithdrawManager():

    """
    Initiate WithdrawManager object with the house address and queue we want to use
    """
    def __init__(self, house_address, withdraw_queue):
        if not house_address:
            raise ValueError(MESSAGE_HOUSE_ADDR_MISSING)

        if not withdraw_queue:
            raise ValueError(MESSAGE_QUEUE_MISSING)

        self.house_address = house_address
        self.withdraw_queue = withdraw_queue
        
        self.listener_process = Process(target=self.start_listening_queue)
        self.listener_process.start()        


    """
    In a loop listen to the queue, 
    Queue.get() is a blocking operation that will return when an item is available
    Once an item is received and new WithdrawWorker process is spanned
    We go back to waiting for another item in the queue
    """
    def start_listening_queue(self):
        
        while True:
            transfer_info = self.withdraw_queue.get()

            if not isinstance(transfer_info, JobCoinTransferInfo):        
                raise ValueError(MESSAGE_UNEXPECTED_ITEM_IN_QUEUE)
            
            withdraw_worker = WithdrawWorker(self.house_address, transfer_info)

    """
    Stop the subprocess that is in constant loop above
    """
    def stop_listeners(self):
        self.listener_process.terminate()