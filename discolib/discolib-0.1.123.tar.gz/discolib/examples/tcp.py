from discolib.core import Disco
from discolib.io import DiscoIO, Validate
import sockets

class TcpIO(DiscoIO):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # now connect to the web server on port 80 - the normal http port
    sock.connect(("127.0.0.1", 31415))

    @validate.read
    def read(self, length: int) -> bytes:
        """Read bytes from the TCP server."""
        return self.sock.read(length)

    @validate.write
    def write(self, data: bytes) -> None:
        """Send bytes to the TCP server."""
        self.sock.write(data)

def main():
    disco = Disco(TcpIO())
    print(disco.get_attr_json(indent=2))
    print(dir(disco))

if __name__ == '__main__':
    main()
