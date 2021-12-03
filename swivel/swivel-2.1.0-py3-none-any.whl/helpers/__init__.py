from web3 import Web3

def call(args):
    return args[0].call(args[1])

def transact(args):
    """For unlocked accounts, we can simply call transact directly"""

    return args[0].transact(args[1])

# TODO **?
def v_r_s_to_dict(t):
    """Transform the py-eth-sig-utils VRS tuple into a dict"""

    return {'v': t[0], 'r': Web3.toBytes(t[1]), 's': Web3.toBytes(t[2])}
