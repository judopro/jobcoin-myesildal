from multiprocessing import  Queue
from jobcoin.jobcoinmixinfo import JobCoinMixInfo
from jobcoin.process import Process
from jobcoin.jobcoinapiproxy import JobCoinApiProxyImpl, JobCoinApiProxyProduction
from jobcoin.jobcointransferinfo import JobCoinTransferInfo, TransferType
from jobcoin.feecalculator import FeeCalculator
from jobcoin.config import MESSAGE_TRANSFERINFO_MISSING, MESSAGE_INSUFFICIENT_FUNDS, TX_DELAY_MIN_SEC, TX_DELAY_MAX_SEC, MESSAGE_TIMEOUT, MESSAGE_QUEUE_MISSING, API_POLL_TIME_SEC, MAX_WAIT_TIME_FOR_DEPOSITS_SEC, API_BASE_URL,  MESSAGE_MIXINFO_MISSING, MESSAGE_HOUSE_ADDR_MISSING
import logging
import time
import random


"""
WithdrawWorker does the actual transfer by using the API
"""
class WithdrawWorker():

    """
    Initiate JobCoinManager object with the house address and transfer info we want to use
    """
    def __init__(self, house_address, jobcointransferinfo, proxy:JobCoinApiProxyImpl=None):
        if not house_address:
            raise ValueError(MESSAGE_HOUSE_ADDR_MISSING)

        if not jobcointransferinfo:
            raise ValueError(MESSAGE_TRANSFERINFO_MISSING)

        self.house_address = house_address
        self.jobcointransferinfo = jobcointransferinfo
        
        if proxy:
            self.proxy = proxy
        else:
            self.proxy = JobCoinApiProxyProduction(API_BASE_URL)

        self.fee_calculator = FeeCalculator()
        self.subprocess = Process(target=self.initiate_withdrawal)
        self.subprocess.start()


    """
    1 - First get whether any fees applies to this transfer
    2 - Calculate the remaning amount to be transferred to destinaton addresses after fees
    3 - Initiate the withdrawal after a random delay
    4 - In a loop transfer a random amount (less than remaning) to each destination address
    5 - Update remaning amount that need to be still transferred
    6 - At the end, send the any remaning amount to the last destination address
    7 - As a last step, if there were any fees applies, charge them as well.
    """
    def initiate_withdrawal(self):        
        
        from_address = self.jobcointransferinfo.jobcoinmixinfo.deposit_address
        dest_addresses = self.jobcointransferinfo.jobcoinmixinfo.destination_addresses

        fee_info = self.fee_calculator.getTransferFeeInfo(self.jobcointransferinfo)
        fee_amount = fee_info.amount if fee_info else 0.0

        #Total amount to be transferred after fees deducted
        rem_amount = self.jobcointransferinfo.amount - fee_amount

        delay = random.uniform(TX_DELAY_MIN_SEC, TX_DELAY_MAX_SEC)
        time.sleep(delay)

        cnt = len(dest_addresses)
        for i in range(cnt-1):
            #Get a random amount 
            amount = random.uniform(0, rem_amount)
            #update remaining amount
            rem_amount -= amount
            #transfer the amount
            try:
                self.proxy.send_amount(from_address, dest_addresses[i], amount)
            except ValueError:
                raise ValueError(MESSAGE_INSUFFICIENT_FUNDS)

        #Finally transfer the remaining amount to last destination address
        if rem_amount > 0:
            self.proxy.send_amount(from_address, dest_addresses[-1], rem_amount)

        # Charge fees if there is one to apply
        if fee_info is not None and fee_amount > 0:
            self.proxy.send_amount(fee_info.jobcoinmixinfo.deposit_address, fee_info.jobcoinmixinfo.destination_addresses[0], fee_amount)

        exit(0)
        

    """
    Stop the subprocess that is in constant loop above
    """
    def stop_listeners(self):
        self.subprocess.terminate()