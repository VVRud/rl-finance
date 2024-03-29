import logging
from os import getenv
import time
from typing import List
import asyncio
import aiohttp
from redis import Redis
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport, log

log.setLevel(logging.ERROR)


class Limit():
    def __init__(self, rate: int, period: float, retry: float, key: str):
        self.rate = rate
        self.period = period
        self.retry = retry
        self.redis = Redis(
            host=getenv("REDIS_HOST"), port=getenv("REDIS_PORT"),
            db=int(float(getenv("REDIS_THROTTLER_DB")))
        )
        self.key = key

    def flush(self):
        while self.redis.llen(self.key):
            earliest = self.redis.lindex(self.key, 0)
            if earliest is not None:
                now = time.time()
                earliest = float(earliest.decode("utf-8"))
                if now - earliest > self.period:
                    self.redis.lpop(self.key)
                else:
                    break
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
            "used": self.redis.llen(self.key),
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
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10 * 60))
        super(FinnnhubThrottler, self).__init__(limits)

    async def make_request(self, *args, **kwargs):
        while True:
            await self.acquire()

            try:
                resp = await self.session.request(*args, **kwargs)
            except (aiohttp.ClientOSError, asyncio.TimeoutError):
                resp = None

            if resp is not None and resp.ok:
                break
        return resp

    async def close(self):
        await self.session.close()


class FinimizeThrottler(BasicThrottler):
    def __init__(self, limits: List[Limit], url: str, headers: dict):
        self.url = url
        self.headers = headers

        super(FinimizeThrottler, self).__init__(limits)

    async def make_request(self, *args, **kwargs):
        await self.acquire()
        async with Client(transport=AIOHTTPTransport(url=self.url, headers=self.headers)) as session:
            result = await session.execute(*args, **kwargs)
        return result

    async def close(self):
        await self.transport.close()
