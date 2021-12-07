# Standard lib imports
import socket

# Local imports
from qwilfish.base_runner import BaseRunner

class LinuxSocketRunner(BaseRunner):

    def __init__(self, interface="lo"):
        self.sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        self.sock.bind((interface, 0))

    def run(self, input):
        data = []
        for byte in range(0, len(input), 8):
            data.append(int(input[byte:byte+8], 2))

        frame = bytes(data)

        self.sock.send(frame)
