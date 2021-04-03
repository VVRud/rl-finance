import os
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo


class MongoCrud(AsyncIOMotorClient):

    def __init__(self):
        super(MongoCrud, self).__init__(
            host=os.getenv("MONGO_HOST"),
            port=int(os.getenv("MONGO_PORT")),
            tz_aware=True,
            compressors="snappy",
            username=os.getenv("MONGO_USERNAME"),
            password=os.getenv("MONGO_PASSWORD"),
            authSource=os.getenv("MONGO_DATABASE")
        )

        self.db = self[os.getenv("MONGO_DATABASE")]

        self.prs_collection = self.db.press_releases
        self.news_collection = self.db.company_news
        self.finimize_collection = self.db.finimize_news

        self.bs_collection = self.db.balance_sheets
        self.is_collection = self.db.income_statements
        self.cf_collection = self.db.cash_flows

    def get_status(self):
        return {
            "connected": True,
            "threshold": self.local_threshold_ms
        }

    def change_id(self, doc):
        doc["_id"] = str(doc.pop("_id"))
        return doc

    # INSERT
    async def insert_company_news(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.news_collection.insert_many(docs, ordered=False, session=s)
        return [str(res) for res in result.inserted_ids]

    async def insert_press_releases(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.prs_collection.insert_many(docs, ordered=False, session=s)
        return [str(res) for res in result.inserted_ids]

    async def insert_cash_flows(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.cf_collection.insert_many(docs, ordered=False, session=s)
        return [str(res) for res in result.inserted_ids]

    async def insert_income_statements(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.is_collection.insert_many(docs, ordered=False, session=s)
        return [str(res) for res in result.inserted_ids]

    async def insert_balance_sheets(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.bs_collection.insert_many(docs, ordered=False, session=s)
        return [str(res) for res in result.inserted_ids]

    async def insert_finimize_news(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.finimize_collection.insert_many(docs, ordered=False, session=s)
        return [str(res) for res in result.inserted_ids]

    # RETRIEVE
    async def get_company_news(self, symbol: str, limit: int = 10, offset: int = 0):
        result = await (
            self.news_collection
            .find({"symbol": symbol})
            .sort("date", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]

    async def get_press_releases(self, symbol: str, limit: int = 10, offset: int = 0):
        result = await (
            self.prs_collection
            .find({"symbol": symbol})
            .sort("date", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]

    async def get_cash_flows(self, symbol: str = None, limit: int = 10, offset: int = 0):
        result = await (
            self.cf_collection
            .find({"symbol": symbol})
            .sort("date", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]

    async def get_income_statements(self, symbol: str = None, limit: int = 10, offset: int = 0):
        result = await (
            self.is_collection
            .find({"symbol": symbol})
            .sort("date", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]

    async def get_balance_sheets(self, symbol: str = None, limit: int = 10, offset: int = 0):
        result = await (
            self.bs_collection
            .find({"symbol": symbol})
            .sort("date", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]

    async def get_finimize_news(self, content_type: str = None, limit: int = 10, offset: int = 0):
        query = {}
        if content_type is not None:
            query = {"contentPieceType.identifier": content_type}

        result = await (
            self.finimize_collection
            .find(query)
            .sort("date", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]
