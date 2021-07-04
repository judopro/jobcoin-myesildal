import requests
from abc import ABCMeta, abstractmethod
from jobcoin.config import MESSAGE_INSUFFICIENT_FUNDS
import logging

"""
Abstract implementation of our Coin API 
"""
class JobCoinApiProxyImpl():

    def __init__(self, hostname):
        self.hostname = hostname
        
    def get_transactions_for_address(self, address):
        raise NotImplementedError()

    def send_amount(self, fromAddress, toAddress, amount):
        raise NotImplementedError()


"""
An implementation of above ProxyImpl to Production house
"""
class JobCoinApiProxyProduction(JobCoinApiProxyImpl):
    def __init__(self, hostname):
        super().__init__(hostname)

    """
    Make a query to the api server 
    and return a list of transactions and balance info for the address
    """    
    def get_transactions_for_address(self, address):
        url = "{}/addresses/{}".format(self.hostname, address)
        r = requests.get(url)
        return r.json()["transactions"]


    def send_amount(self, fromAddress, toAddress, amount):
        
        url = "{}/transactions".format(self.hostname)

        params = dict()
        params["fromAddress"] = fromAddress
        params["toAddress"] = toAddress
        params["amount"] = amount

        res = requests.post(url, data=params)

        #Insufficient funds error should be handled
        if "error" in res.json():
            raise ValueError(MESSAGE_INSUFFICIENT_FUNDS)
        
        logging.getLogger().log(logging.ERROR, "amount {:2f} sent to {} successfully".format(amount, toAddress))
        return True


"""
An implementation of above ProxyImpl as a Mock OBject for using with unit tests
"""
class JobCoinApiProxyMock(JobCoinApiProxyImpl):
    """
    returnTransaction is a boolean flag to control
    in get_transactions_for_address whether to return transactions for that address or not.
    For some test cases, we set it to NO to check graceful failure.
    """
    def __init__(self, hostname, successGetTransaction=True, successsend_amount=True):
        super().__init__(hostname)
        self.successGetTransaction = successGetTransaction
        self.successsend_amount = successsend_amount

    """
    Return a predetermined set of transactions for unit test cases
    """
    def get_transactions_for_address(self, address):

        if not self.successGetTransaction:
            return []

        tx = [{
                "timestamp": "2021-04-22T13:10:01.210Z",
                "toAddress": address,
                "amount": "50.35"
            }
        ]
        return tx

    def send_amount(self, fromAddress, toAddress, amount):
        if not self.successsend_amount:
            raise ValueError(MESSAGE_INSUFFICIENT_FUNDS)

        return True