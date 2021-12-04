import base64
import random

from Crypto.Cipher import AES

chars = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
charsLen = len(chars)


def rds(len0):
    ret = ""
    for i in range(len0):
        ret = ret + str(chars[random.randint(0, charsLen - 1)])
    return ret


def pad(text):
    count = len(text)
    fillsize = AES.block_size - (count % AES.block_size)
    ret = text + chr(fillsize) * fillsize
    return ret


def aes_encry(data, key, iv):
    key = key.replace(r"(^\s+)|(\s+$)", "")
    aes = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    ret = aes.encrypt(pad(data).encode("utf-8"))
    return base64.b64encode(ret).decode("utf-8")


def encrypt(data, key):
    iv = rds(16)
    data = rds(64) + data
    return aes_encry(data, key, iv)
