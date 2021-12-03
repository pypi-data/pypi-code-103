from swivel.abstracts import VaultTracker as base
from .abi import VAULT_TRACKER

class VaultTracker(base):
    def __init__(self, v):
        """
        Parameters:
            v (W3) Instance of a vendor W3 class (no other vendors are supported as of now)
        """
        self.vendor = v
        self.abi = VAULT_TRACKER

    def admin(self, opts=None):
        return self.contract.functions.admin(), opts

    def c_token_address(self, opts=None):
        return self.contract.functions.cTokenAddr(), opts

    def swivel(self, opts=None):
        return self.contract.functions.swivel(), opts

    def maturity(self, opts=None):
        return self.contract.functions.maturity(), opts

    def maturity_rate(self, opts=None):
        return self.contract.functions.maturityRate(), opts

    def vaults(self, o, opts=None):
        return self.contract.functions.vaults(o), opts
    
    def balances_of(self, o, opts=None):
        return self.contract.functions.balancesOf(o), opts
