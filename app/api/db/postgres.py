import os
from typing import List
from databases import Database
from sqlalchemy import desc
from .pg_tables import (
    companies, dividends, sec_sentiment, sec_similarity,
    daily_prices, weekly_prices, monthly_prices, intraday_prices_1min,
    intraday_prices_5min, intraday_prices_15min, intraday_prices_30min, intraday_prices_60min,
)


class PgCrud(Database):

    def __init__(self):
        self.database_url = (
            f"postgresql://{os.getenv('POSTGRES_USERNAME')}:{os.getenv('POSTGRES_PASSWORD')}@"
            f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/"
            f"{os.getenv('POSTGRES_DATABASE')}"
        )
        super(PgCrud, self).__init__(self.database_url, min_size=2, max_size=5)

    def get_status(self):
        return {
            "connected": self.is_connected
        }

    def __get_intraday_table(self, interval: str):
        if interval == "1min":
            table = intraday_prices_1min
        elif interval == "5min":
            table = intraday_prices_5min
        elif interval == "15min":
            table = intraday_prices_15min
        elif interval == "30min":
            table = intraday_prices_30min
        elif interval == "60min":
            table = intraday_prices_60min
        else:
            raise ValueError(f"Unknown interval {interval}")
        return table

    async def get_id(self, symbol: str):
        _id = [
            company.id
            for company in await self.get_companies()
            if company.symbol == symbol
        ]
        return _id[0]

    # INSERT VALUES
    # Alpha Vantage
    async def insert_daily(self, values: List[dict]):
        async with self.transaction():
            query = daily_prices.insert()
            t_id = await self.execute_many(query, values)
        return t_id

    async def insert_weekly(self, values: List[dict]):
        async with self.transaction():
            query = weekly_prices.insert()
            t_id = await self.execute_many(query, values)
        return t_id

    async def insert_monthly(self, values: List[dict]):
        async with self.transaction():
            query = monthly_prices.insert()
            t_id = await self.execute_many(query, values)
        return t_id

    async def insert_intraday(self, values: List[dict], interval: str):
        async with self.transaction():
            query = self.__get_intraday_table(interval).insert()
            t_id = await self.execute_many(query, values)
        return t_id

    # Finnhub
    async def insert_company(self, values: dict):
        async with self.transaction():
            query = companies.insert()
            c_id = await self.execute(query, values)
        return c_id

    async def insert_sec_sentiment(self, values: List[dict]):
        async with self.transaction():
            query = sec_sentiment.insert()
            r_id = await self.execute_many(query, values)
        return r_id

    async def insert_sec_similarity(self, values: List[dict]):
        async with self.transaction():
            query = sec_similarity.insert()
            r_id = await self.execute_many(query, values)
        return r_id

    async def insert_dividends(self, values: List[dict]):
        async with self.transaction():
            query = dividends.insert()
            r_id = await self.execute_many(query, values)
        return r_id

    # GET VALUES
    # Alpha Vantage
    async def get_intraday(self, symbol: str, interval: str, limit: int = 100, offset: int = None):
        _id = await self.get_id(symbol)
        table = self.__get_intraday_table(interval)
        query = table.select(
            whereclause=(table.c.c_id == _id),
            order_by=desc(table.c.date_time),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return rows

    async def get_daily(self, symbol: str, limit: int = 100, offset: int = None):
        _id = await self.get_id(symbol)
        query = daily_prices.select(
            whereclause=(daily_prices.c.c_id == _id),
            order_by=desc(daily_prices.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return rows

    async def get_weekly(self, symbol: str, limit: int = 100, offset: int = None):
        _id = await self.get_id(symbol)
        query = weekly_prices.select(
            whereclause=(weekly_prices.c.c_id == _id),
            order_by=desc(weekly_prices.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return rows

    async def get_monthly(self, symbol: str, limit: int = 100, offset: int = None):
        _id = await self.get_id(symbol)
        query = monthly_prices.select(
            whereclause=(monthly_prices.c.c_id == _id),
            order_by=desc(monthly_prices.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return rows

    # Finnhub
    async def get_company(self, symbol: str):
        query = companies.select(
            whereclause=(companies.c.symbol == symbol)
        )
        row = await self.fetch_one(query)
        return row

    async def get_companies(self):
        query = companies.select()
        return await self.fetch_all(query)

    async def get_sec_sentiments(self, symbol: str, limit: int = 100, offset: int = None):
        _id = await self.get_id(symbol)
        query = sec_sentiment.select(
            whereclause=(sec_sentiment.c.c_id == _id),
            order_by=desc(sec_sentiment.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return rows

    async def get_sec_similarities(self, symbol: str, limit: int = 100, offset: int = None):
        _id = await self.get_id(symbol)
        query = sec_similarity.select(
            whereclause=(sec_similarity.c.c_id == _id),
            order_by=desc(sec_similarity.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return rows

    async def get_dividends(self, symbol: str, limit: int = 100, offset: int = None):
        _id = await self.get_id(symbol)
        query = dividends.select(
            whereclause=(dividends.c.c_id == _id),
            order_by=desc(dividends.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return rows
