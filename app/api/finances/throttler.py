from os import getenv
import time
from typing import List
import asyncio
import aiohttp
from redis import Redis


class Limit():
    def __init__(self, rate: int, period: float, retry: float, key: str):
        self.rate = rate
        self.period = period
        self.retry = retry
        self.redis = Redis(
            host=getenv("REDIS_HOST"), port=getenv("REDIS_PORT"),
            password=getenv("REDIS_PASSWORD"), db=1
        )
        self.key = key

    def flush(self):
        while self.redis.llen(self.key):
            now = time.time()
            earliest = float(self.redis.lindex(self.key, 0).decode("utf-8"))
            if now - earliest > self.period:
                self.redis.lpop(self.key)
            else:
                break

    async def acquire(self):
        while True:
            self.flush()
            if self.redis.llen(self.key) < self.rate:
                break
            await asyncio.sleep(self.retry)

    def get_status(self):
        self.flush()
        return {
            "name": self.key,
            "opened": self.redis.llen(self.key) < self.rate,
            "rate": self.rate,
            "period": self.period,
            "retry": self.retry
        }

    def push(self):
        self.redis.rpush(self.key, time.time())


class Throttler():
    def __init__(self, limits: List[Limit]):
        self.limits = sorted(limits, key=lambda x: x.period)
        self.session = aiohttp.ClientSession()

    async def acquire(self):
        for limit in self.limits:
            await limit.acquire()

        for limit in self.limits:
            limit.push()

    async def make_request(self, *args, **kwargs):
        await self.acquire()
        return self.session.request(*args, **kwargs)

    def get_status(self):
        return [limit.get_status() for limit in self.limits]

    async def close(self):
        await self.session.close()
