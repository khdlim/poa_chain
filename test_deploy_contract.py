import json
import os
import sys
import time

from tqdm import tqdm
from web3 import Web3
from web3.middleware import geth_poa_middleware

from chain_utils import deploy_contract, call_contract_transaction
from config import node1, node2


def tsleep(finalize_delay_sec):
    print("Sleeping %d seconds to finalize" % finalize_delay_sec)
    for _ in tqdm(range(finalize_delay_sec)):
        time.sleep(1)


def main():

    in_file = "contracts/storage_constructor_sol_Storage.abi"
    print("Reading ABI from %s" % in_file)
    with open(in_file, "r") as f:
        abi = json.load(f)

    in_file = "contracts/storage_constructor_sol_Storage.bin"
    print("Reading bytecode from %s" % in_file)
    with open(in_file, "r") as f:
        bin = f.read()

    print("Connecting to RNode-2 RPC")
    w3 = Web3(Web3.HTTPProvider(node2.node_rpc_addr))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    print("Current block number is %s" % w3.eth.block_number)

    if not os.path.exists("contract_address.txt"):
        initial_value = 7
        print("Deploying contract with initial value of %d" % initial_value)

        cont_ = w3.eth.contract(abi=abi, bytecode=bin)
        web3_deploy_json = cont_.constructor(initial_value).buildTransaction()
        print("Deploying smart contract")
        resp = deploy_contract(
            node2.address, node2.ethsigner_rpc_addr, web3_deploy_json
        )
        if "error" in resp:
            print("Error deploying contract: %s" % resp)
            sys.exit(1)

        tx_hash = resp["result"]
        print("TX hash is %s" % tx_hash)

        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        print(
            "Successfully deployed, contract address is %s" % tx_receipt.contractAddress
        )

        with open("contract_address.txt", "w") as f:
            print(tx_receipt.contractAddress, file=f)
        contract_address = tx_receipt.contractAddress

    else:
        print("contract_address.txt found, contract deployed")
        with open("contract_address.txt", "r") as f:
            contract_address = f.read().strip()
        print("Contract_address is %s" % contract_address)

    contract = w3.eth.contract(address=contract_address, abi=abi)
    print("-" * 80)
    print("")
    print("Calling retrieve() on smart contract at %s" % contract_address)
    result = contract.functions.retrieve().call()
    print("Current stored value is %d" % result)

    for value_to_store in (25, 100):
        print("-" * 80)
        print("")
        print(
            "Calling store(%d) on smart contract at %s"
            % (value_to_store, contract_address)
        )
        gas = 50000
        gas_price_gwei = 1000
        s = contract.functions.store(value_to_store).buildTransaction(
            {
                "from": node2.address,
                "gas": hex(gas),
                "gasPrice": hex(gas_price_gwei),
                "value": "0x0",
            }
        )
        resp = call_contract_transaction(s, node2.ethsigner_rpc_addr)
        # print(resp)

        tsleep(4)
        print("Calling retrieve() on smart contract at %s" % contract_address)
        result = contract.functions.retrieve().call()
        print("Current stored value is %d" % result)


if __name__ == "__main__":
    main()
