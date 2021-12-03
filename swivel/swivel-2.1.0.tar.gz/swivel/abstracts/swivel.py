from abc import abstractmethod
from swivel.abstracts import Deployed

class Swivel(Deployed):
    @abstractmethod
    def name(self, opts=None):
        """The stored name constant for this contract

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def version(self, opts=None):
        """The stored version constant for this contract

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def hold(self, opts=None):
        """The stored hold constant for this contract

        Description:
            TODO

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def min_feenominator(self, opts=None):
        """The stored constant representing the minimum value for any fee denominator

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def domain(self, opts=None):
        """The stored EIP712 domain hash for this contract

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def market_place(self, opts=None):
        """The stored address of a market place contract associated with this contract

        Returns:
            web3 callable, opts
        """

        pass

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
    def feenominators(self, i, opts=None):
        """The stored fee constants for this contract

        Parameters:
            i (int) Index of the fenominator array to return

        Returns:
            web3 callable, opts
        """

        pass

    @abstractmethod
    def initiate(self, orders, a, s, opts=None):
        """Allows a user to initiate a position

        Parameters:
            orders (tuple) Offline swivel orders
            a (list) Order volume (principal) amounts relative to orders list
            s (tuple) Valid ECDSA signatures for each order
            opts (dict) Optional tx opts

        Returns:
            web3 transactable, opts
        """

        pass

    @abstractmethod
    def exit(self, orders, a, s, opts=None):
        """Allows a user to exit (sell) a currently held position to the marketplace

        Parameters:
            orders (tuple) Offline swivel orders
            a (list) Order volume (principal) amounts relative to orders list
            s (tuple) Valid ECDSA signatures for each order
            opts (dict) Optional tx opts

        Returns:
            web3 transactable, opts
        """

        pass

    @abstractmethod
    def cancel(self, order, s, opts=None):
        """Allows the cancellation of an order, preventing it from being filled further

        Parameters:
            order (dict) An offline swivel order
            s (string) Valid ECDSA signature for the order
            opts (dict) Optional tx opts

        Returns:
            web3 transactable, opts
        """

        pass
        
    @abstractmethod
    def split_underlying(self, u, m, a, opts=None):
        """Allows users to deposit underlying and in the process split it into/mint zcTokens and vault notional

        Parameters:
            u (string) Address of the underlying token
            m (int) Maturity timestamp of the market
            a (int) Amount of underlying being deposited
            opts (dict) Optional tx opts

        Returns:
            web3 transactable, opts
        """

        pass

    @abstractmethod
    def combine_tokens(self, u, m, a, opts=None):
        """Allows users to deposit/burn 1:1 amounts of both zcTokens and vault notional, in the process 'combining' the two and redeeming underlying

        Parameters:
            u (string) Address of the underlying token
            m (int) Maturity timestamp of the market
            a (int) Amount of zctokens being redeemed
            opts (dict) Optional tx opts

        Returns:
            web3 transactable, opts
        """

        pass

    @abstractmethod
    def redeem_zc_token(self, u, m, a, opts=None):
        """Allows zctoken holders to redeem their tokens for underlying tokens after maturity has been reached

        Parameters:
            u (string) Address of the underlying token
            m (int) Maturity timestamp of the market
            a (int) Amount of zctokens being redeemed
            opts (dict) Optional tx opts

        Returns:
            web3 transactable, opts
        """

        pass

    @abstractmethod
    def redeem_vault_interest(self, u, m, opts=None):
        """Allows vault owners to redeem any currently accrued interest

        Parameters:
            u (string) Address of the underlying token
            m (int) Maturity timestamp of the market
            opts (dict) Optional tx opts

        Returns:
            web3 transactable, opts
        """

        pass
