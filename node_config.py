class NodeConfig:
    def __init__(self, address, ethsigner_rpc_addr, node_rpc_addr):
        self.address = address
        self.ethsigner_rpc_addr = ethsigner_rpc_addr
        self.node_rpc_addr = node_rpc_addr


node1 = NodeConfig(
    "0xadb5a42ce9c486e4a28428452bc4d3c6b497257c",
    "http://localhost:8590",
    "http://localhost:8549",
)

node2 = NodeConfig(
    "0xf17f52151EbEF6C7334FAD080c5704D77216b732",
    "http://localhost:8591",
    "http://localhost:8550",
)


mm_addr = "0x25eEb729929c0b502A5bCd2eCF9Afcb7d862F33F"

finalize_delay_sec = 5
