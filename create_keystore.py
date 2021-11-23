import eth_account
import sys

from brownie.network.account import Accounts


ADDRESS_FILE = './keystore.address'
MNEMONIC_FILE = './keystore.mnemonic'
KEYSTORE_FILE = './keystore.json'


def main():
    if len(sys.argv) != 3:
        print('usage: {} keystore-password keystore-base-base'.format(sys.argv[0]))
        sys.exit(1)

    # create mnemonic
    eth_account.Account.enable_unaudited_hdwallet_features()
    _, mnemonic = eth_account.Account.create_with_mnemonic()

    # retrieve command line args
    password = sys.argv[1]
    keystore_base = sys.argv[2]

    # create account
    accounts = Accounts()
    account = accounts.from_mnemonic(
        mnemonic=mnemonic, 
        count=1,
        offset=0,
        passphrase='')
    
    # write address file and mnemonic
    with open('{}.address'.format(keystore_base), 'w') as fa:
        fa.write(account.address)
        
    # write address file and mnemonic
    with open('{}.mnemonic'.format(keystore_base), 'w') as fm:
        fm.write('{}\n'.format(mnemonic))
        
    # export to keystore
    account.save('{}.json'.format(keystore_base), password=password)


if __name__ == "__main__":
    main()
