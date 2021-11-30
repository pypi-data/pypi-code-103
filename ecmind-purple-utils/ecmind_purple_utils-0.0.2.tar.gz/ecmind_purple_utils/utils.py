import datetime
from random import random
import base64
import json
import uuid

class Token():
    def __init__(self, issuer: str, username: str, timestamp: datetime.datetime, session_guid: str):
        self.issuer = issuer
        self.username = username
        self.session_guid = session_guid
        self.timestamp = timestamp

    def is_expired(self) -> bool:
        return datetime.datetime.now() > self.timestamp

class TokenHelper():
    def __init__(self, salt):
        if isinstance(salt, str):
            if salt.lower().endswith('.json'):
                with open(salt, 'r') as f:
                    self.salt = json.load(f)
            else:
                self.salt = json.loads(salt)
        elif isinstance(salt, list):
             self.salt = salt
        else:
            raise ValueError("Salt parameter must be a path, json string or list of ints.")

    def generate(self, username: str, issuer, session_guid: str = None, offset_in_min: int = 5) -> str:
        if session_guid == None:
            session_guid = uuid.uuid1().hex.replace("-", "")

        time = datetime.datetime.now() + datetime.timedelta(minutes=offset_in_min)
        timestamp = int(datetime.datetime.timestamp(time) * 1000)

        decrypted = f'{issuer}_!_{username}_!_{session_guid}:{timestamp}'

        decrypted_bytes = decrypted.encode("UTF-8")

        index = int((random() * (self.salt.__len__() + 1.0)) %
                    self.salt.__len__())
        index_str = "{:04X}".format(index)

        current_index = index
        encrypted = ""
        for b in decrypted_bytes:
            res = b ^ self.salt[current_index % self.salt.__len__()]
            encrypted = encrypted + ("{:02X}".format(res))
            current_index = current_index + 1

        checksum = self._calc_checksum(bytearray(encrypted, "UTF-8"), index)
        checksum_str = "{:04X}".format(checksum)

        middle = int(encrypted.__len__() / 2)

        content = "_" + encrypted[:middle] + \
            index_str + encrypted[middle:] + checksum_str

        header = {
            "alg": "OSCrypt",
            "enc": "GUIDVARLEN"
        }

        header_str = base64.b64encode(json.dumps(
            header).encode("UTF-8")).decode("UTF-8")

        token = header_str + "..." + \
            base64.b64encode(content.encode("UTF-8")).decode("UTF-8") + "."

        return token

    def parse(self, token: str):
        # remove JWT prefix if exists
        if token.startswith('JWT '):
            token = token[4:]

        token_parts = token.split('.')

        if len(token_parts) != 5:
            raise ValueError("Wrong number of JWE parts")
        
        protected = self._base64url_decode(token_parts[0])
        ciphertext = self._base64url_decode(token_parts[3])
        
        header = json.loads(protected)

        alg = header['alg']

        # Check if token is a enaio/yuuvis token
        if alg != 'OSCrypt':
            raise ValueError(
                f'Unsupported algorithm {alg}. Only OSCRYPT allowed')

        if not ciphertext[0] == ord('_'):
            raise ValueError(f'ciphertext have to start with a unterline (_)')

        # remove _ prefix
        ciphertext = ciphertext[1:]

        # read checksum
        checksum_str = ciphertext[-4:]
        checksum = int(checksum_str, 16)

        # remove checksum
        ciphertext = ciphertext[:-4]

        # extract index from the center
        length = len(ciphertext)
        index_start_pos = int(length / 2 - 2)
        index_end_pos = int(index_start_pos + 4)

        index_hex = ciphertext[index_start_pos: index_end_pos]
        index = int(index_hex, 16)

        # remove hexindex from center
        salted = ciphertext[:index_start_pos] + ciphertext[index_end_pos:]

        checksum_calc = self._calc_checksum(salted, index)

        if checksum_calc != checksum:
            raise ValueError(
                f'checksum does not match {checksum} vs {checksum_calc}. Token is defect?')

        # decrypt
        decrypted_bytes = bytearray()
        for i in range(0, len(salted) - 1, 2):
            currentByteStr = salted[i:i+2]
            currentByte = int(currentByteStr, 16)
            decrypted_bytes.append(
                self.salt[index % len(self.salt)] ^ currentByte)
            index += 1

        # decode data as Unicode String
        decrypted = decrypted_bytes.decode("UTF-8")

        # split data and timestamp by :
        data_time = decrypted.split(":")

        # split data by '_!_'
        data = data_time[0].split("_!_")

        # issuer
        issuer = data[0]

        # username
        username = data[1]

        # (optional) session_guid
        session_guid = None
        if(data.__len__() > 2):
            session_guid = data[2]

        timestamp = datetime.datetime.fromtimestamp(int(data_time[1]) / 1000)

        return Token(issuer, username, timestamp, session_guid)

    def _base64url_decode(self, payload):
        size = len(payload) % 4
        if size == 2:
            payload += '=='
        elif size == 3:
            payload += '='
        elif size != 0:
            raise ValueError('Invalid base64 string')
        return base64.b64decode(payload.encode('utf-8'))

    def _calc_checksum(self, salted: bytearray, index: int):
        result = 0
        for b in salted:
            result += b
        return (result ^ index) & 0xFFFF
