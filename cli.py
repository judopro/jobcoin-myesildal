#!/usr/bin/env python
import uuid
import sys
import click

from multiprocessing import Queue

from jobcoin.jobcoin import JobCoin
from jobcoin.depositmanager import DepositManager
from jobcoin.withdrawmanager import WithdrawManager

from jobcoin.config import PROD_HOUSE_ADDRESS
from jobcoin.jobcoinmixinfo import JobCoinMixInfo


@click.command()
@click.option('--house_address', default=PROD_HOUSE_ADDRESS)
def main(house_address):
    print('Welcome to the Jobcoin mixer!\n')
    
    deposit_queue = Queue()
    withdraw_queue = Queue()

    deposit_manager = DepositManager(house_address, deposit_queue, withdraw_queue)
    withdraw_manager = WithdrawManager(house_address, withdraw_queue)
    jobcoin = JobCoin(house_address, deposit_queue)
    
    while True:
        addresses = click.prompt(
            'Please enter a comma-separated list of new, unused Jobcoin '
            'addresses where your mixed Jobcoins will be sent.',
            prompt_suffix='\n[blank to quit] > ',
            default='',
            show_default=False)
        if addresses.strip() == '':
            deposit_manager.stop_listeners()
            withdraw_manager.stop_listeners()
            sys.exit(0)
        
        destination_addresses = addresses.split(',')
        deposit_address = uuid.uuid4().hex
        click.echo(
            '\nYou may now send Jobcoins to address {deposit_address}. They '
            'will be mixed and sent to your destination addresses.\n'
              .format(deposit_address=deposit_address))
        
        jobcoinmixinfo = JobCoinMixInfo(deposit_address, destination_addresses)
        jobcoin.start_mixing(jobcoinmixinfo)


if __name__ == '__main__':
    sys.exit(main())
