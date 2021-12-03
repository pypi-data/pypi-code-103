from py_eth_sig_utils.signing import signature_to_v_r_s
from swivel.helpers import v_r_s_to_dict
from swivel.abstracts import Swivel as base
from .abi import SWIVEL

class Swivel(base):
    def __init__(self, v):
        """
        Parameters:
            v (W3) Instance of a vendor W3 class (no other vendors are supported as of now)
        """
        self.vendor = v
        self.abi = SWIVEL

    def name(self, opts=None):
        return self.contract.functions.NAME(), opts

    def version(self, opts=None):
        return self.contract.functions.VERSION(), opts

    def hold(self, opts=None):
        return self.contract.functions.HOLD(), opts

    def domain(self, opts=None):
        return self.contract.functions.domain(), opts

    def market_place(self, opts=None):
        return self.contract.functions.marketPlace(), opts

    def admin(self, opts=None):
        return self.contract.functions.admin(), opts

    def transfer_admin(self, a, opts=None):
        return self.contract.functions.transferAdmin(a), self.tx_opts(opts)

    def min_feenominator(self, opts=None):
        return self.contract.functions.MIN_FEENOMINATOR(), opts

    def feenominators(self, i, opts=None):
        return self.contract.functions.feenominators(i), opts

    def initiate(self, orders, a, s, opts=None):
        # normalize the full signatures to a tuple of vrs components (tuples)
        components = tuple(map(lambda sig: v_r_s_to_dict(signature_to_v_r_s(self.vendor.instance.toBytes(hexstr=sig))), s))
        return self.contract.functions.initiate(orders, a, components), self.tx_opts(opts)

    def exit(self, orders, a, s, opts=None):
        # normalize the full signatures to a list of vrs components
        components = tuple(map(lambda sig: v_r_s_to_dict(signature_to_v_r_s(self.vendor.instance.toBytes(hexstr=sig))), s))
        return self.contract.functions.exit(orders, a, components), self.tx_opts(opts)

    def cancel(self, order, s, opts=None):
        components = signature_to_v_r_s(self.vendor.instance.toBytes(hexstr=s))
        return self.contract.functions.cancel(order, v_r_s_to_dict(components)), self.tx_opts(opts)

    def split_underlying(self, u, m, a, opts=None):
        return self.contract.functions.splitUnderlying(u, m, a), self.tx_opts(opts)

    def combine_tokens(self, u, m, a, opts=None):
        return self.contract.functions.combineTokens(u, m, a), self.tx_opts(opts)
    
    def redeem_zc_token(self, u, m, a, opts=None):
        return self.contract.functions.redeemZcToken(u, m, a), self.tx_opts(opts)

    def redeem_vault_interest(self, u, m, opts=None):
        return self.contract.functions.redeemVaultInterest(u, m), self.tx_opts(opts)
