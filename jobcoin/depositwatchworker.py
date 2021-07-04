from multiprocessing import  Queue
from jobcoin.jobcoinmixinfo import JobCoinMixInfo
from jobcoin.process import Process
from jobcoin.jobcoinapiproxy import JobCoinApiProxyImpl, JobCoinApiProxyProduction

from jobcoin.config import MESSAGE_TIMEOUT, MESSAGE_QUEUE_MISSING, API_POLL_TIME_SEC, MAX_WAIT_TIME_FOR_DEPOSITS_SEC, API_BASE_URL,  MESSAGE_MIXINFO_MISSING, MESSAGE_HOUSE_ADDR_MISSING
from jobcoin.jobcointransferinfo import JobCoinTransferInfo, TransferType
import logging
import time


"""
DepositWatchWorker checks with coin api for the arrival of deposit funds to deposit address
Once arrived, it puts a withdrawal job into withdraw queue
"""
class DepositWatchWorker():

    """
    Initiate object with the house address and withdraw_queue we want to use
    """
    def __init__(self, house_address, jobcoinmixinfo, withdraw_queue, proxy:JobCoinApiProxyImpl=None):
        if not house_address:
            raise ValueError(MESSAGE_HOUSE_ADDR_MISSING)

        if not jobcoinmixinfo:
            raise ValueError(MESSAGE_MIXINFO_MISSING)

        if not withdraw_queue:
            raise ValueError(MESSAGE_QUEUE_MISSING)

        self.house_address = house_address
        self.jobcoinmixinfo = jobcoinmixinfo
        self.withdraw_queue = withdraw_queue
        
        if proxy:
            self.proxy = proxy
        else:
            self.proxy = JobCoinApiProxyProduction(API_BASE_URL)

        self.listener_process = Process(target=self.watch_for_deposit)
        self.listener_process.start()


    """
    Watch for deposit at the deposit address
    Once found, create 2 transfer jobs
    a) to move deposit funds to house address
    b) to send from house address to destination addresses
    Then put both of them in the queue for the withdrawals
    Wait API_POLL_TIME_SEC seconds between each try.
    """
    def watch_for_deposit(self):        
        tries = 0
        while (tries*API_POLL_TIME_SEC <= MAX_WAIT_TIME_FOR_DEPOSITS_SEC):
            transactions = self.proxy.getAddressTransactions(self.jobcoinmixinfo.deposit_address)
            current_tx = list(filter(lambda x: x["toAddress"] == self.jobcoinmixinfo.deposit_address, transactions))
            
            if len(current_tx) > 0:
                amount = float(current_tx[0]["amount"])

                # 1 - Create Transfer for all amount from deposit address to house address
                house_mix_info = JobCoinMixInfo(self.jobcoinmixinfo.deposit_address, [self.house_address])
                house_transfer_info = JobCoinTransferInfo(house_mix_info, amount, TransferType.INTERNAL)

                # 2 - Create Transfer for the withdrawal to user addresses
                user_mix_info = JobCoinMixInfo(self.house_address, self.jobcoinmixinfo.destination_addresses)
                user_transfer_info = JobCoinTransferInfo(user_mix_info, amount, TransferType.USER)

                # 3 - Add both transfers to the queue
                self.withdraw_queue.put(house_transfer_info)
                self.withdraw_queue.put(user_transfer_info)
                
                exit(0)

            tries += 1
            time.sleep(API_POLL_TIME_SEC)
        
        raise ValueError(MESSAGE_TIMEOUT)

   
    """
    Stop the subprocess that is in constant loop above
    """
    def stop_listeners(self):
        self.listener_process.terminate()