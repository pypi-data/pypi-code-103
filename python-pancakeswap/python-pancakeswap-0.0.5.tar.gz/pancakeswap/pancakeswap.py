from loguru import logger
from pancakeswap import contract_addr, pancakeswap_abi, token_abi, load_symbol
from web3 import Web3, HTTPProvider
import time
import threading


class PancakeSwap:
    def __init__(self):
        self.symbol_whitelist = load_symbol("./config/symbol.config")
        self.swap_path_medium = ["BNB", "BUSD", "USDT"]
        self.web3 = Web3(HTTPProvider("https://bsc-dataseed1.binance.org:443"))
        self.pan_contract = self.web3.eth.contract(
            address=self.web3.toChecksumAddress(contract_addr), abi=pancakeswap_abi
        )
        self.threads = {}

    def start(self, func, params):
        t = threading.Thread(target=getattr(self, func), args=params)
        t.start()

    def stop():
        pass

    def polling_price(self, token, callback, seconds):
        best_path = self.get_best_path("BUSD", token, 10000)
        while True:
            price = 1 / self.get_price(best_path, 10000)
            callback(price)
            time.sleep(seconds)

    def sign_transaction(self, func_name: str, addr: str, private: str, **kwargs):
        try:
            func = getattr(self.pan_contract.functions, func_name)(**kwargs)

            params = {
                "from": addr,
                "value": self.web3.toWei(0, "ether"),
                "gasPrice": self.web3.toWei(5, "gwei"),
                "gas": 210000,
                "nonce": self.web3.eth.getTransactionCount(self.to_checksum_addr(addr)),
            }
            tx = func.buildTransaction(params)
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=private)
            tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
            return self.web3.toHex(tx_hash)

        except Exception as e:
            logger.error(f"{func_name} failed: {e}")

    def call(self, func_name: str, **kwargs):
        try:
            tx = getattr(self.pan_contract.functions, func_name)(**kwargs).call()
            return tx
        except Exception as e:
            logger.error(f"Call {func_name} failed: {e}")

    def to_checksum_addr(self, addr):
        return self.web3.toChecksumAddress(addr)

    def swap(self, from_token, to_token, wallet, private_key, amount, limit_price=None, slippery=1):
        from_token_addr = self.to_checksum_addr(self.symbol_whitelist[from_token])
        to_token_addr = self.to_checksum_addr(self.symbol_whitelist[to_token])

        owner = self.to_checksum_addr(wallet)
        spender = self.to_checksum_addr(contract_addr)
        contract = self.web3.eth.contract(from_token_addr, abi=token_abi)
        balance = self.balance_of(from_token, wallet)

        if not self.is_token_approved(from_token, wallet):
            approve = contract.functions.approve(spender, balance).buildTransaction(
                {
                    "from": owner,
                    "gasPrice": self.web3.toWei("5", "gwei"),
                    "nonce": self.web3.eth.get_transaction_count(owner),
                }
            )
            signed_tnx = self.web3.eth.account.sign_transaction(approve, private_key=private_key)
            tx_token = self.web3.eth.send_raw_transaction(signed_tnx.rawTransaction)
            logger.info(f"{from_token} approval txn: {self.web3.toHex(tx_token)}")
            self.wait_for_transaction_done(tx_token)

        logger.info(f"{wallet} Swap {amount} {from_token} to {to_token}!")

        best_path = self.get_best_path(from_token, to_token, amount)
        if len(best_path) == 0:
            return None

        if limit_price is None:
            out_min_amount = 0
        else:
            best_price = self.get_price(best_path, amount)
            if best_price < limit_price:
                logger.warning(f"Best price: {best_price}, Limit Price {limit_price} cancel order!")
                return None
            out_min_amount = int(self.web3.toWei(amount / limit_price, "ether") * 0.9)

        txn = self.sign_transaction(
            "swapExactTokensForTokens",
            wallet,
            private_key,
            amountIn=self.web3.toWei(amount, "ether"),
            amountOutMin=out_min_amount,
            path=best_path,
            to=owner,
            deadline=(int(time.time() + 1000000)),
        )

        logger.info(f"Swap txn: {txn}")
        return txn

    def is_token_approved(self, token, owner):
        token_addr = self.to_checksum_addr(self.symbol_whitelist[token])
        contract = self.web3.eth.contract(token_addr, abi=token_abi)
        owner = self.to_checksum_addr(owner)
        spender = self.to_checksum_addr(contract_addr)
        return contract.functions.allowance(owner, spender).call() != 0

    def get_price(self, path, amount):
        try:
            price = self.call("getAmountsOut", amountIn=self.web3.toWei(amount, "ether"), path=path)
            return price[-1] / price[0]
        except:
            return None

    def get_best_path(self, from_token, to_token, amount):
        best_path = []
        from_addr = self.to_checksum_addr(self.symbol_whitelist[from_token])
        to_addr = self.to_checksum_addr(self.symbol_whitelist[to_token])

        max_price = self.get_price([from_addr, to_addr], amount)
        if max_price is not None:
            best_path = [from_addr, to_addr]

        for medium in self.swap_path_medium:
            medium_addr = self.to_checksum_addr(self.symbol_whitelist[medium])
            path = [from_addr, medium_addr, to_addr]
            price = self.get_price(path, amount)

            if max_price is None and price is not None:
                max_price = price
                best_path = path
            elif price is not None and price > max_price:
                max_price = price
                best_path = path
        return best_path

    def balance_of(self, token: str, addr):
        token_addr = self.to_checksum_addr(self.symbol_whitelist[token])
        contract = self.web3.eth.contract(token_addr, abi=token_abi)
        decimals = 10 ** contract.functions.decimals().call()
        return self.web3.fromWei(contract.functions.balanceOf(addr).call(), "ether")

    def add_liquidity(self):
        pass

    def remove_liquidity(self):
        pass

    def getGasFee(txn):
        gasUsed = self.web3.eth.getTransactionReceipt(txn).gasUsed
        gas_fee = self.web3.fromWei(w3.eth.gas_price, "ether") * gasUsed
        return gas_fee

    def wait_for_transaction_done(self, txn):
        fee = None
        while fee is None:
            try:
                time.sleep(2)
                fee = self.web3.eth.getTransactionReceipt(txn).gasUsed
            except:
                pass
        return fee
