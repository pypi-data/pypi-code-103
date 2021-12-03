import logging
import datetime
from binance import ThreadedWebsocketManager
from collections import deque
from threading import Thread, Event, Condition, Lock


class Candle:
    def __init__(self, symbol):
        self.symbol = symbol
        self.price_open_dt = self.price_close_dt = None

    def update(self, price_dt, price):
        logging.debug(f"{self.symbol} {price}")
        self.price_close_dt = price_dt
        self.price_close = price

        if self.price_open_dt is None:
            self.price_open = self.price_low = self.price_high = price
            self.price_open_dt = price_dt

        if price < self.price_low:
            self.price_low = price
        if price > self.price_high:
            self.price_high = price

    def generate_next(self):
        candle = Candle(self.symbol)
        candle.price_open = (
            candle.price_low
        ) = candle.price_high = candle.price_close = self.price_close
        candle.price_open_dt = candle.price_close_dt = self.price_close_dt
        return candle

    def __str__(self):
        return f"{str(self.price_open_dt)}-{str(self.price_close_dt)} {self.symbol} {self.price_open} {self.price_low} {self.price_high} {self.price_close}"


class CandlesGenerator(ThreadedWebsocketManager):
    def __init__(self):
        super().__init__()
        self.active_candles = {}
        self.lock_active_candles = Lock()
        self.completed_candles = deque()
        self.completed_candles_cond = Condition()
        self.stopped = Event()

    def price_handler(self, msg):
        data = msg["data"]
        self.lock_active_candles.acquire()
        for entry in data:
            price_dt = datetime.datetime.fromtimestamp(entry["E"] / 1000)
            symbol = entry["s"]
            price = entry["i"]
            if symbol not in self.active_candles:
                candle = Candle(symbol)
                self.active_candles[symbol] = candle
            else:
                candle = self.active_candles[symbol]
            candle.update(price_dt, price)
        self.lock_active_candles.release()

    def collect_ready_candles(self):
        with self.lock_active_candles:
            new_candles = {}
            for candle in self.active_candles.values():
                self.completed_candles.append(candle)
                new_candles[candle.symbol] = candle.generate_next()
            self.active_candles = new_candles
        if len(self.completed_candles) > 0:
            with self.completed_candles_cond:
                self.completed_candles_cond.notify()

    def start(self):
        ThreadedWebsocketManager.start(self)
        self.start_all_mark_price_socket(self.price_handler)

        def loop():
            while not self.stopped.wait(60):
                self.collect_ready_candles()

        Thread(target=loop).start()

    def stop(self):
        ThreadedWebsocketManager.stop(self)
        self.stopped.set()

    def __iter__(self):
        while not self.stopped.is_set():
            with self.completed_candles_cond:
                if len(self.completed_candles) == 0:
                    self.completed_candles_cond.wait()
                yield self.completed_candles.popleft()


class BufferedCandlesGenerator(CandlesGenerator):
    def __init__(self, buffer_size):
        super().__init__()
        self.buffer_size = buffer_size
        self.buffer = {}

    def __iter__(self):
        for candle in super(BufferedCandlesGenerator, self).__iter__():
            if candle.symbol not in self.buffer:
                self.buffer[candle.symbol] = []
            self.buffer[candle.symbol].append(candle)
            print(
                f"Collected {len(self.buffer[candle.symbol])} candles for {candle.symbol}"
            )
            if len(self.buffer[candle.symbol]) >= self.buffer_size:
                candles = self.buffer[candle.symbol]
                self.buffer[candle.symbol] = []
                yield candles


if __name__ == "__main__":
    candles_generator = BufferedCandlesGenerator(2)
    candles_generator.start()
    for candles in candles_generator:
        for candle in candles:
            print(candle)
