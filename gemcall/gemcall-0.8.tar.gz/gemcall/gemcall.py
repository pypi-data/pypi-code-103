# vim: tabstop=4 shiftwidth=4 expandtab

import socket
import urllib.parse
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat

class Response():
    def __init__(self, socket: socket.socket) -> "Response":
        self._socket = socket

        cert = self._socket.getpeercert(binary_form=True)
        certobj = x509.load_der_x509_certificate(cert, default_backend())
        pubkey = certobj.public_key()

        self.serverpubkey = pubkey.public_bytes(Encoding('PEM'), PublicFormat('X.509 subjectPublicKeyInfo with PKCS#1'))
        self._filehandle = self._socket.makefile(mode = "rb")

        # Two code digits, one space and a maximum of 1024 bytes of meta info.
        try:
            self.responsecode, self.meta = self._filehandle.readline(1027).split(maxsplit=1)
            self.responsecode = int(self.responsecode)
            self.meta = self.meta.strip().decode("UTF-8")
        except:
            self.discard()
            raise RuntimeError("Received malformed header from gemini server")

    def read(self, bufsize: int = 4096) -> "bytes":
        return self._filehandle.read(bufsize)

    def readline(self, bufsize: int = 4096) -> "bytes":
        return self._filehandle.readline(bufsize)

    def discard(self) -> None:
        self._filehandle.close()
        self._socket.close()

def request(url: str = "", clientcert: str = None, clientkey: str = None, timeout: int = 3) -> "Response":
    url = url if url.startswith("gemini://") else "gemini://" + url
    parsed = urllib.parse.urlparse(url)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    if (clientcert and clientkey):
        context.load_cert_chain(clientcert, clientkey)

    sock = socket.create_connection((parsed.hostname, parsed.port or 1965))
    ssock = context.wrap_socket(sock, server_hostname=parsed.hostname)
    ssock.sendall((url+"\r\n").encode("UTF-8"))

    return Response(ssock)

