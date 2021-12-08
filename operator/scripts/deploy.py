import os
import time

from brownie import (
    network,
    accounts,
    config,
    ChainlinkOperator,
    ChainlinkTestClient
)

from brownie.convert.normalize import format_event

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
        
        print('using keystore file {} to deploy operator contract'.format(KEYSTORE_FILE))
        return accounts.load(filename=KEYSTORE_FILE, password=password) 

    print('no keystore file {} found, using fallback account'.format(KEYSTORE_FILE))
    return get_account()


def pp_event(event, prefix='') -> str:
    lines = []
    for i, log in enumerate(event):
        lines.append('{}log[{}]'.format(prefix, i))
        for key, value in log.items():
            lines.append('{}  {}: {}'.format(prefix, key, value))
    
    return '\n'.join(lines)


def pp_events(events, prefix='') -> str:
    lines = []
    for key, event in events.items():
        lines.append('{}{}\n{}'.format(prefix, key, pp_event(event, '{}  '.format(prefix))))
    
    return '\n'.join(lines)


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

    if os.path.exists(CHAINLINK_DIR):
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

    # deploy (local) test client contract
    if not os.path.exists(CHAINLINK_DIR):
        test_job_id = 'id42'

        print('\ndeploying chainlink test client contract')
        client = ChainlinkTestClient.deploy({ 'from': account.address })
        print('test client contract address {}'.format(client.address))

        print('set link token contract for test client to {}'.format(link_contract.address))
        tx = client.setLinkTokenAddress(link_contract.address)
        print('tx events for client.setLinkTokenAddress {}'.format(tx.events))

        print('verify link token contract address via client.getLinkTokenAddress()'.format(link_contract.address))
        link_address = client.getLinkTokenAddress()
        print('return value {}'.format(link_address))

        print('request eth price via call to operator {}'.format(operator.address))
        tx = client.requestEthereumPrice(operator.address, test_job_id)
        print('tx events for client.requestEthereumPrice\n{}'.format(pp_events(tx.events, '  ')))
