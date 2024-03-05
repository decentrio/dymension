import json
import sys
import subprocess

def get_bash_command_output(command):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    return result.stdout.strip()

def address_to_hex(address):
    json_output = get_bash_command_output(f"dymd keys parse {address} --output json --keyring-backend test --home v1")
    return "0x" + json.loads(json_output)['bytes']

def update_genesis_file(input_file, output_file, key1, key2, key3):
    '''
    Parameters:
    input_file: The input genesis file. This file contains the initial state and configurations of the blockchain.
    output_file: The output genesis file. This file will be the modified version of the input file with necessary updates.
    key_name: The name of the key used to sign the genesis file. This key is used in the validator's signing information.
    '''
    # Retrieving the consensus address, validator address, and public key using bash commands
    consensus_address_1 = get_bash_command_output(f"dymd tendermint show-address --home {key1}")
    consensus_address_2 = get_bash_command_output(f"dymd tendermint show-address --home {key2}")
    consensus_address_3 = get_bash_command_output(f"dymd tendermint show-address --home {key3}")

    validator_address_1 = json.loads(get_bash_command_output(f"dymd keys show {key1} --bech val --output json --keyring-backend test --home {key1}"))["address"]
    validator_address_2 = json.loads(get_bash_command_output(f"dymd keys show {key2} --bech val --output json --keyring-backend test --home {key2}"))["address"]
    validator_address_3 = json.loads(get_bash_command_output(f"dymd keys show {key3} --bech val --output json --keyring-backend test --home {key3}"))["address"]

    account_address_1 = json.loads(get_bash_command_output(f"dymd keys show {key1} --bech acc --output json --keyring-backend test --home {key1}"))["address"]
    account_address_2 = json.loads(get_bash_command_output(f"dymd keys show {key2} --bech acc --output json --keyring-backend test --home {key2}"))["address"]
    account_address_3 = json.loads(get_bash_command_output(f"dymd keys show {key3} --bech acc --output json --keyring-backend test --home {key3}"))["address"]

    validator_pubkey_1 = json.loads(get_bash_command_output(f"dymd tendermint show-validator --home {key1}"))["key"]
    validator_pubkey_2 = json.loads(get_bash_command_output(f"dymd tendermint show-validator --home {key2}"))["key"]
    validator_pubkey_3 = json.loads(get_bash_command_output(f"dymd tendermint show-validator --home {key3}"))["key"]

    account_pubkey_1 = json.loads(json.loads(get_bash_command_output(f"dymd keys show {key1} --bech acc --output json --keyring-backend test --home {key1}"))["pubkey"])["key"]
    account_pubkey_2 = json.loads(json.loads(get_bash_command_output(f"dymd keys show {key2} --bech acc --output json --keyring-backend test --home {key2}"))["pubkey"])["key"]
    account_pubkey_3 = json.loads(json.loads(get_bash_command_output(f"dymd keys show {key3} --bech acc --output json --keyring-backend test --home {key3}"))["pubkey"])["key"]

    # Printing the consensus address, validator address, and public key
    print(f"Consensus Address 1: {consensus_address_1}")
    print(f"Address 1: {validator_address_1}")
    print(f"Account Address 1: {account_address_1}")
    print(f"Validator Public Key 1: {validator_pubkey_1}")
    print(f"Account Public Key 1: {account_pubkey_1}")

    print(f"Consensus Address 2: {consensus_address_2}")
    print(f"Address 2: {validator_address_2}")
    print(f"Account Address 2: {account_address_2}")
    print(f"Validator Public Key 2: {validator_pubkey_2}")
    print(f"Account Public Key 2: {account_pubkey_2}")

    print(f"Consensus Address 3: {consensus_address_3}")
    print(f"Address 3: {validator_address_3}")
    print(f"Account Address 3: {account_address_3}")
    print(f"Validator Public Key 3: {validator_pubkey_3}")
    print(f"Account Public Key 3: {account_pubkey_3}")

    with open(input_file, 'r') as file:
        data = json.load(file)

    # Updating app_state
    data['validators'] = []

    # Deleting specific sections in staking
    staking_sections = ['delegations', 'redelegations', 'unbonding_delegations']
    for section in staking_sections:
        data['app_state']['staking'][section] = []

    # Update last_validator_powers
    last_total_power = int(data['app_state']['staking']['last_total_power'])
    val_power = int(last_total_power / 3)
    data['app_state']['staking']['last_validator_powers'] = [
        {
            'address': validator_address_1,
            'power': str(val_power)
        },
        {
            'address': validator_address_2,
            'power': str(val_power)
        },
        {
            'address': validator_address_3,
            'power': str(last_total_power - 2 * val_power)
        }
    ]

    counter = 0
    
    # Give the validator address some balance. The balance is taken from a random account with more than 1000000 udym
    for balance in data['app_state']['bank']['balances']:
        if balance['coins' ][0]['denom'] == 'udym' and int(balance['coins'][0]['amount']) > 1000000:
            counter += 1
            if (counter == 1):
                balance['address'] = account_address_1
            elif (counter == 2):
                balance['address'] = account_address_2
            elif (counter == 3):
                balance['address'] = account_address_3
                counter = 0
                break

    # Iterate over the account and change the first account from type /ethermint.types.v1.EthAccount to 
    # have the address as the account_address and the key is the public key
    for account in data['app_state']['auth']['accounts']:
        if account.get('@type') == '/c' and account["base_account"]["sequence"] != "0":
            counter += 1
            if (counter == 1):
                previous_address_1 = account['base_account']['address']
                account['base_account']['address'] = account_address_1
                account['base_account']['pub_key'] = {
                    "@type": "/ethermint.crypto.v1.ethsecp256k1.PubKey",
                    "key": account_pubkey_1
                }
                print(f"ETH account: {account['base_account']}")
            if (counter == 2):
                previous_address_2 = account['base_account']['address']
                account['base_account']['address'] = account_address_2
                account['base_account']['pub_key'] = {
                    "@type": "/ethermint.crypto.v1.ethsecp256k1.PubKey",
                    "key": account_pubkey_2
                }
                print(f"ETH account: {account['base_account']}")
            if (counter == 3):
                previous_address_3 = account['base_account']['address']
                account['base_account']['address'] = account_address_3
                account['base_account']['pub_key'] = {
                    "@type": "/ethermint.crypto.v1.ethsecp256k1.PubKey",
                    "key": account_pubkey_3
                }
                print(f"ETH account: {account['base_account']}")
                counter = 0
                break

    # Turn previous_address to hex and find that hex in the app_state.evm.accounts and change the address to account_address hex
    previous_address_1_hex = address_to_hex(previous_address_1)
    previous_address_2_hex = address_to_hex(previous_address_2)
    previous_address_3_hex = address_to_hex(previous_address_3)
    for account in data['app_state']['evm']['accounts']:
        if account['address'].lower() == previous_address_1_hex.lower():
            account['address'] = address_to_hex(account_address_1)
            counter += 1
        elif account['address'].lower() == previous_address_2_hex.lower():
            account['address'] = address_to_hex(account_address_2)
            counter += 1
        elif account['address'].lower() == previous_address_3_hex.lower():
            account['address'] = address_to_hex(account_address_3)
            counter += 1
        if counter == 3:
            break

    # Update the last validator in staking.validators
    bonded_tokens_account = next(acc for acc in data['app_state']['auth']['accounts'] if acc.get('name') == 'bonded_tokens_pool')
    bonded_tokens_balance = next(balance for balance in data['app_state']['bank']['balances'] if balance['address'] == bonded_tokens_account['base_account']['address'])
    bonded_tokens = int(bonded_tokens_balance['coins'][0]['amount'])
    bonded_token = int(bonded_tokens / 3)

    if data['app_state']['staking']['validators']:
        validator_1 = data['app_state']['staking']['validators'][0]
        validator_1['consensus_pubkey']['key'] = validator_pubkey_1
        validator_1['operator_address'] = validator_address_1
        validator_1['tokens'] = str(bonded_token)
        validator_1['status'] = "BOND_STATUS_BONDED"

        validator_2 = data['app_state']['staking']['validators'][1]
        validator_2['consensus_pubkey']['key'] = validator_pubkey_2
        validator_2['operator_address'] = validator_address_2
        validator_2['tokens'] = str(bonded_token)
        validator_2['status'] = "BOND_STATUS_BONDED"

        validator_3 = data['app_state']['staking']['validators'][2]
        validator_3['consensus_pubkey']['key'] = validator_pubkey_3
        validator_3['operator_address'] = validator_address_3
        validator_3['tokens'] = str(bonded_tokens - 2 * bonded_token)
        validator_3['status'] = "BOND_STATUS_BONDED"

        data['app_state']['staking']['validators'] = [validator_1, validator_2, validator_3]

    # Update the last element in app_state.slashing_signing_infos
    if data['app_state']['slashing']['signing_infos']:
        data['app_state']['slashing']['signing_infos'][-1]['address'] = consensus_address_1
        data['app_state']['slashing']['signing_infos'][-1]['validator_signing_info']['address'] = consensus_address_1

        data['app_state']['slashing']['signing_infos'][-2]['address'] = consensus_address_2
        data['app_state']['slashing']['signing_infos'][-2]['validator_signing_info']['address'] = consensus_address_2

        data['app_state']['slashing']['signing_infos'][-3]['address'] = consensus_address_3
        data['app_state']['slashing']['signing_infos'][-3]['validator_signing_info']['address'] = consensus_address_3

    # Update voting params and min deposit
    data['app_state']['gov']['voting_params']['voting_period'] = "60s"
    data['app_state']['gov']['deposit_params']['min_deposit'][0]['amount'] = "1000000"

    # Writing the updated data to the output file
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    input_file, output_file, key1, key2, key3 = sys.argv[1:6]
    update_genesis_file(input_file, output_file, key1, key2, key3)