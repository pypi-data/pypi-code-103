from abc import ABC

class Deployed(ABC):
    def at(self, a, opts=None):
        """Get a reference to the vendor specific contract instance deployed at a given address

        Parameters:
            a (string) the address of the deployed smart contract
            o (dict) optional tx options
        """

        self.address = a
        # TODO throw if the contract is falsy?
        self.contract = self.vendor.contract(a, self.abi)
        # TODO do we want to keep this reference?
        self.opts = opts

    def tx_opts(self, o):
        """Sets default transaction options"""

        defaults = { 'from': self.vendor.account }

        if o is not None:
            # any user passed opts should overwrite defaults...
            defaults.update(o)

        return defaults
