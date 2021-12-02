import os
import base64
import hashlib
from jsbn import RSAKey
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptDecrypt:
    @staticmethod
    def enc_sha1(value:str):
        return hashlib.sha1(value.encode()).hexdigest()

    @staticmethod
    def enc_sha256(value:str):
        return hashlib.sha256(value.encode()).hexdigest()

    @staticmethod
    def rsa_enc(key,text,e="10001"):
        rsa = RSAKey()
        rsa.setPublic(key,e)

        return rsa.encrypt(text)

class KeyGenerate:
    @classmethod
    def generate_key(cls):
        password_provided = EncryptDecrypt.enc_sha1(os.getenv('ENCRYPT_KEY') if os.getenv('ENCRYPT_KEY') is not None else os.environ.get('ENCRYPT_KEY',"cumsdtu_c8F-w0ppLGVmLVIPjDLDvw"))  # This is input in the form of a string
        password = password_provided.encode()  # Convert to type bytes
        salt = b'salt_'  # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))  # Can only use kdf once
        return key


class EncryptionTools(KeyGenerate):
    def __init__(self, data,encode=False):
        key = self.generate_key()
        self.fernet_instance = Fernet(key)
        self.data = data.encode() if encode else data  # Data is always in bytes format

    def encrypt(self):
        return self.fernet_instance.encrypt(self.data)


class DecryptionTools(KeyGenerate):
    def __init__(self, data, encode=False):
        key = self.generate_key()
        self.fernet_instance = Fernet(key)
        self.data = data.encode() if encode else data  # Data is always in bytes format

    def decrypt(self):
        return self.fernet_instance.decrypt(self.data)


if __name__=='__main__':
    e=EncryptionTools("Jan@2015#$",True)
    data=e.encrypt()
    print(data)
    d= DecryptionTools(data)
    msg = d.decrypt()
    print(msg)
