import waitress
import socket
import time
import typing
import logging

logger = logging.getLogger(__name__)


def serve_waitress(
    app: typing.Callable, global_conf: dict, **kw: typing.Any
) -> int:
    sockets: list = []
    if "prebound" in global_conf:
        filenos: str = global_conf["prebound"].split()
        for fileno in filenos:
            sock = socket.fromfd(int(fileno), socket.AF_INET, socket.SOCK_STREAM)
            sockets.append(sock)
        kw.update(sockets=sockets)
    try:
        waitress.serve(app, **kw)
    finally:
        for sock in sockets:
            sock.close()
    return 0


def server_factory(global_conf: dict, **kws: str) -> typing.Callable:
    if "fast-listen" in kws:
        filenos: list[str] = []
        for host_port in kws["fast-listen"].split():
            host, port = host_port.split(":")
            prebound = waitress.wasyncore.dispatcher()
            prebound.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            prebound.set_reuse_addr()
            prebound.bind((host, int(port)))
            prebound.listen(5)
            while not prebound.readable():
                time.sleep(0.5)
            fileno = prebound.socket.fileno()  # type: ignore
            filenos.append(str(fileno))
        global_conf.update(prebound=" ".join(filenos))
        del kws["fast-listen"]
        logger.info("waitress fast listen initialized.")
    del kws["paste.server_factory"]

    def serve(app: typing.Callable):
        return serve_waitress(app, global_conf, **kws)

    return serve
