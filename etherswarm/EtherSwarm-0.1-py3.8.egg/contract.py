from etherswarm.provider import provider as P
from etherswarm.gasprice import gasPrice
import json
from functools import partial

def load_contract(addr, abi_path, prov=P):
    with open(abi_path) as f:
        abi = json.load(f)
        if "abi" in abi.keys():
            abi = abi["abi"]
        ctrt = P.eth.contract(addr, abi=abi)
        for fn in ctrt.functions._functions:
            fn_name = fn["name"]
            hooked = contract_hooker(ctrt.functions.__getattribute__(fn_name))
            ctrt.functions.__setattr__(fn_name, hooked)
        return ctrt


def contract_hooker(fn):
    def _(*args, **kwargs):
        ret = fn(*args, **kwargs)
        return ret
    return _
