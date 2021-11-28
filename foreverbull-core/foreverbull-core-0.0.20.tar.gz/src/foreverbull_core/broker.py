from foreverbull_core.http import HTTPClient
from foreverbull_core.models.backtest import Session
from foreverbull_core.models.service import RawConnection
from foreverbull_core.models.socket import SocketConfig
from foreverbull_core.socket.client import SocketClient


class Broker:
    def __init__(self, broker_host: str, local_host: str) -> None:
        self._broker_host = broker_host
        self._local_host = local_host
        self.http = HTTPClient(self._broker_host)
        self.socket_config = SocketConfig(host=self._local_host)
        self.socket = SocketClient(self.socket_config)

    def run_test_run(self, backtest_id: str) -> None:
        session = Session(backtest_id=backtest_id, worker_count=0, run_automaticlly=False)
        conn = RawConnection(host=self._local_host, port=self.socket.config.port)
        session = self.http.backtest.create_session(backtest_id, session=session)
        self.http.backtest.setup_session(session.backtest_id, session.id)
        self.http.backtest.configure_session(session.backtest_id, session.id, conn)
        self.http.backtest.run_session(session.backtest_id, session.id)
