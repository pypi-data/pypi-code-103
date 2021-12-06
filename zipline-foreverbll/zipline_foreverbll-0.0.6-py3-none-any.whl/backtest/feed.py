import logging
import threading
import time

from foreverbull_core.models.finance import Asset, EndOfDay
from foreverbull_core.models.socket import Request, SocketConfig
from foreverbull_core.socket.exceptions import SocketClosed
from foreverbull_core.socket.nanomsg import NanomsgSocket
from zipline.api import get_datetime

from app.backtest.exceptions import EndOfDayError


class Feed:
    def __init__(self, configuration=None):
        self.logger = logging.getLogger(__name__)
        if configuration is None:
            configuration = SocketConfig(socket_type="publisher")
        self.configuration = configuration
        self.socket = NanomsgSocket(configuration)
        self.bardata = None
        self.day_completed = False
        self.timeouts = 10
        self.lock = threading.Event()
        self.lock.set()

    def info(self) -> None:
        return {"socket": self.configuration.dict()}

    def handle_data(self, context, data) -> None:
        if self.lock is None:
            return
        self.logger.debug("running day {}".format(str(get_datetime())))
        self.day_completed = False
        self.lock.clear()
        self.bardata = data
        for asset in context.assets:
            a = Asset(
                sid=asset.sid,
                symbol=asset.symbol,
                asset_name=asset.asset_name,
                exchange=asset.exchange,
                exchange_full=asset.exchange_full,
                country_code=asset.country_code,
            )
            eod = EndOfDay(
                asset=a,
                date=str(get_datetime()),
                price=data.current(asset, "price"),
                last_traded=str(data.current(asset, "last_traded")),
                open=data.current(asset, "open"),
                high=data.current(asset, "high"),
                low=data.current(asset, "low"),
                close=data.current(asset, "close"),
                volume=data.current(asset, "volume"),
            )
            message = Request(task="stock_data", data=eod.dict())
            try:
                self.socket.send(message.dump())
            except SocketClosed as exc:
                self.logger.error(exc, exc_info=True)
                return
        message = Request(task="day_completed")
        try:
            self.socket.send(message.dump())
        except SocketClosed as exc:
            self.logger.error(exc, exc_info=True)
            return
        self.wait_for_new_day()
        self.day_completed = True

    def wait_for_new_day(self) -> None:
        for _ in range(self.timeouts):
            try:
                if self.lock.wait(0.5):
                    break
            except AttributeError:
                return
        else:
            raise EndOfDayError("timeout when waiting for new day")

    def stop(self) -> None:
        if self.lock:
            self.lock.set()
        self.lock = None
        if self.socket is None:
            return
        message = Request(task="backtest_completed")
        try:
            self.socket.send(message.dump())
            time.sleep(0.5)
            self.socket.close()
            self.socket = None
        except SocketClosed as exc:
            self.logger.error(exc, exc_info=True)
