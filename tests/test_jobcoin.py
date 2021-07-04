#!/usr/bin/env python
import pytest
import re
from click.testing import CliRunner
import cli
import uuid
from multiprocessing import Queue

import sys
sys.path.append("..")

from jobcoin import config
from jobcoin.jobcoin import JobCoin
from jobcoin.config import TEST_HOUSE_ADDRESS, MESSAGE_HOUSE_ADDR_MISSING, MESSAGE_QUEUE_MISSING

@pytest.fixture
def response():
    import requests
    return requests.get('https://jobcoin.gemini.com/')


def test_content(response):
    assert b'Hello!' in response.content


def test_cli_basic():
    runner = CliRunner()
    result = runner.invoke(cli.main,  ['--house_address', TEST_HOUSE_ADDRESS])
    assert result.exit_code == 0
    assert 'Welcome to the Jobcoin mixer' in result.output


def test_cli_creates_address():
    runner = CliRunner()
    address_create_output = runner.invoke(cli.main, ['--house_address', TEST_HOUSE_ADDRESS], input='1234,4321').output
    output_re = re.compile(
        r'You may now send Jobcoins to address [0-9a-zA-Z]{32}. '
        'They will be mixed and sent to your destination addresses.'
    )

    #Capture deposit address so we can actually deposit to there to test
    assert output_re.search(address_create_output) is not None


"""
Test that the expected error occurs when house address is missing
"""
def test_jobcoin_constructor_house_addr_error():
    with pytest.raises(ValueError) as e:
        mgr = JobCoin(None, None)
    
    assert str(e.value) == MESSAGE_HOUSE_ADDR_MISSING


"""
Test that the expected error occurs when queue is missing
"""
def test_jobcoin_constructor_queue_error():
    with pytest.raises(ValueError) as e:
        house_addr = uuid.uuid4().hex
        mgr = JobCoin(house_addr, None)
    
    assert str(e.value) == MESSAGE_QUEUE_MISSING

"""
Test that a jobcoin is created correctly from parameters
"""
def test_jobcoin_constructor_success():
    house_addr = uuid.uuid4().hex

    queue = Queue()
    mgr = JobCoin(house_addr, queue)

    assert mgr.house_address == house_addr
    assert mgr.deposit_queue == queue
