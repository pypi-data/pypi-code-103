
import socket
import struct
import os
import threading


class LogSocket:
    def __init__(self, port, address=None):
        self.sock = None
        self.address = address
        self.port = port

        self.reconnect()

    def reconnect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(2)

        if self.address is None:
            self.address = LogSocket.get_wsl_ip()

        if self.address is None:
            self.address = "127.0.0.1"

        try:
            self.sock.connect((self.address, self.port))
            process_id = os.getpid()
            buf = struct.pack('i', process_id)
            self.sock.send(buf)
        except:
            self.sock = None

    def log(self, text):
        if self.sock is None:
            return

        contents = '[' + str(threading.get_native_id()) + '] ' + text

        encoded_contents = contents.encode('utf-8')
        buf = struct.pack('i', len(encoded_contents))

        try:
            self.sock.send(buf)
            self.sock.send(encoded_contents)
        except:
            self.reconnect()

    def close(self):
        self.sock.close()

    @staticmethod
    def get_wsl_ip():
        with open('/etc/resolv.conf') as f:
            for line in f.readlines():
                item = line.split(' ')
                if item[0] == 'nameserver':
                    return item[1].strip()

        return None

