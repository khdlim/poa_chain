def eth_to_wei(x):
    return int(x * 1e18)


def wei_to_eth(x):
    return x / 1e18


def eth_to_gwei(x):
    return int(x * 1e9)


def gwei_to_eth(x):
    return x / 1e9


def hex_to_int(hex_str):
    return int(hex_str.split("x")[1], 16)


def int_to_hex(x):
    return hex(x)
