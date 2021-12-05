import redis
import json
import requests
from typing import List
import wallex
from threading import Thread
import time


from .exceptions import *


class Cacher:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 1, decode_responses: bool = True,
                 expiry: int = 1, sleep: int = 1, base_url: str = 'https://wallex.ir/api/v2/'):

        try:
            self.redis_conn = redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)
        except redis.exceptions.RedisError as e:
            raise RedisError(f'Redis connection failed: {e} | host: {host} | port: {port} | db: {db}')
        self.expiry = expiry
        self.sleep = sleep

        self.wl = wallex.Wallex('')
        self.wl.base_url = base_url
        self.wl.verify = False if self.wl.base_url != 'https://wallex.ir/api/v2/' else None

    @staticmethod
    def gen_currencies() -> List:
        r = requests.get("https://wallex.ir/api/v2/markets")
        r_json = r.json()
        stats = r_json.get("result").get('symbols')

        _ = [x for x in stats.keys() if x.split('-')[1].lower() != 'btc']

        return _

    def cache_orderbook(self, pair: str) -> bool:
        try:
            order_book = self.wl.order_book(pair)
            self.redis_conn.set(pair, json.dumps(order_book), ex=self.expiry)
            return True
        except Exception as e:
            raise e
        except wallex.exceptions.RequestsExceptions as e:
            raise e

    def read_order_book(self, symbol: str):
        order_book = self.redis_conn.get(symbol.upper())
        if order_book:
            return json.loads(order_book)
        else:
            raise EmptyCacheException(f'No cached order book for {symbol}')

    def run(self):
        currencies = self.gen_currencies()
        while True:
            threads = [Thread(target=self.cache_orderbook, args=(x,)) for x in currencies]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            time.sleep(self.sleep)


if __name__ == '__main__':
    try:
        Cacher().run()
    except KeyboardInterrupt:
        print('\n\n[EXIT]')
        exit(0)
