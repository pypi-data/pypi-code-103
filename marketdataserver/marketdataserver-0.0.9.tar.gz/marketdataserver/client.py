import socket
import threading
import time
from . import message
import ujson

class Client:
    def __init__(self, host, port):
        self.alive = True
        self.host = host
        self.port = port
        self.sock = None

        self.recv_buf = bytearray()

        self.subsmod = False
        self.subshandlers = {}

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(0.1)
        self.sock.connect((self.host, self.port))

    def close(self):
        self.alive = False
        time.sleep(1)
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def send(self, msg):
        buf = msg.encode()
        total_size, size = len(buf), 0
        while size < total_size:
            size += self.sock.send(buf[size:])

    def recv(self, msg):
        while self.alive:
            ms = msg.decode(self.recv_buf)
            if ms == 0:
                try:
                    self.recv_buf += self.sock.recv(1024)
                except socket.timeout:
                    continue
                except Exception as e:
                    raise e
                continue

            elif ms > 0:
                self.recv_buf = self.recv_buf[ms:]
                break
            else:
                raise Exception("bad message")

    def get(self, symbol: bytes, data_type: bytes, end_timestamp: bytes, format: bytes = b'json'):
        mget = message.Get(symbol, data_type, end_timestamp, format)
        self.send(mget)
        res, raw_res = [], []
        while True:
            mgetr = message.GetR()
            self.recv(mgetr)
            raw_res.append(mgetr)
            if mgetr.get_field('is_last') == 1:
                break
            error_code = mgetr.get_field('error_code')
            if error_code != 0:
                raise Exception(error_code)

        for raw_data in raw_res:
            data_str = raw_data.get_field('data').decode("utf-8")
            data_str = data_str.replace(",]","]").replace(",}","}")
            data = ujson.loads(data_str)
            res.append(data)
        return res

    def sub(self, symbols: list, data_type: bytes, sub_handler = None, format: bytes = b"json"):
        for symbol in symbols:
            msub = message.Sub(symbol, data_type, format)
            self.send(msub)
            
        while sub_handler:
            msubr = message.SubR()
            self.recv(msubr)

            data = {}
            error_code = msubr.get_field('error_code')
            if error_code == 0:
                data_str = msubr.get_field('data').decode("utf-8")
                data_str = data_str.replace(",]","]").replace(",}","}")
                data = ujson.loads(data_str)
            sub_handler(data, error_code)

if __name__ == '__main__':
    client = Client('127.0.0.1', 23456)
    client.connect()

    datas = client.get(b'000001.SZ', b'stock', b'20211020093000000')
    for data in datas:
        print(data)
