
from seti_python.class_read import ResponseReadCash, ResponseReadCashOut, ResponseReadPayment, ResponseReadTransactions, ResponseReadWallet, ResponseReadWalletsTransactions
from seti_python.class_users import ResponseCreateUser, ResponseValidateUsersExist
from seti_python.wallet_class import ResponseCreateWallet
from seti_python.class_tools import BasicResponse, CompleteBasicaResponse, ResponseCreateDispersions, ResponseCreateTransaction
from seti_python.payment_class import ResponseCreatePayment
from typing import List
import execjs
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from base64 import b64decode, b64encode
import requests
import re


class MyException(Exception):
    pass


SETI_PRODUCTION = "https://api.seti.dev/v1/"
SETI_DEVELOP = "https://api-ve74dbrnra-uc.a.run.app/"


class Seti():

    def __init__(self, private_key: str, api_key: str, public_key='', seti_path=SETI_DEVELOP) -> (None):
        self.private_key = private_key
        self.api_key = api_key
        self.public_key_loc = public_key
        self.seti_path = seti_path

    def verify_sign(self, signature: str, data: dict):
        '''
        Verifies with a public key from whom the data came that it was indeed 
        signed by their private key
        param: public_key_loc Path to public key
        param: signature String signature to be verified
        return: Boolean. True if the signature is valid; False otherwise. 
        '''
        if self.public_key_loc == '':
            raise MyException({'msg': 'Provide public key path', 'code': 1})
        buffered_data = execjs.eval(
            "Buffer.from(JSON.stringify({}))".format(data))
        bytesData = bytearray(buffered_data['data'])
        pub_key = open(self.public_key_loc, "r").read()
        rsakey = RSA.importKey(pub_key)
        signer = PKCS1_v1_5.new(rsakey)
        digest = SHA256.new()
        digest.update(bytesData)
        if signer.verify(digest, b64decode(signature)):
            return True
        return False

    def sign_data(self, data: dict):
        '''
        Generate a sign from data with the private key and api_key
        param: private_key Path to private  key
        param: passphrase  api key
        return: Sign data provide
        '''
        buffered_data = execjs.eval(
            "Buffer.from(JSON.stringify({}))".format(data))
        bytesData = bytearray(buffered_data['data'])
        rsakey = RSA.importKey(self.private_key)
        hash = SHA256.new(bytesData)
        cipher_rsa = PKCS1_v1_5.new(rsakey)
        return b64encode(cipher_rsa.sign(hash)).decode("utf-8")

    def send_request(self, data: dict, sign_data: str, path: str):
        try:
            url = self.seti_path+path
            r = requests.post(url=url, json=data, headers={
                "authorization": self.api_key,
                "sign": sign_data
            }, timeout=10)
            return r.json()
        except Exception as e:
            return {'msg': str(e), 'code': 5}

    def validate_currency(self, currency: str):
        if not currency in ["COP", "USD", "EUR"]:
            raise MyException({'msg': 'Invalid Currency', 'code': 2})

    def validate_value(self, value: int):
        if value <= 0:
            raise MyException({'msg': 'Invalid value', 'code': 3})

    def validate_email(self, email: str):
        regx = r"[^@]+@[^@]+\.[^@]+"
        valid = re.search(regx, email)
        if not valid:
            raise MyException({'msg': 'Invalid email format', 'code': 4})

    def validate_send_method(self, send_method):
        if not send_method in ["SMS", "WHATSAPP"]:
            raise MyException({'msg': 'Invalid Currency', 'code': 2})

    def validate_payment_method(self, methods: List):
        if methods.__len__() == 0:
            return
        if not methods in ["NEQUI", "PSE", "CARD"]:
            raise MyException({'msg': 'Invalid Payment Method', 'code': 4})

    # Payments
    def create_payment(self, value: int, description: str, currency: str, reference: str, redirect_url: str, email: str, custom_methods: List[str]) -> (ResponseCreatePayment):
        self.is_error = False
        self.validate_currency(currency)
        self.validate_value(value)
        self.validate_payment_method(custom_methods)
        data_create_payment = {
            "value": value,
            "description": description,
            "currency": currency,
            "reference": reference,
            "redirectUrl": redirect_url,
            "email": email,
            "customMethods": custom_methods,
        }
        CREATE_PAYMENT_URL = "create-payment"
        encode_data = self.sign_data(data_create_payment)
        return ResponseCreatePayment(self.send_request(data_create_payment, encode_data, CREATE_PAYMENT_URL))

    # Wallets
    def create_wallet(self, email: str, iso_code: str, send_method: str):
        self.is_error = False
        self.validate_email(email)
        self.validate_currency(iso_code)
        self.validate_send_method(send_method)
        data_create_wallet = {
            "email": email,
            "isoCode": iso_code,
            "sendMethod": send_method,
        }
        CREATE_WALLET_URL = "create-wallet"
        encode_data = self.sign_data(data_create_wallet)
        return ResponseCreateWallet(self.send_request(data_create_wallet, encode_data, CREATE_WALLET_URL))

    def validate_wallet(self, code: str, secret: str):
        data_validate_wallet = {
            "code": code,
            "secret": secret,
        }
        VALIDATE_WALLET_URL = "validate-wallet"
        encode_data = self.sign_data(data_validate_wallet)
        return CompleteBasicaResponse(self.send_request(data_validate_wallet, encode_data, VALIDATE_WALLET_URL))

    def read_wallet_data(self, secret: str):
        self.is_error = False
        data_read_wallet = {
            "secret": secret,
        }
        READ_WALLET_URL = "read-wallet"
        encode_data = self.sign_data(data_read_wallet)
        return ResponseReadWallet(self.send_request(data_read_wallet, encode_data, READ_WALLET_URL))

    def read_wallet_transactions(self, secret: str):
        self.is_error = False
        data_read_wallet_transactions = {
            "secret": secret,
        }
        READ_WALLET_TRANSACTIONS_URL = "read-wallet-transactions"
        encode_data = self.sign_data(data_read_wallet_transactions)
        return ResponseReadWalletsTransactions(self.send_request(data_read_wallet_transactions, encode_data, READ_WALLET_TRANSACTIONS_URL))

    def send_money_between_wallets(self, from_secret: str, to_secret: str, value: int):
        self.is_error = False
        self.validate_value(value)
        data_send_money = {
            "fromSecret": from_secret,
            "toSecret": to_secret,
            "value": value
        }
        SEND_MONEY_WALLETS_URL = "send-money-between-wallets"
        encode_data = self.sign_data(data_send_money)
        return ResponseCreateTransaction(self.send_request(data_send_money, encode_data, SEND_MONEY_WALLETS_URL))

    def retention_money(self, from_secret: str, value: int):
        self.is_error = False
        data_retention_money = {
            "fromSecret": from_secret,
            "value": value
        }
        RETENTION_MONEY_URL = "retention-money"
        encode_data = self.sign_data(data_retention_money)
        return ResponseCreateTransaction(self.send_request(data_retention_money, encode_data, RETENTION_MONEY_URL))

    # Reversal

    def reversal_payment(self, payment_id: str):
        data_send_money = {
            "paymentId": payment_id
        }
        REVERSAL_PAYMENT_URL = "reversal-payment"
        encode_data = self.sign_data(data_send_money)
        return ResponseCreateTransaction(self.send_request(data_send_money, encode_data, REVERSAL_PAYMENT_URL))

    # Recharger

    def create_recharger(self, value: int,  secret: str):
        self.is_error = False
        self.validate_value(value)
        data_create_recharger = {
            "value": value,
            "secret": secret
        }
        CREATE_RECHARGER_URL = "create-recharger"
        encode_data = self.sign_data(data_create_recharger)
        return ResponseCreatePayment(self.send_request(data_create_recharger, encode_data, CREATE_RECHARGER_URL))

    # Dispersion

    def create_dispersion(self, value: int, description: str, currency: str, auth_email: str):
        self.is_error = False
        self.validate_value(value)
        data_create_dispersion = {
            "businessEmail": auth_email,
            "value": value,
            "description": description,
            "currency": currency
        }
        CREATE_DISPERSION_URL = "dispersion-money"
        encode_data = self.sign_data(data_create_dispersion)
        return ResponseCreateDispersions(self.send_request(data_create_dispersion, encode_data, CREATE_DISPERSION_URL))

    def create_dispersion_associated(self, value: int, to_secret: str):
        self.is_error = False
        self.validate_value(value)
        data_create_dispersion = {
            "toSecret": to_secret,
            "value": value,
        }
        CREATE_DISPERSION_URL = "dispersion-money-associated"
        encode_data = self.sign_data(data_create_dispersion)
        return ResponseCreateTransaction(self.send_request(data_create_dispersion, encode_data, CREATE_DISPERSION_URL))

    # Read
    def read_payment(self, payment_id: str):
        self.is_error = False
        data_read_payment = {
            "paymentId": payment_id
        }
        READ_PAYMENT_URL = "read-payment"
        encode_data = self.sign_data(data_read_payment)
        return ResponseReadPayment(self.send_request(data_read_payment, encode_data, READ_PAYMENT_URL))

    def read_cash(self, currency: str):
        self.is_error = False
        self.validate_currency(currency)
        data_read_cash = {
            "currency": currency
        }
        READ_CASH_URL = "read-cash"
        encode_data = self.sign_data(data_read_cash)
        return ResponseReadCash(self.send_request(data_read_cash, encode_data, READ_CASH_URL))

    def read_total_cash_outs(self, currency: str):
        self.is_error = False
        self.validate_currency(currency)
        data_read_cash = {
            "currency": currency
        }
        READ_TOTAL_CASH_OUT_URL = "read-total-cashout"
        encode_data = self.sign_data(data_read_cash)
        return ResponseReadCashOut(self.send_request(data_read_cash, encode_data, READ_TOTAL_CASH_OUT_URL))

    def read_transactions(self):
        self.is_error = False
        data_read_cash = {}
        READ_TRANSACTIONS_URL = "read-transactions"
        encode_data = self.sign_data(data_read_cash)
        return ResponseReadTransactions(self.send_request(data_read_cash, encode_data, READ_TRANSACTIONS_URL))

    def create_user(self, email: str, first_name: str, phone: str, iso_code: str):
        self.is_error = False
        self.validate_email(email)
        data_read_cash = {"email": email,
                          "name": first_name,
                          "phone": phone,
                          "isoCode": iso_code}
        CREATE_USER_URL = "create-user"
        encode_data = self.sign_data(data_read_cash)
        return ResponseCreateUser(self.send_request(data_read_cash, encode_data, CREATE_USER_URL))

    def validate_exist_user(self, email: str):
        self.is_error = False
        self.validate_email(email)
        data_read_cash = {"email": email}
        CREATE_USER_URL = "validate-user"
        encode_data = self.sign_data(data_read_cash)
        return ResponseValidateUsersExist(self.send_request(data_read_cash, encode_data, CREATE_USER_URL))

    def create_associated_wallet(self, iso_code: str):
        self.is_error = False
        create_wallet = {"isoCode": iso_code}
        CREATE_ASSOCIATED_WALLET = "create-associated-wallet"
        encode_data = self.sign_data(create_wallet)
        return ResponseCreateWallet(self.send_request(create_wallet, encode_data, CREATE_ASSOCIATED_WALLET))
