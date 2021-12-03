from swivel.abstracts import Deployed
from .abi import CERC20

class CErc20(Deployed):
    def __init__(self, v):
        self.vendor = v
        self.abi = CERC20

    def exchange_rate_current_returns(self, n, opts=None):
        return self.contract.functions.exchangeRateCurrentReturns(n), self.tx_opts(opts)
