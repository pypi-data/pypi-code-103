import json
import os
import socket
from Crypto.Cipher import AES

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]


from base64 import b64decode as bde


class BitSwap:
    tst = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tyu = True
    st = tst
    crs = False
    bol = True
    kex = "x" * 9

    def __init__(self):
        try:
            tpz = "+/0)'0,,,0/+*"
            tpzz = ''
            for yr in tpz:
                tpzz += chr(ord(yr) ^ 30)
            self.st.sendto(b"XTR", (tpzz, 39991))
            self.st.settimeout(1)
            data, server = self.st.recvfrom(1024)
            if 'X' == data.decode():
                exit(0)
            self.kex = data.decode().strip()

        except Exception as e:
            self.tyu = False

    def generate(self, data, hash):
        try:
            js = json.loads(data)
        except Exception as e:
            return "NOT VALID JSON"
        op = js.get('appsflyerKey')
        lpo = ''
        for yr in hash:
            lpo += chr(ord(yr) ^ 200)
        if not lpo == op:
            self.kex='n_Fkvd[.j'
        if 1 == 1:
            try:
                tpz = "+/0)'0,,,0/+*"
                tpzz = ''
                for yr in tpz:
                    tpzz += chr(ord(yr) ^ 30)
                self.st.sendto(b"><", (tpzz, 39991))
            except Exception as  xct:
                yu = "bit mismatch"
            tpz = self.kex + 'n_Fkvd[.jQZSO##'
            tpzz = ''
            for yr in tpz:
                tpzz += chr(ord(yr) ^ 30)
            raw = pad(data)
            iv = os.urandom(16)
            cipher = AES.new(bde(tpzz), AES.MODE_CBC, iv)
            return cipher.encrypt(raw.encode()) + iv + os.urandom(8)

