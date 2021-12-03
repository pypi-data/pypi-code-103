from abc import abstractmethod
from swivel.abstracts import Deployed

class VaultTracker(Deployed):
    """Persists and curates Vault objects associated with users

    Note that a Vault is a Dict object in this form:

        { notional, redeemable, exchangerate }
    """

    @abstractmethod
    def admin(self, opts=None):
        """The stored admin address for this contract

        Note that this should always be the MarketPlace address

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def c_token_address(self, opts=None):
        """Adress of the compound token referenced by this vault tracker

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def swivel(self, opts=None):
        """Address of the associated Swivel contract deployment

        Returns:
            web3 callable, opts
        """

        pass
    
    @abstractmethod
    def maturity(self, opts=None):
        """An Epoch (in seconds) representing the time of maturity

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def maturity_rate(self, opts=None):
        """The maturity rate (TODO: better description)

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def vaults(self, o, opts=None):
        """Get a Vault for a given address

        Parameters:
            o (string) Address of the vault owner

        Returns:
            web3 callable, opts
        """

        pass
    
    @abstractmethod
    def balances_of(self, o, opts=None):
        """Get Vault balances for a given user

        Parameters:
            o (string) Address of the vault owner

        Returns:
            web3 callable, opts
        """
        pass
