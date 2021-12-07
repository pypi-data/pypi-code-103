# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional

# Pip
from web3 import Web3
from web3._utils.threads import Timeout
from web3.exceptions import TransactionNotFound
from eth_account.signers.local import LocalAccount
from web3.middleware import geth_poa_middleware
from web3.types import TxData, TxReceipt

from web3_erc20_predefined import *
from noraise import noraise

# -------------------------------------------------------------------------------------------------------------------------------- #



# --------------------------------------------------------- class: KWeb3 --------------------------------------------------------- #

class KWeb3(Web3):

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        endpoint_uri: str,
        account_private_key: Optional[str] = None,
        use_poa_middleware: bool = False
    ):
        super().__init__(Web3.HTTPProvider(endpoint_uri))
        self.account = self.account_from_key(account_private_key) if account_private_key else None

        if self.account:
            self.eth.default_account = self.account.address

        if use_poa_middleware:
            self.middleware_onion.inject(geth_poa_middleware, layer=0)


    # ---------------------------------------------------- Public methods ---------------------------------------------------- #

    def account_from_key(
        self,
        private_key: str
    ):
        return self.eth.account.from_key(private_key)


    # transactions

    @noraise(print_exc=False)
    def get_transaction(
        self,
        tx_hash: str
    ) -> Optional[TxData]:
        ''' None means, the Transaction is not found'''
        return self.eth.get_transaction(tx_hash)

    def get_transaction_index(
        self,
        tx_hash: str
    ) -> Optional[int]:
        ''' None means, the Transaction is not found'''
        t = self.get_transaction(tx_hash)

        return t.get('transactionIndex') if t else None

    def is_transaction_validated(
        self,
        tx_hash: str
    ) -> Optional[bool]:
        ''' None means, the Transaction is not found'''
        return self.get_transaction_index(tx_hash) is not None

    def wait_for_transaction_to_be_validated(
        self,
        tx_hash: str,
        timeout: float = 120,
        poll_latency: float = 0.1
    ) -> Optional[TxData]:
        with Timeout(timeout) as _timeout:
            while True:
                try:
                    txn_data = self.get_transaction(tx_hash)
                except TransactionNotFound:
                    txn_data = None

                if txn_data is not None and txn_data.get('transactionIndex') is not None:
                    break

                _timeout.sleep(poll_latency)

        return txn_data


    # transaction receipts

    @noraise(print_exc=False)
    def get_transaction_receipt(
        self,
        tx_hash: str
    ) -> Optional[TxReceipt]:
        return self.eth.get_transaction_receipt(tx_hash)

    def get_transaction_result(
        self,
        tx_hash: str
    ) -> Optional[bool]:
        t = self.get_transaction_receipt(tx_hash)

        if t.get('transactionIndex') is None:
            return None

        status = t.get('status')

        return bool(status) if status is not None else None

    def wait_for_transation_receipt(
        self,
        tx_hash: str,
        timeout_seconds: int = 120,
        poll_latency: float = 0.1
    ) -> Optional[TxReceipt]:
        return self.eth.wait_for_transation_receipt(
            transaction_hash=tx_hash,
            timeout=timeout_seconds,
            poll_latency=poll_latency
        )


    # erc20

    def erc20(
        self,
        address: str,
        account: Optional[LocalAccount] = None
    ) -> ERC20:
        return ERC20(
            eth=self.eth,
            address=address,
            account=account or self.account
        )


    # Predefined - BSC

    def wbnb(
        self,
        account: Optional[LocalAccount] = None
    ) -> Wbnb:
        return Wbnb(
            eth=self.eth,
            account=account or self.account
        )

    def busd(
        self,
        account: Optional[LocalAccount] = None
    ) -> Busd:
        return Busd(
            eth=self.eth,
            account=account or self.account
        )

    # Predefined - BSC Testnet

    def wbnb_testnet(
        self,
        account: Optional[LocalAccount] = None
    ) -> TestWbnb:
        return TestWbnb(
            eth=self.eth,
            account=account or self.account
        )

    # Predefined - Eth

    def dai(
        self,
        account: Optional[LocalAccount] = None
    ) -> Dai:
        return Dai(
            eth=self.eth,
            account=account or self.account
        )

    def usdc(
        self,
        account: Optional[LocalAccount] = None
    ) -> USDC:
        return USDC(
            eth=self.eth,
            account=account or self.account
        )

    def usdt(
        self,
        account: Optional[LocalAccount] = None
    ) -> USDT:
        return USDT(
            eth=self.eth,
            account=account or self.account
        )

    def weth(
        self,
        account: Optional[LocalAccount] = None
    ) -> Weth:
        return Weth(
            eth=self.eth,
            account=account or self.account
        )


# -------------------------------------------------------------------------------------------------------------------------------- #