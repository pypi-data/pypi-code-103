import random
import threading

__all__ = ['random_identity', 'random_port', 'get_internal_ip', 'get_public_ip']


def random_identity() -> str:
    import random
    return f'{random.getrandbits(40):010x}'


def random_port(min_port: int = 49153, max_port: int = 65535) -> int:
    import multiprocessing
    from contextlib import closing
    import socket

    def _get_port(port=0):
        _p = None
        with multiprocessing.Lock():
            with threading.Lock():
                with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                    try:
                        s.bind(('', port))
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        return s.getsockname()[1]
                    except OSError:
                        pass

    all_ports = list(range(min_port, max_port + 1))
    random.shuffle(all_ports)
    for _port in all_ports:
        if _get_port(_port) is not None:
            return _port
    else:
        raise OSError(
            f'can not find an available port between [{min_port}, {max_port}].'
        )


def get_internal_ip() -> str:
    """
    Return the private IP address of the gateway for connecting from other machine in the same network.

    :return: Private IP address.
    """
    import socket

    ip = '127.0.0.1'
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
    except Exception:
        pass
    return ip


def get_public_ip(timeout: float = 3.0):
    """
    Return the public IP address of the gateway for connecting from other machine in the public network.

    :param timeout: the seconds to wait until return None.

    :return: Public IP address.

    .. warn::
        Set :param:`timeout` to a large number will block the Flow.

    """
    import urllib.request

    results = []

    def _get_ip(url):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=timeout) as fp:
                _ip = fp.read().decode()
                results.append(_ip)

        except Exception as ex:
            print(ex)
            pass  # intentionally ignored, public ip is not showed

    ip_server_list = [
        'https://api.ipify.org',
        'https://ident.me',
        'https://checkip.amazonaws.com/',
    ]

    threads = []

    for idx, ip in enumerate(ip_server_list):
        t = threading.Thread(target=_get_ip, args=(ip,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout)

    for r in results:
        if r:
            return r
