import os
from web3 import Web3
from .signer import Signer

class W3:
    def __init__(self, p, a=None):
        """
        Parameters:
            p (Web3.Provider) Provider being used to connect
            a (address) An optional default account to use. Will default to .eth.accounts[0] if omitted
        """

        self.instance = Web3(p)

        # normalize .account from the various scenarios
        if a != None:
            self.account = a
        else:
            if bool(self.instance.eth.default_account):
                self.account = self.instance.eth.default_account
            else:
                self.account = self.instance.eth.accounts[0]

        self.signer = Signer()

    def contract(self, address, abi):
        """Get an instance of the vedor low-level contract object

        Parameters:
            address (address) The address of the deployed smart contract
            abi (string) ABI of the deployed smart contract

        Returns:
            the vendor specific contract object
        """
        
        return self.instance.eth.contract(address=address, abi=abi)

    def sign_order(self, o, i, a):
        """Sign an order, producing an EIP712 compliant signature

        Parameters:
            o (dict) Swivel Order object
            i (int) ChainId
            a (string) Address of the deployed verifying contract

        Returns:
            The signature hex
        """

        key = os.getenv('PRIVATE_KEY')
        return self.signer.sign_order(o, i, a, self.instance.toBytes(hexstr=key))

    def estimate_gas(self, a):
        """Return an estimate of gas to be used in a transaction, as well as the price of the gas
        
        Parameters:
            a (tuple) Length 2 tuple whose values are a web3 transactable object and a tx_opts dict.
            This is the common return of all Swivel.py H.O.C contract methods. 

        Returns:
            gas, gas_price
        """

        built = self.build_transaction(a)
        return built['gas'], built['gasPrice']

    def build_transaction(self, a):
        """Return a suitable transaction object for signing
        
        Description:
            As per our pattern a[1] is the tx_opts dict. Note that you should include, at least,
            'chainId' in that dict. Other optional properties are available, see
            https://web3py.readthedocs.io/en/latest/web3.eth.account.html#sign-a-transaction.
            * 'maxFeePerGas'
            * 'maxPriorityFeePerGas'
            * etc...
        """

        a[1]['nonce'] = self.instance.eth.get_transaction_count(a[1]['from'])
        return a[0].buildTransaction(a[1])

    def sign_transaction(self, t):
        """Called after a transaction has been built with `build_transaction`
        
        Parameters:
            t (dict) A built transaction object from build_transaction

        Returns:
            A signed transaction
        """

        key = os.getenv('PRIVATE_KEY')
        return self.instance.eth.account.sign_transaction(t, private_key=key)

    def send_raw_transaction(self, t):
        """Given a raw signed transaction, broadcast it
        
        Parameters:
            t (transaction) A web3 transaction which has been signed

        Returns:
            A transaction hash suitable for web3's ...wait_for_transaction_receipt method
        """

        return self.instance.eth.send_raw_transaction(t.rawTransaction)

    def send(self, a):
        """Convenience method which builds, signs and broadcasts a transaction"""

        return self.send_raw_transaction(self.sign_transaction(self.build_transaction(a)))
