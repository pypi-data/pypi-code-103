from pydantic import BaseModel
import socket


def _get_free_tcp_port() -> int:
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    _, port = tcp.getsockname()
    tcp.close()
    return port


class WebPilotConfig(BaseModel):
    remote_port: int = _get_free_tcp_port()
    url: str = "about:blank"
    headless: bool = True
    sandboxed: bool = True
    chrome_executable: str = 'chrome'
