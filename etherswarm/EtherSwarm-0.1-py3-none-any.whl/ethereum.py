from etherswarm.provider import provider as P
from etherswarm.accounts import accounts, privates
from etherswarm.gasprice import gasPrice


def update_gas(tx):
    gas = P.eth.estimateGas(tx)
    tx.update({"gas": int(gas * 1.1)})
    return tx


def sign(tx, i, nonce_bias=0):
    if not tx.get("nonce"):
        tx["nonce"] = nonce_bias + P.eth.getTransactionCount(accounts(i).address)
    tx = update_gas(tx)
    return P.eth.account.sign_transaction(tx, privates(i))


def send(signed):
    return P.eth.sendRawTransaction(signed.rawTransaction)


def transfer(_fid, _tid, _value, nonce_bias=0, speed="fast"):
    tx = {
        "from": accounts(_fid).address,
        "to": accounts(_tid).address,
        "chainId": 1,
        "nonce": nonce_bias + P.eth.getTransactionCount(accounts(_fid).address),
        'gas': 21000,
        "value": P.toWei(_value, "ether"),
        "gasPrice": gasPrice(speed)
    }
    return send(sign(tx, _fid)).hex()
