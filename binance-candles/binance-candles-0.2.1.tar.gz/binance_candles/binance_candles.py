import datetime
from binance import ThreadedWebsocketManager
from collections import deque
from threading import Thread, Event, Condition, Lock


class Candle:
    def __init__(self, symbol):
        self.symbol = symbol
        self.price_open_dt = self.price_close_dt = None

    def update(self, price_dt, price):
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

    def copy(self):
        candle = Candle(self.symbol)
        candle.price_open_dt = self.price_open_dt
        candle.price_close_dt = self.price_close_dt
        candle.price_open = self.price_open
        candle.price_low = self.price_low
        candle.price_high = self.price_high
        candle.price_close = self.price_close
        return candle

    def __str__(self):
        return f"{str(self.price_open_dt)}-{str(self.price_close_dt)} {self.symbol} {self.price_open} {self.price_low} {self.price_high} {self.price_close}"


class CandlesGenerator(ThreadedWebsocketManager):
    def __init__(self, candles_handler, price_change_handler=None):
        super().__init__()
        self.active_candles = {}
        self.lock_active_candles = Lock()
        self.candles_handler = candles_handler
        self.stopped = Event()
        self.price_change_handler = price_change_handler

    def price_handler(self, msg):
        data = msg["data"]
        updated_symbols = []
        with self.lock_active_candles:
            for entry in data:
                price_dt = datetime.datetime.fromtimestamp(entry["E"] / 1000)
                symbol = entry["s"]
                updated_symbols.append(symbol)
                price = entry["i"]
                if symbol not in self.active_candles:
                    candle = Candle(symbol)
                    self.active_candles[symbol] = candle
                else:
                    candle = self.active_candles[symbol]
                candle.update(price_dt, price)
        if self.price_change_handler is not None:
            self.price_change_handler(updated_symbols)

    def get_active_candle(self, symbol):
        with self.lock_active_candles:
            if symbol in self.active_candles:
                return self.active_candles[symbol].copy()

    def collect_ready_candles(self):
        completed_candles = []
        with self.lock_active_candles:
            new_candles = {}
            for candle in self.active_candles.values():
                completed_candles.append(candle)
                new_candles[candle.symbol] = candle.generate_next()
            self.active_candles = new_candles
        if len(completed_candles) > 0:
            self.candles_handler(completed_candles)

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


if __name__ == "__main__":
    candles_generator = CandlesGenerator()
    candles_generator.start()
    for candle in candles_generator:
        print(candle)
