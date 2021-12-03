from abc import abstractmethod
from swivel.abstracts import Deployed

class MarketPlace(Deployed):
    @abstractmethod
    def admin(self, opts=None):
        """The stored admin address for this contract

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def transfer_admin(self, a, opts=None):
        """Allows the current admin to transfer the title to another party

        Description:
            Note that this method is only callable by the admin

        Parameters:
            a (address) Address of the new admin

        Returns:
            web3 transactable, opts
        """

        pass

    @abstractmethod
    def swivel(self, opts=None):
        """The address of the associated Swivel contract deployment

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def set_swivel_address(self, a, opts=None):
        """Sets the address of the Swivel smart contract this market place is associated with

        Description:
            Note that this method is only callable by the admin once

        Parameters:
            a (address) The address of a deployed Swivel smart contract
            opts (dict) Optional transaction options

        Returns:
            web3 transactable, opts
        """

        pass

    @abstractmethod
    def pause(self, b, opts=None):
        """Allows the admin to pause / unpause market transactions

        Parameters:
            b Boolean which acts as a toggle, True to pause, False to unpause

        Returns:
            web3 transactable, opts
        """

        pass

    @abstractmethod
    def paused(self, opts=None):
        """A boolean which indicates a pause in all markets if truthy

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def c_token_address(self, u, m, opts=None):
        """Gets the compound token address associated with a given market

        Parameters:
            u (string) Underlying token address
            m (int) Maturity epoch
            opts (dict) optional call opts

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def create_market(self, m, c, n, s, opts=None):
        """Creates a new market

        Description:
            New instances of both ZcToken and VaultTracker are deployed, their addresses then being associated
            with the newly created market.

            Note that this method is only callable by the admin

        Parameters:
            m (int) Epoch in seconds, the maturity of the market
            c (string) Address of the Compound token associated with the market
            n (string) Name for the new ZcToken
            s (string) Name for the new ZcToken
            opts (dict) Optional transaction options

        Returns:
            web3 transactable, opts
        """

        pass

    @abstractmethod
    def markets(self, u, m, opts=None):
        """Gets the market associated with the given underlying and maturity arguments

        Description:
            The returned Market object is { cTokenAddr, ZcTokenAddr, vaultAddr }

        Parameters:
            u (string) Underlying token address
            m (int) Muturity epoch
            opts (dict) optional call opts

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def mature_market(self, u, m, opts=None):
        """Called after maturity, allowing all of the zcTokens to earn floating interest on Compound until funds are released

        Parameters:
            u (string) Underlying token address
            m (int) Maturity epoch
            opts (dict) optional call opts

        Returns:
            web3 transactable, opts
        """

        pass

    @abstractmethod
    def transfer_vault_notional(self, u, m, t, a, opts=None):
        """Transfer vault notional from sender to a given address

        Parameters:
            u (string) Underlying token address
            m (int) Muturity epoch
            t (string) Address of the amount owner
            a (int) Amount to transfer
            opts (dict) Optional transaction opts

        Returns:
            web3 transactable, opts
        """

        pass
