from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from pdx import Session
from pdx import Console
import os
import hashlib


# Class for encrypting and decrypting string values using RSA keys
class Encryptor:
    rsaKeyPath = None

    def encrypt(self, content):
        encrypted_value = None
        try:
            # Use RSA key to encrypt the data
            if self.rsaKeyPath and os.path.exists(self.rsaKeyPath):
                with open(self.rsaKeyPath, 'rb') as ff:
                    key = RSA.importKey(ff.read())
                    cipher = PKCS1_OAEP.new(key)
                    encrypted_value = cipher.encrypt(str.encode(content))
            else:
                Console.get().put_error("Unable to locate RSA key.")

        except Exception as ee:
            Console.get().put_error("Unable to encrypt value.")

        # Overwrite the content variable and delete it
        content = '                '
        del content

        return encrypted_value

    def decrypt(self, encrypted_bytes):
        decrypted_value = None
        try:
            # Use RSA key to decrypt the data
            if self.rsaKeyPath and os.path.exists(self.rsaKeyPath):
                with open(self.rsaKeyPath, 'rb') as ff:
                    key = RSA.importKey(ff.read())
                    cipher = PKCS1_OAEP.new(key)
                    decrypted_value = cipher.decrypt(encrypted_bytes).decode('utf-8')
                    del key
                    del cipher
            else:
                Console.get().put_error("Unable to locate RSA key.")

        except Exception as ee:
            Console.get().put_error("Unable to decrypt value.")

        return decrypted_value

    def encrypt_to_file(self, content, file_path):
        """Encrypt the given data and save it in a specified (binary) file"""
        # Encrypt the content
        encrypted_bytes = self.encrypt(content)

        # Overwrite the content variable and delete it
        content = '                '
        del content

        try:
            # Write encrypted data to file
            if encrypted_bytes:
                with open(file_path, 'wb') as ff:
                    ff.write(encrypted_bytes)
                del encrypted_bytes
        except Exception as ee:
            Console.get().put_error("Unable to write encrypted value to file.")

    def decrypt_from_file(self, file_path):
        """Decrypt the data in a specified (binary) file"""
        try:
            # Read encrypted data from file
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as ff:
                    return self.decrypt(ff.read())
        except Exception as ee:
            Console.get().put_error("Unable to read encrypted value from file.")

    def locate_rsa_path(self):
        # the standard location of RSA keys
        default_path = os.path.join(Session.user_home, '.ssh', 'id_rsa')
        # Allow user to have a separate key just for pdx-lib
        override_path = os.path.join(Session.user_home, '.pdx-lib', '.ssh', 'id_rsa')

        # Determine which key to use
        if os.path.exists(override_path):
            self.rsaKeyPath = override_path
        elif os.path.exists(default_path):
            self.rsaKeyPath = default_path
        else:
            Console.get().put_error("Unable to locate RSA key.")

        # Cleanup
        del default_path
        del override_path

    # Initialize an Encryptor object
    def __init__(self, given_rsa_key_path=None):
        """Create an Encryptor object"""
        if given_rsa_key_path:
            self.rsaKeyPath = given_rsa_key_path
        else:
            self.locate_rsa_path()


# Not encryption, but somewhat related.  Get a simple hash of a string
def getHash(source):
    hl = hashlib.new('ripemd160')
    hl.update(str.encode(source))
    return hl.hexdigest()
