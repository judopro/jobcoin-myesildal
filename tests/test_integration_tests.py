import uuid
import pytest,contextlib
from multiprocessing import Queue
import re
from click.testing import CliRunner
import cli
import uuid

from jobcoin import config
from jobcoin.jobcoin import JobCoin
from jobcoin.depositmanager import DepositManager
from jobcoin.withdrawmanager import WithdrawManager

from jobcoin.withdrawworker import WithdrawWorker
from jobcoin.jobcoinmixinfo import JobCoinMixInfo
from jobcoin.jobcoinapiproxy import JobCoinApiProxyImpl, JobCoinApiProxyProduction
from jobcoin.config import FEE_ADDRESS,TX_FEE_PERCENTAGE, TEST_HOUSE_ADDRESS, API_BASE_URL, TEST_HOUSE_ADDRESS, MESSAGE_INSUFFICIENT_FUNDS, MESSAGE_TIMEOUT, API_BASE_URL, MESSAGE_HOUSE_ADDR_MISSING, MESSAGE_MIXINFO_MISSING
import time
import logging

"""
This is a full end-to-end integration test that verifies the funds are actually transferred
1) Start Deposit and Withdraw Manager who will be monitoring queues
2) Submit a mixing info to JobCoin instance
3) Send an amount to deposit address specified in jobcoin mixinfo programatically to trigger the events
4) Sleep 5 seconds so the send transaction above is detected by Deposit Manager
5) Verify that the deposit manager finds the transaction
5) Sleep another 5 seconds so the deposit manager has put actual transfer job to withdrawal queue
6) Using API check that the amounts are transferred into the destination addresses
7) Using API verify that the fees were calculated and transferred correctly
"""
def test_mixing_to_single_address():
    deposit_queue = Queue()
    withdraw_queue = Queue()

    deposit_manager = DepositManager(TEST_HOUSE_ADDRESS, deposit_queue, withdraw_queue)
    withdraw_manager = WithdrawManager(TEST_HOUSE_ADDRESS, withdraw_queue)

    jobcoin = JobCoin(TEST_HOUSE_ADDRESS, deposit_queue)

    deposit_address = uuid.uuid4().hex

    amount = 1.99
    fromAddress = "my_source_address0"
    destination_addresses = [uuid.uuid4().hex]
    jobcoinmixinfo = JobCoinMixInfo(deposit_address, destination_addresses)
    jobcoin.start_mixing(jobcoinmixinfo)
    
    proxy = JobCoinApiProxyProduction(API_BASE_URL)

    proxy.send_amount(fromAddress, deposit_address, amount)

    #logging.getLogger().log(logging.DEBUG,"Sleeping for 5 seconds...Waiting for transaction to be read")
    print("Sleeping for 5 seconds...Waiting for transaction to be read")
    time.sleep(5)
    
    transactions = proxy.get_transactions_for_address(deposit_address)
    current_tx = list(filter(lambda x: x["toAddress"] == deposit_address, transactions))
    assert len(current_tx) > 0

    #logging.getLogger().log(logging.DEBUG,"Sleeping for 5 seconds...Waiting for transaction to be read")
    print("Sleeping for 5 seconds...Waiting for final transaction")
    time.sleep(5)

    transactions = proxy.get_transactions_for_address(destination_addresses[0])
    current_tx = list(filter(lambda x: x["toAddress"] == destination_addresses[0], transactions))
    assert len(current_tx) > 0

    ttl_transferred = float(current_tx[0]["amount"])

    fee_amount = amount * TX_FEE_PERCENTAGE
    transactions = proxy.get_transactions_for_address(FEE_ADDRESS)
    fee_tx = list(filter(lambda x: x["toAddress"] == FEE_ADDRESS and float(x["amount"]) == fee_amount, transactions))
    assert len(fee_tx) > 0

    assert amount == (ttl_transferred+fee_amount)

    deposit_manager.stop_listeners()
    withdraw_manager.stop_listeners()
    
    #logging.getLogger().log(logging.DEBUG, "Finished.")
    print("Finished.")


"""
This is a full end-to-end integration test that verifies the funds are actually transferred
Using 2 destination addresses
1) Start Deposit and Withdraw Manager who will be monitoring queues
2) Submit a mixing info to JobCoin instance
3) Send an amount to deposit address specified in jobcoin mixinfo programatically to trigger the events
4) Sleep 5 seconds so the send transaction above is detected by Deposit Manager
5) Verify that the deposit manager finds the transaction
5) Sleep another 5 seconds so the deposit manager has put actual transfer job to withdrawal queue
6) Using API check that the amounts are transferred into the destination addresses
7) Using API verify that the fees were calculated and transferred correctly
"""
def test_mixing_to_two_addresses():
    
    deposit_queue = Queue()
    withdraw_queue = Queue()

    deposit_manager = DepositManager(TEST_HOUSE_ADDRESS, deposit_queue, withdraw_queue)
    withdraw_manager = WithdrawManager(TEST_HOUSE_ADDRESS, withdraw_queue)

    jobcoin = JobCoin(TEST_HOUSE_ADDRESS, deposit_queue)

    deposit_address = uuid.uuid4().hex

    amount = 3.99
    fromAddress = "my_source_address0"
    destination_addresses = [uuid.uuid4().hex, uuid.uuid4().hex]
    jobcoinmixinfo = JobCoinMixInfo(deposit_address, destination_addresses)
    jobcoin.start_mixing(jobcoinmixinfo)
    
    proxy = JobCoinApiProxyProduction(API_BASE_URL)

    proxy.send_amount(fromAddress, deposit_address, amount)

    #logging.getLogger().log(logging.DEBUG,"Sleeping for 5 seconds...Waiting for transaction to be read")
    print("Sleeping for 5 seconds...Waiting for transaction to be read")
    time.sleep(5)
    
    transactions = proxy.get_transactions_for_address(deposit_address)
    current_tx = list(filter(lambda x: x["toAddress"] == deposit_address, transactions))
    assert len(current_tx) > 0

    #logging.getLogger().log(logging.DEBUG,"Sleeping for 5 seconds...Waiting for transaction to be read")
    print("Sleeping for 5 seconds...Waiting for final transaction")
    time.sleep(5)

    ttl_transferred = 0.0
    for i in range(2):
        transactions = proxy.get_transactions_for_address(destination_addresses[i])
        current_tx = list(filter(lambda x: x["toAddress"] == destination_addresses[i], transactions))
        ttl_transferred += float(current_tx[0]["amount"])
        assert len(current_tx) > 0


    fee_amount = amount * TX_FEE_PERCENTAGE
    transactions = proxy.get_transactions_for_address(FEE_ADDRESS)
    fee_tx = list(filter(lambda x: x["toAddress"] == FEE_ADDRESS and float(x["amount"]) == fee_amount, transactions))
    assert len(fee_tx) > 0

    assert amount == (ttl_transferred+fee_amount)

    deposit_manager.stop_listeners()
    withdraw_manager.stop_listeners()
    
    #logging.getLogger().log(logging.DEBUG, "Finished.")
    print("Finished.")