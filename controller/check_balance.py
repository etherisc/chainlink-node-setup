from brownie import network
from brownie import web3
from brownie.network import accounts

network.connect('xdai-main')

print('is connected: {}'.format(network.is_connected()))
print('show active: {}'.format(network.show_active()))

account = accounts.at('0xFa7ACf72337f67a542620f3B9F5A3f8b7Fb68C45', force=True)
print('account: {}'.format(account.address))
print('balance: {}'.format(account.balance()))
print('balance: {:,.6f} DAI'.format(web3.fromWei(account.balance(), 'ether')))
