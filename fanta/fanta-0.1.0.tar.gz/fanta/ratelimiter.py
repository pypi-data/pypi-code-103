"""
MIT License

Copyright (c) 2021 RPS
Copyright (c) 2020-2021 Tag-Epic

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from asyncio import Lock, sleep
from time import time
from logging import getLogger

logger = getLogger("fanta.ratelimiter")


class TimesPer:
    def __init__(self, times, per):
        self.times = times
        self.per = per
        self.lock = Lock()
        self.left = self.times
        self.reset = time() + per

    async def trigger(self):
        async with self.lock:
            current_time = time()
            if current_time >= self.reset:
                self.reset = current_time + self.per
                self.left = self.times
            if self.left == 0:
                sleep_for = self.reset - current_time
                logger.debug(f"Ratelimited! Sleeping for {sleep_for}s")
                await sleep(self.reset - current_time)
                self.left = self.times
            self.left -= 1
