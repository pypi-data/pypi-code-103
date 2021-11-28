from discolib.core import Disco
from discolib.io import DiscoIO, Validate
import socket

disco = None

class TcpIO(DiscoIO):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 31415))

    @Validate.read
    def read(self, length: int) -> bytes:
        """Read bytes from the TCP server."""
        return self.sock.recv(length)

    @Validate.write
    def write(self, data: bytes) -> None:
        """Send bytes to the TCP server."""
        self.sock.sendall(data)

def main():
    global disco
    disco = Disco(TcpIO())
    print(disco.get_attr_json(indent=2))
    print(dir(disco))

if __name__ == '__main__':
    main()
