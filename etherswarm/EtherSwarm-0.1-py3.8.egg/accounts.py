from etherswarm.utils import env
from hashlib import sha256
import web3
import json
from etherswarm.provider import provider as P
from etherswarm.cmd import command, router, output


def privates(num: int, seed=env("SK_SEED")) -> bytes:
    if type(seed) is not bytes:
        seed = seed.encode()
    n = str(num).encode()
    return sha256(sha256(seed + n).digest() + n).digest()


def accounts(num: int):
    return web3.eth.Account.privateKeyToAccount(privates(num))


def list_accounts(s, e, callback=lambda x: None):
    ret = []
    for i in range(s, e):
        ret.append((i, accounts(i).address, callback(i)))
    return ret


@command
@output
def get_balance(num):
    '''
    show balance of account
    get_balance <index>
    '''
    return float(P.fromWei(P.eth.getBalance(accounts(num).address), "ether"))


@command
@output
def as_keystore(index: int, psw: str):
    '''
    show private as keystore
    as_keystore <index> <password>
    '''
    return web3.Account.encrypt(privates(index), psw)


@command
@output
def dump_as_keystore(index: int, psw: str, path: str):
    '''
    dump private key as keystore file
    dump_as_keystore <index> <password> <file_path>
    '''
    return json.dump(web3.Account.encrypt(privates(index), psw), open(path, "w+"))
