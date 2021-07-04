import sys
"""
sys.exit('\n!!! Please update config.py with your personal Jobcoin URL and '
         'remove this message.\n')
"""
API_BASE_URL = 'https://jobcoin.gemini.com/shone-unviable/api'
API_ADDRESS_URL = '{}/addresses'.format(API_BASE_URL)
API_TRANSACTIONS_URL = '{}/transactions'.format(API_BASE_URL)

PROD_HOUSE_ADDRESS = "PROD_HOUSE_ADDRESS"
TEST_HOUSE_ADDRESS = "TEST_HOUSE_ADDRESS"

# Transaction Fee Percentage to be deducted from each transaction requested by users. 
# Such as .08 for %8, .12 for %12
TX_FEE_PERCENTAGE = 0.02
FEE_ADDRESS = "FEES"

# Min delay in mixing and sending coins to final destination address. In seconds
TX_DELAY_MIN_SEC = 1.0

# Max delay in mixing and sending coins to final destination address. In seconds
TX_DELAY_MAX_SEC = 3.0

# How often to pull the coin network for user deposits. In seconds
API_POLL_TIME_SEC = 1.0

# How much to wait for user deposits to appear on network before cancelling a transaction. In seconds
MAX_WAIT_TIME_FOR_DEPOSITS_SEC = 20.0 

MESSAGE_INSUFFICIENT_FUNDS = 'Insufficient funds'
MESSAGE_TIMEOUT = 'Transaction timed out'
MESSAGE_HOUSE_ADDR_MISSING = 'House address is missing'
MESSAGE_QUEUE_MISSING = 'No queue was given'
MESSAGE_DEPOSIT_ADDR_MISSING = 'Deposit address is missing'
MESSAGE_DESTINATION_ADDR_MISSING = 'No destination address is specified'
MESSAGE_AMOUNT_MISSING = 'Transfer amount should be larger than 0.0'
MESSAGE_MIXINFO_MISSING = 'Expecting a JobCoinMixInfo received none.'
MESSAGE_TRANSFERINFO_MISSING = 'Expecting a JobCoinTransferInfo received none.'
MESSAGE_UNEXPECTED_ITEM_IN_QUEUE = 'Expecting a JobCoinMixInfo in queue, received something else.'