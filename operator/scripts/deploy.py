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

# use node account to deploy operator contract
CHAINLINK_DIR = '/opt/chainlinknode' 
KEYSTORE_FILE = '{}/keystore.json'.format(CHAINLINK_DIR)
PASSWORD_FILE = '{}/password'.format(CHAINLINK_DIR)

# output file with address of deployed operator
OPERATOR_ADDRESS_FILE = '{}/operator.address'.format(CHAINLINK_DIR)


def get_node_account():
    if os.path.exists(KEYSTORE_FILE):
        with open(PASSWORD_FILE) as f:
            password = f.readline().strip()
        
        return accounts.load(filename=KEYSTORE_FILE, password=password) 

    return get_account()


def main():
    account = get_node_account()
    link_contract = get_contract('link_token')

    print('link address {}'.format(link_contract.address))
    print('deployer address {}'.format(account.address))
    print('owner address {}'.format(account.address))

    # unsure funding of the chainlink node account
    i = 0
    while account.balance() == 0.0:
        print('{} waiting for funding of {}'.format(i, account.address))
        time.sleep(10)
        i += 1

    # deploy operator contract with node account as contract owner
    print('deploying operator contract')
    operator = ChainlinkOperator.deploy(
        link_contract.address, 
        account.address, 
        { 'from': account.address })
    
    print('operator contract address {}'.format(operator.address))
    print('writing contract address to file {}'.format(OPERATOR_ADDRESS_FILE))
    with open(OPERATOR_ADDRESS_FILE, 'w') as f:
        f.write(operator.address)

    # call using chainlink node account after deploying operator to add 
    # node account to allowed sender list. 
    # fulfillOracleRequest and fulfillOracleRequest2 may only be called from addresses registered as authorized senders
    print('add contract owner address to authorized senders (= accounts from chainlink nodes that are allowed to call )')
    authorized_senders = [account.address]
    operator.setAuthorizedSenders(authorized_senders)

    print('isAuthorizedSender({}): {}'.format(account.address, operator.isAuthorizedSender(account.address)))
    print('getAuthorizedSenders(): {}'.format(operator.getAuthorizedSenders()))
    print('deploy and initialization of operator contract done')
