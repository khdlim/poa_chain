import sys
import requests
from conversion import wei_to_eth, hex_to_int


class Requester:
    def __init__(self, rpc_address):
        self.session = requests.session()
        self.rpc_address = rpc_address
        self.headers = {"Content-type": "application/json"}

    def send_request(self, method, params):
        # print("Sending request to %s" % self.rpc_address)
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}

        response = self.session.post(
            self.rpc_address, json=payload, headers=self.headers
        )
        return response.json()


def send_ether(
    sender_addr, recipient_addr, gas, gas_price_gwei, value_eth, ethsigner_rpc_addr
):
    # gas = "0x7600"
    # gasPrice = "0x9184e72a000"
    # value = "0x01000000000"
    # sender_addr = "0xf17f52151EbEF6C7334FAD080c5704D77216b732"
    # recipient_addr = "0xf7a76a078f914d602d409d41a50132c971bcd342"
    gas_hex_str = hex(gas)
    gasPrice_hex_str = hex(gas_price_gwei)
    value_gwei_hex_str = hex(int(value_eth * 1e18))

    r = Requester(ethsigner_rpc_addr)
    try:
        resp = r.send_request("eth_getTransactionCount", [sender_addr, "pending"])
        nonce_hex_str = resp["result"]
    except:
        raise IOError("Error getting nonce for %s" % sender_addr)

    params = [
        {
            "from": sender_addr,
            "to": recipient_addr,
            "gas": gas_hex_str,
            "gasPrice": gasPrice_hex_str,
            "value": value_gwei_hex_str,
            "nonce": nonce_hex_str,
        }
    ]
    # print(params)
    r = Requester(ethsigner_rpc_addr)
    resp = r.send_request("eth_sendTransaction", params)
    if "error" in resp:
        print(resp)
        sys.exit(1)
    return resp


def check_balance(query_address, rpc_node_addr="http://localhost:8550"):
    # print("Checking balances before transfer")
    r_ = Requester(rpc_node_addr)
    resp = r_.send_request("eth_getBalance", [query_address, "latest"])
    if "error" in resp:
        print(resp)
        sys.exit(1)
    balance = wei_to_eth(hex_to_int(resp["result"]))
    print("Address %s balance is %s ETH" % (query_address, balance))
    return balance


def deploy_contract(
    sender_addr,
    ethsigner_rpc_addr,
    web3_deploy_json,
):
    r = Requester(ethsigner_rpc_addr)
    resp = r.send_request("eth_getTransactionCount", [sender_addr, "pending"])
    nonce_hex_str = resp["result"]

    # Convert web3.py params to ethsigner params
    ethsigner_params = [
        {
            "nonce": nonce_hex_str,
            "from": sender_addr,
            "to": None,
            "gas": hex(web3_deploy_json["gas"]),
            "gasPrice": hex(web3_deploy_json["gasPrice"]),
            "data": web3_deploy_json["data"],
            "value": "0x00",
        }
    ]
    r = Requester(ethsigner_rpc_addr)
    resp = r.send_request("eth_sendTransaction", ethsigner_params)
    if "error" in resp:
        print(resp)
        sys.exit(1)
    return resp


def call_contract_transaction(
    tx_dict,
    ethsigner_rpc_addr,
):
    r = Requester(ethsigner_rpc_addr)
    resp = r.send_request("eth_getTransactionCount", [tx_dict["from"], "pending"])
    if "error" in resp:
        print(resp)
        sys.exit(1)
    nonce_hex_str = resp["result"]
    tx_dict["nonce"] = nonce_hex_str
    resp = r.send_request("eth_sendTransaction", [tx_dict])
    if "error" in resp:
        print(resp)
        sys.exit(1)

    return resp
