import json
import sys
import subprocess

def get_bash_command_output(command):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    return result.stdout.strip()

def address_to_hex(address):
    json_output = get_bash_command_output(f"dymd keys parse {address} --output json --keyring-backend test")
    return "0x" + json.loads(json_output)['bytes']

def update_genesis_file(input_file, output_file, key1, key2, key3):
    '''
    Parameters:
    input_file: The input genesis file. This file contains the initial state and configurations of the blockchain.
    output_file: The output genesis file. This file will be the modified version of the input file with necessary updates.
    key_name: The name of the key used to sign the genesis file. This key is used in the validator's signing information.
    '''
    # Retrieving the consensus address, validator address, and public key using bash commands
    consensus_address = get_bash_command_output("dymd tendermint show-address")
    validator_address = get_bash_command_output(f"dymd keys show {key_name} --bech val --output json --keyring-backend test")
    account_address = get_bash_command_output(f"dymd keys show {key_name} --bech acc --output json --keyring-backend test")
    validator_pubkey = get_bash_command_output("dymd tendermint show-validator")
    validator_address_json = json.loads(validator_address)
    validator_address = validator_address_json["address"]
    account_address_json = json.loads(account_address)
    account_address = account_address_json["address"]
    account_pubkey = json.loads(account_address_json["pubkey"])["key"]
    validator_public_key = json.loads(validator_pubkey)["key"]

    # Printing the consensus address, validator address, and public key
    print(f"Consensus Address: {consensus_address}")
    print(f"Address: {validator_address}")
    print(f"Account Address: {account_address}")
    print(f"Validator Public Key: {validator_public_key}")
    print(f"Account Public Key: {account_pubkey}")

    with open(input_file, 'r') as file:
        data = json.load(file)

    # Updating app_state
    data['validators'] = []

    # Deleting specific sections in staking
    staking_sections = ['delegations', 'redelegations', 'unbonding_delegations']
    for section in staking_sections:
        data['app_state']['staking'][section] = []

    # Update last_validator_powers
    last_total_power = data['app_state']['staking']['last_total_power']
    data['app_state']['staking']['last_validator_powers'] = [{
        'address': validator_address,
        'power': last_total_power
    }]
    
    # Give the validator address some balance. The balance should first be taken from the not_bonded_tokens_pool. if it's not found than 
    # take it from a random account with more than 1000000 udym
    not_bonded_tokens_account = next(acc for acc in data['app_state']['auth']['accounts'] if acc.get('name') == 'not_bonded_tokens_pool')
    try:
        not_bonded_tokens_balance = next(balance for balance in data['app_state']['bank']['balances'] if balance['address'] == not_bonded_tokens_account['base_account']['address'])
        not_bonded_tokens_balance['address'] = account_address
    except StopIteration:
        for balance in data['app_state']['bank']['balances']:
            if balance['coins' ][0]['denom'] == 'udym' and int(balance['coins'][0]['amount']) > 1000000:
                balance['address'] = account_address
                break

    # Iterate over the account and change the first account from type /ethermint.types.v1.EthAccount to 
    # have the address as the account_address and the key is the public key
    for account in data['app_state']['auth']['accounts']:
        if account.get('@type') == '/ethermint.types.v1.EthAccount' and account["base_account"]["sequence"] != "0":
            previous_address = account['base_account']['address']
            account['base_account']['address'] = account_address
            account['base_account']['pub_key'] = {
                "@type": "/ethermint.crypto.v1.ethsecp256k1.PubKey",
                "key": account_pubkey
            }
            print(f"ETH account: {account['base_account']}")
            break
        
    # for account in auth[:]:
    #     if account.get('@type') == '/ethermint.types.v1.EthAccount' and account["base_account"]["sequence"] == "0":
    #         auth.remove(account)
    # data['app_state']['auth']['accounts'] = auth

    # Turn previous_address to hex and find that hex in the app_state.evm.accounts and change the address to account_address hex
    previous_address_hex = address_to_hex(previous_address)
    for account in data['app_state']['evm']['accounts']:
        if account['address'].lower() == previous_address_hex.lower():
            account['address'] = address_to_hex(account_address)
            break

    # Update the last validator in staking.validators
    bonded_tokens_account = next(acc for acc in data['app_state']['auth']['accounts'] if acc.get('name') == 'bonded_tokens_pool')
    bonded_tokens_balance = next(balance for balance in data['app_state']['bank']['balances'] if balance['address'] == bonded_tokens_account['base_account']['address'])

    if data['app_state']['staking']['validators']:
        last_validator = data['app_state']['staking']['validators'][-1]
        last_validator['consensus_pubkey']['key'] = validator_public_key
        last_validator['operator_address'] = validator_address
        last_validator['tokens'] = bonded_tokens_balance['coins'][0]['amount']
        last_validator['status'] = "BOND_STATUS_BONDED"

        data['app_state']['staking']['validators'] = [last_validator]

    # Update the last element in app_state.slashing_signing_infos
    if data['app_state']['slashing']['signing_infos']:
        last_signing_info = data['app_state']['slashing']['signing_infos'][-1]
        last_signing_info['address'] = consensus_address
        last_signing_info['validator_signing_info']['address'] = consensus_address

    # Update voting params and min deposit
    data['app_state']['gov']['voting_params']['voting_period'] = "60s"
    data['app_state']['gov']['deposit_params']['min_deposit'][0]['amount'] = "1000000"

    # Writing the updated data to the output file
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    input_file, output_file, key1, key2, key3 = sys.argv[1:6]
    update_genesis_file(input_file, output_file, key1, key2, key3)