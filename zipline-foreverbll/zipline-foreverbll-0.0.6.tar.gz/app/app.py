import logging
import os
import threading

from foreverbull_core.models.backtest import Period, Result, Session
from foreverbull_core.socket.exceptions import SocketClosed, SocketTimeout
from foreverbull_core.socket.router import MessageRouter

from app.backtest.backtest import Backtest
from app.backtest.broker import Broker


class ApplicationError(Exception):
    pass


class Application(threading.Thread):
    def __init__(self, broker: Broker):
        self.logger = logging.getLogger(__name__)
        self.broker: Broker = broker
        self.backtests = {}
        self.id = os.environ.get("SERVICE_ID", None)
        self.running = False
        self.online = False
        self._router = MessageRouter()
        self._router.add_route(self._new_backtest, "new_backtest", Session)
        self._router.add_route(self._backtest_status, "backtest_status", Session)
        self._router.add_route(self._abort_backtest, "abort_backtest", Session)
        self._router.add_route(self._remove_backtest, "remove_backtest", Session)
        self._router.add_route(self._backtest_result, "backtest_result", Session)
        threading.Thread.__init__(self)

    def _backtest_result(self, session: Session) -> dict:
        try:
            b = self.backtests[session.id]
        except KeyError:
            raise ApplicationError("backtest not found")
        result = Result()
        for period in b.result:
            period_result = Period(**period)
            result.periods.append(period_result)
        return result.dict()

    def _new_backtest(self, session: Session) -> dict:
        if session.id in self.backtests:
            raise ApplicationError("remove backtest before creating new one")
        b = Backtest()
        b.start()
        self.backtests[session.id] = b
        return b.info()

    def _backtest_status(self, session: Session) -> dict:
        try:
            b = self.backtests[session.id]
        except KeyError:
            raise ApplicationError("backtest not found")
        return b.status()

    def _abort_backtest(self, session: Session) -> None:
        try:
            b = self.backtests[session.id]
        except KeyError:
            raise ApplicationError("backtest not found")
        b.stop()
        b.join()

    def _remove_backtest(self, session: Session) -> None:
        try:
            b = self.backtests[session.id]
        except KeyError:
            raise ApplicationError("backtest not found")
        if b.is_alive():
            self._abort_backtest(session)
        self.backtests.pop(session.id)

    def run(self) -> None:
        self.running = True
        while True:
            try:
                message = self.broker.socket.recv()
                rsp = self._router(message)
                self.broker.socket.send(rsp)
            except SocketTimeout:
                pass
            except SocketClosed:
                return
            except Exception as e:
                self.logger.warning(f"Unknown Exception when running: {repr(e)}")

    def stop(self) -> None:
        self.broker.socket.close()
        for backtest in self.backtests.values():
            backtest.stop()
            backtest.join()
