from web3 import Web3
from etherswarm.utils import env

__all__ = ["provider"]


def init_provider(entry_point=env("ENTRY_POINT")) -> Web3:
    protocol = entry_point.split("://")[0]
    if protocol in ["ws", "wss"]:
        return Web3(Web3.WebsocketProvider(entry_point))
    if protocol in ["http", "https"]:
        return Web3(Web3.HTTPProvider(entry_point))
    raise Exception("Unknow or Invalid entry point: %s" % entry_point)

provider = init_provider()
