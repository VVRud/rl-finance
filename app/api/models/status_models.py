from typing import List
from pydantic import BaseModel


class PostgresModel(BaseModel):
    connected: bool


class MongoModel(BaseModel):
    connected: bool
    threshold: float


class RateLimitsModel(BaseModel):
    name: str
    opened: bool
    rate: int
    period: float
    retry: float


class StatusModel(BaseModel):
    postgres: PostgresModel
    mongo: MongoModel
    alphavantage: List[RateLimitsModel]
    finnhub: List[RateLimitsModel]
    finimize: List[RateLimitsModel]
