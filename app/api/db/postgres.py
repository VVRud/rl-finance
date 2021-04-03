import os
from typing import List
from databases import Database
from sqlalchemy import desc, and_
from sqlalchemy.dialects.postgresql import insert
from .pg_tables import (
    companies, dividends, sec_sentiment, sec_similarity,
    stocks_candles, splits,
    trends, eps_estimates, eps_surprises, upgrades_downgrades, revenue_estimates, earnings_calendars,
    crypto, crypto_candles
)


class PgCrud(Database):

    def __init__(self):
        self.database_url = (
            f"postgresql://{os.getenv('POSTGRES_USERNAME')}:{os.getenv('POSTGRES_PASSWORD')}@"
            f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/"
            f"{os.getenv('POSTGRES_DATABASE')}"
        )

        min_size = int(os.getenv("POSTGRES_MIN_CONN", 1))
        max_size = int(os.getenv("POSTGRES_MAX_CONN", 2))

        super(PgCrud, self).__init__(self.database_url, min_size=min_size, max_size=max_size)

    def get_status(self):
        return {
            "connected": self.is_connected
        }

    def mappings_to_dicts(self, values: list):
        return [dict(v) for v in values]

    # INSERT VALUES
    async def insert_company(self, values: dict):
        async with self.transaction():
            query = insert(companies).on_conflict_do_nothing()
            c_id = await self.execute(query, values)
        return c_id

    async def insert_dividends(self, values: List[dict]):
        async with self.transaction():
            query = insert(dividends).on_conflict_do_nothing()
            await self.execute_many(query, values)

    async def insert_sec_sentiment(self, values: List[dict]):
        async with self.transaction():
            query = insert(sec_sentiment).on_conflict_do_nothing()
            await self.execute_many(query, values)

    async def insert_sec_similarity(self, values: List[dict]):
        async with self.transaction():
            query = insert(sec_similarity).on_conflict_do_nothing()
            await self.execute_many(query, values)

    async def insert_stock_candles(self, values: List[dict]):
        async with self.transaction():
            query = insert(stocks_candles).on_conflict_do_nothing()
            await self.execute_many(query, values)

    async def insert_splits(self, values: List[dict]):
        async with self.transaction():
            query = insert(splits).on_conflict_do_nothing()
            await self.execute_many(query, values)

    async def insert_trends(self, values: List[dict]):
        async with self.transaction():
            query = insert(trends).on_conflict_do_nothing()
            await self.execute_many(query, values)

    async def insert_eps_estimates(self, values: List[dict]):
        async with self.transaction():
            query = insert(eps_estimates).on_conflict_do_nothing()
            await self.execute_many(query, values)

    async def insert_eps_surprises(self, values: List[dict]):
        async with self.transaction():
            query = insert(eps_surprises).on_conflict_do_nothing()
            await self.execute_many(query, values)

    async def insert_upgrades_downgrades(self, values: List[dict]):
        async with self.transaction():
            query = insert(upgrades_downgrades).on_conflict_do_nothing()
            await self.execute_many(query, values)

    async def insert_revenue_estimates(self, values: List[dict]):
        async with self.transaction():
            query = insert(revenue_estimates).on_conflict_do_nothing()
            await self.execute_many(query, values)

    async def insert_earnings_calendars(self, values: List[dict]):
        async with self.transaction():
            query = insert(earnings_calendars).on_conflict_do_nothing()
            await self.execute_many(query, values)

    async def insert_crypto(self, values: dict):
        async with self.transaction():
            query = insert(crypto).on_conflict_do_nothing()
            c_id = await self.execute(query, values)
        return c_id

    async def insert_crypto_candles(self, values: List[dict]):
        async with self.transaction():
            query = insert(crypto_candles).on_conflict_do_update()
            await self.execute_many(query, values)

    # GET VALUES
    async def get_company(self, symbol: str):
        query = companies.select(
            whereclause=(companies.c.symbol == symbol)
        )
        row = await self.fetch_one(query)
        if row is not None:
            return dict(row)
        return row

    async def get_companies(self):
        query = companies.select()
        rows = await self.fetch_all(query)
        return self.mappings_to_dicts(rows)

    async def get_dividends(self, symbol: str, limit: int = 100, offset: int = None):
        _id = (await self.get_company(symbol))["id"]
        query = dividends.select(
            whereclause=(dividends.c.c_id == _id),
            order_by=desc(dividends.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return self.mappings_to_dicts(rows)

    async def get_sec_sentiments(self, symbol: str, limit: int = 100, offset: int = None):
        _id = (await self.get_company(symbol))["id"]
        query = sec_sentiment.select(
            whereclause=(sec_sentiment.c.c_id == _id),
            order_by=desc(sec_sentiment.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return self.mappings_to_dicts(rows)

    async def get_sec_similarities(self, symbol: str, limit: int = 100, offset: int = None):
        _id = (await self.get_company(symbol))["id"]
        query = sec_similarity.select(
            whereclause=(sec_similarity.c.c_id == _id),
            order_by=desc(sec_similarity.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return self.mappings_to_dicts(rows)

    async def get_stock_candles(self, symbol: str, resolution: str, limit: int = 100, offset: int = None):
        _id = (await self.get_company(symbol))["id"]
        query = stocks_candles.select(
            whereclause=and_(
                stocks_candles.c.c_id == _id,
                stocks_candles.c.resolution == resolution
            ),
            order_by=desc(stocks_candles.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return self.mappings_to_dicts(rows)

    async def get_splits(self, symbol: str, limit: int = 100, offset: int = None):
        _id = (await self.get_company(symbol))["id"]
        query = splits.select(
            whereclause=(splits.c.c_id == _id),
            order_by=desc(splits.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return self.mappings_to_dicts(rows)

    async def get_trends(self, symbol: str, limit: int = 100, offset: int = None):
        _id = (await self.get_company(symbol))["id"]
        query = trends.select(
            whereclause=(trends.c.c_id == _id),
            order_by=desc(trends.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return self.mappings_to_dicts(rows)

    async def get_eps_estimates(self, symbol: str, limit: int = 100, offset: int = None):
        _id = (await self.get_company(symbol))["id"]
        query = eps_estimates.select(
            whereclause=(eps_estimates.c.c_id == _id),
            order_by=desc(eps_estimates.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return self.mappings_to_dicts(rows)

    async def get_eps_surprises(self, symbol: str, limit: int = 100, offset: int = None):
        _id = (await self.get_company(symbol))["id"]
        query = eps_surprises.select(
            whereclause=(eps_surprises.c.c_id == _id),
            order_by=desc(eps_surprises.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return self.mappings_to_dicts(rows)

    async def get_upgrades_downgrades(self, symbol: str, limit: int = 100, offset: int = None):
        _id = (await self.get_company(symbol))["id"]
        query = upgrades_downgrades.select(
            whereclause=(upgrades_downgrades.c.c_id == _id),
            order_by=desc(upgrades_downgrades.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return self.mappings_to_dicts(rows)

    async def get_revenue_estimates(self, symbol: str, limit: int = 100, offset: int = None):
        _id = (await self.get_company(symbol))["id"]
        query = revenue_estimates.select(
            whereclause=(revenue_estimates.c.c_id == _id),
            order_by=desc(revenue_estimates.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return self.mappings_to_dicts(rows)

    async def get_earnings_calendars(self, symbol: str, limit: int = 100, offset: int = None):
        _id = (await self.get_company(symbol))["id"]
        query = earnings_calendars.select(
            whereclause=(earnings_calendars.c.c_id == _id),
            order_by=desc(earnings_calendars.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return self.mappings_to_dicts(rows)

    async def get_crypto(self, symbol: str):
        query = crypto.select(
            whereclause=(crypto.c.symbol == symbol)
        )
        row = await self.fetch_one(query)
        if row is not None:
            return dict(row)
        return row

    async def get_cryptos(self):
        query = crypto.select()
        rows = await self.fetch_all(query)
        return self.mappings_to_dicts(rows)

    async def get_crypto_candles(self, symbol: str, resolution: str, limit: int = 100, offset: int = None):
        _id = (await self.get_company(symbol))["id"]
        query = crypto_candles.select(
            whereclause=and_(
                crypto_candles.c.c_id == _id,
                crypto_candles.c.resolution == resolution
            ),
            order_by=desc(crypto_candles.c.date),
            limit=limit, offset=offset
        )
        rows = await self.fetch_all(query=query)
        return self.mappings_to_dicts(rows)
