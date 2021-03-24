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

        self.bs_collection = self.db.balance_sheets
        self.is_collection = self.db.income_statements
        self.cf_collection = self.db.cash_flows

        self.insights_collection = self.db.insights
        self.briefs_collection = self.db.briefs
        self.other_collection = self.db.other

        self.funcs = {
            "INSIGHT": {
                "insert": self.insert_insights,
                "get": self.get_insights
            },
            "DAILY_BRIEF": {
                "insert": self.insert_briefs,
                "get": self.get_briefs
            },
            "OTHER": {
                "insert": self.insert_other,
                "get": self.get_other
            }
        }

    def get_status(self):
        return {
            "connected": True,
            "threshold": self.local_threshold_ms
        }

    def change_id(self, doc):
        doc["_id"] = str(doc.pop("_id"))
        return doc

    # INSERT
    async def insert_prs(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.prs_collection.insert_many(docs, session=s)
        return [self.change_id(res) for res in result]

    async def insert_cash_flows(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.cf_collection.insert_many(docs, session=s)
        return [self.change_id(res) for res in result]

    async def insert_income_statements(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.is_collection.insert_many(docs, session=s)
        return [self.change_id(res) for res in result]

    async def insert_balance_sheets(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.bs_collection.insert_many(docs, session=s)
        return [self.change_id(res) for res in result]

    async def insert_insights(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.insights_collection.insert_many(docs, session=s)
        return [self.change_id(res) for res in result]

    async def insert_briefs(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.briefs_collection.insert_many(docs, session=s)
        return [self.change_id(res) for res in result]

    async def insert_other(self, docs: List[dict]):
        async with await self.start_session() as s:
            result = await self.other_collection.insert_many(docs, session=s)
        return [self.change_id(res) for res in result]

    # RETRIEVE
    async def get_prs(self, symbol: str, limit: int = 10, offset: int = 0):
        result = await (
            self.prs_collection
            .find({"symbol": symbol})
            .sort("date_time", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]

    async def get_cash_flows(self, symbol: str = None, limit: int = 10, offset: int = 0):
        result = await (
            self.cf_collection
            .find({"symbol": symbol})
            .sort("dateUpdatedDisplay", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]

    async def get_income_statements(self, symbol: str = None, limit: int = 10, offset: int = 0):
        result = await (
            self.is_collection
            .find({"symbol": symbol})
            .sort("dateUpdatedDisplay", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]

    async def get_balance_sheets(self, symbol: str = None, limit: int = 10, offset: int = 0):
        result = await (
            self.bs_collection
            .find({"symbol": symbol})
            .sort("dateUpdatedDisplay", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]

    async def get_insights(self, limit: int = 10, offset: int = 0):
        result = await (
            self.insights_collection
            .find()
            .sort("dateUpdatedDisplay", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]

    async def get_briefs(self, limit: int = 10, offset: int = 0):
        result = await (
            self.briefs_collection
            .find()
            .sort("dateUpdatedDisplay", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]

    async def get_other(self, limit: int = 10, offset: int = 0):
        result = await (
            self.other_collection
            .find()
            .sort("dateUpdatedDisplay", pymongo.DESCENDING)
            .skip(offset).limit(limit)
            .to_list(length=limit)
        )
        return [self.change_id(res) for res in result]
