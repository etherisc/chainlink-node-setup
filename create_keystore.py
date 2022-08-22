import eth_account
import sys

from brownie.network.account import Accounts


ADDRESS_FILE = './secrets/{}.address'
MNEMONIC_FILE = './secrets/{}.mnemonic'
KEYSTORE_FILE = './secrets/{}.json'

def main():
    if len(sys.argv) != 3:
        print('usage: {} keystore-password keystore-base'.format(sys.argv[0]))
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
    with open(ADDRESS_FILE.format(keystore_base), 'w') as fa:
        fa.write(account.address)
        
    # write address file and mnemonic
    with open(MNEMONIC_FILE.format(keystore_base), 'w') as fm:
        fm.write('{}\n'.format(mnemonic))
        
    # export to keystore
    account.save(KEYSTORE_FILE.format(keystore_base), password=password)


if __name__ == "__main__":
    main()
