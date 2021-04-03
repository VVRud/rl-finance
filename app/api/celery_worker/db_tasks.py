from async_property import async_property
from databases.core import logger
from db import PgCrud, mongo_db
from asyncpg.exceptions import ConnectionDoesNotExistError
from asyncpg.exceptions._base import InterfaceError
from celery import Task


class PostgresTask(Task):
    _db = None
    autoretry_for = (InterfaceError, ConnectionDoesNotExistError)
    retry_kwargs = {"max_retries": 12, "countdown": 10}

    @async_property
    async def db(self):
        if self._db is None:
            db = PgCrud()
            try:
                await db.connect()
            except AssertionError as e:
                logger.warning(f"Skipping. {str(e)}")
            finally:
                self._db = db
        return self._db


class MongoTask(Task):
    _db = None

    @async_property
    async def db(self):
        if self._db is None:
            self._db = mongo_db
        return self._db
