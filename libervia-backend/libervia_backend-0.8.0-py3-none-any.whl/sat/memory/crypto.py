#!/usr/bin/env python3

# SAT: a jabber client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from os import urandom
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


crypto_backend = default_backend()


class BlockCipher:

    BLOCK_SIZE = 16
    MAX_KEY_SIZE = 32
    IV_SIZE = BLOCK_SIZE  # initialization vector size, 16 bits

    @staticmethod
    def encrypt(key, text, leave_empty=True):
        """Encrypt a message.

        Based on http://stackoverflow.com/a/12525165

        @param key (unicode): the encryption key
        @param text (unicode): the text to encrypt
        @param leave_empty (bool): if True, empty text will be returned "as is"
        @return (D(str)): base-64 encoded encrypted message
        """
        if leave_empty and text == "":
            return ""
        iv = BlockCipher.getRandomKey()
        key = key.encode()
        key = (
            key[: BlockCipher.MAX_KEY_SIZE]
            if len(key) >= BlockCipher.MAX_KEY_SIZE
            else BlockCipher.pad(key)
        )

        cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend=crypto_backend)
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(BlockCipher.pad(text.encode())) + encryptor.finalize()
        return b64encode(iv + encrypted).decode()

    @staticmethod
    def decrypt(key, ciphertext, leave_empty=True):
        """Decrypt a message.

        Based on http://stackoverflow.com/a/12525165

        @param key (unicode): the decryption key
        @param ciphertext (base-64 encoded str): the text to decrypt
        @param leave_empty (bool): if True, empty ciphertext will be returned "as is"
        @return: Deferred: str or None if the password could not be decrypted
        """
        if leave_empty and ciphertext == "":
            return ""
        ciphertext = b64decode(ciphertext)
        iv, ciphertext = (
            ciphertext[: BlockCipher.IV_SIZE],
            ciphertext[BlockCipher.IV_SIZE :],
        )
        key = key.encode()
        key = (
            key[: BlockCipher.MAX_KEY_SIZE]
            if len(key) >= BlockCipher.MAX_KEY_SIZE
            else BlockCipher.pad(key)
        )

        cipher = Cipher(algorithms.AES(key), modes.CFB8(iv), backend=crypto_backend)
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(ciphertext) + decryptor.finalize()
        return BlockCipher.unpad(decrypted)

    @staticmethod
    def getRandomKey(size=None, base64=False):
        """Return a random key suitable for block cipher encryption.

        Note: a good value for the key length is to make it as long as the block size.

        @param size: key length in bytes, positive or null (default: BlockCipher.IV_SIZE)
        @param base64: if True, encode the result to base-64
        @return: str (eventually base-64 encoded)
        """
        if size is None or size < 0:
            size = BlockCipher.IV_SIZE
        key = urandom(size)
        return b64encode(key) if base64 else key

    @staticmethod
    def pad(s):
        """Method from http://stackoverflow.com/a/12525165"""
        bs = BlockCipher.BLOCK_SIZE
        return s + (bs - len(s) % bs) * (chr(bs - len(s) % bs)).encode()

    @staticmethod
    def unpad(s):
        """Method from http://stackoverflow.com/a/12525165"""
        s = s.decode()
        return s[0 : -ord(s[-1])]


class PasswordHasher:

    SALT_LEN = 16  # 128 bits

    @staticmethod
    def hash(password, salt=None, leave_empty=True):
        """Hash a password.

        @param password (str): the password to hash
        @param salt (base-64 encoded str): if not None, use the given salt instead of a random value
        @param leave_empty (bool): if True, empty password will be returned "as is"
        @return: Deferred: base-64 encoded str
        """
        if leave_empty and password == "":
            return ""
        salt = (
            b64decode(salt)[: PasswordHasher.SALT_LEN]
            if salt
            else urandom(PasswordHasher.SALT_LEN)
        )

        # we use PyCrypto's PBKDF2 arguments while porting to crytography, to stay
        # compatible with existing installations. But this is temporary and we need
        # to update them to more secure values.
        kdf = PBKDF2HMAC(
            # FIXME: SHA1() is not secure, it is used here for historical reasons
            #   and must be changed as soon as possible
            algorithm=hashes.SHA1(),
            length=16,
            salt=salt,
            iterations=1000,
            backend=crypto_backend
        )
        key = kdf.derive(password.encode())
        return b64encode(salt + key).decode()

    @staticmethod
    def verify(attempt, pwd_hash):
        """Verify a password attempt.

        @param attempt (str): the attempt to check
        @param pwd_hash (str): the hash of the password
        @return: Deferred: boolean
        """
        assert isinstance(attempt, str)
        assert isinstance(pwd_hash, str)
        leave_empty = pwd_hash == ""
        attempt_hash = PasswordHasher.hash(attempt, pwd_hash, leave_empty)
        assert isinstance(attempt_hash, str)
        return attempt_hash == pwd_hash
