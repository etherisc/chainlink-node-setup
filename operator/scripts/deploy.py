import os
import time

from brownie import (
    network,
    accounts,
    config,
    ChainlinkOperator,
)

from scripts.helpful_scripts import get_account
from scripts.helpful_scripts import get_contract

# name of imported account to deploy operator contract
NODE_ACCOUNT = 'node_account'
KEYSTORE_FILE = './{}.json'

PASSWORD_ENV = 'NODE_ACCOUNT_PW'
KEYSTORE_ENV = 'NODE_ACCOUNT_KEYSTORE'
OPERATOR_ADDRESS_FILE = './operator.address'

def get_account_local():
    if os.environ[KEYSTORE_ENV] and os.environ[PASSWORD_ENV]:
        keystore_file = os.environ[KEYSTORE_ENV]
        password = os.environ[PASSWORD_ENV]

        return accounts.load(filename=keystore_file, password=password) 

    return get_account()


def main():
    account = get_account_local()
    link_contract = get_contract('link_token')

    print('link address {}'.format(link_contract.address))
    print('deployer address {}'.format(account.address))
    print('owner address {}'.format(account.address))

    i = 0
    while account.balance() == 0.0:
        print('waiting for funding of {}'.format(account.address))
        time.sleep(5)
        i += 1

        if i > 2:
            accounts[0].transfer(account, "0.01 ether")

    operator = ChainlinkOperator.deploy(
        link_contract.address, 
        account.address, 
        { 'from': account.address })
    
    print('contract address {}'.format(operator.address))
    with open(OPERATOR_ADDRESS_FILE, 'w') as f:
        f.write(operator.address)

    print('getAuthorizedSenders(): {}'.format(operator.getAuthorizedSenders()))

    # needs to be called by chainlink node after deploying operator to add itself
    # to allowed sender list. 
    # fulfillOracleRequest and fulfillOracleRequest2 may only be called from addresses registered as authorized senders
    print('add contract owner address to authorized senders (= accounts from chainlink nodes that are allowed to call )')
    authorized_senders = [account.address]
    operator.setAuthorizedSenders(authorized_senders)

    print('isAuthorizedSender({}): {}'.format(account.address, operator.isAuthorizedSender(account.address)))
    print('getAuthorizedSenders(): {}'.format(operator.getAuthorizedSenders()))
    print('deploy and initialization of operator contract done')
