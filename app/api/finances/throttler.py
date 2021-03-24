from os import getenv
import time
from typing import List
import asyncio
import aiohttp
from redis import Redis
from gql import Client
from gql.transport.requests import RequestsHTTPTransport


class Limit():
    def __init__(self, rate: int, period: float, retry: float, key: str):
        self.rate = rate
        self.period = period
        self.retry = retry
        self.redis = Redis(
            host=getenv("REDIS_HOST"), port=getenv("REDIS_PORT"), db=1
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


class BasicThrottler():
    def __init__(self, limits: List[Limit]):
        self.limits = sorted(limits, key=lambda x: x.period)

    def get_status(self):
        return [limit.get_status() for limit in self.limits]

    async def acquire(self):
        for limit in self.limits:
            await limit.acquire()

        for limit in self.limits:
            limit.push()

    async def make_request(self, *args, **kwargs):
        raise NotImplementedError()

    async def close(self):
        raise NotImplementedError()


class FinnnhubThrottler(BasicThrottler):
    def __init__(self, limits: List[Limit]):
        self.session = aiohttp.ClientSession()
        super(FinnnhubThrottler, self).__init__(limits)

    async def make_request(self, *args, **kwargs):
        await self.acquire()
        return self.session.request(*args, **kwargs)

    async def close(self):
        await self.session.close()


class FinimizeThrottler(BasicThrottler):
    def __init__(self, limits: List[Limit], url: str, headers: dict):
        self.url = url
        self.headers = headers

        self.transport = RequestsHTTPTransport(url=self.url, headers=self.headers)
        self.client = Client(transport=self.transport)

        super(FinimizeThrottler, self).__init__(limits)

    async def make_request(self, *args, **kwargs):
        await self.acquire()
        return self.client.execute(*args, **kwargs)

    async def close(self):
        await self.transport.close()
