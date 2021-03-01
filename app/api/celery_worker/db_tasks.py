from async_property import async_property
from databases.core import logger
from db import pg_db, mongo_db
from celery import Task


class PostgresTask(Task):
    _db = None

    @async_property
    async def db(self):
        if self._db is None:
            try:
                await pg_db.connect()
            except AssertionError as e:
                logger.warning(f"Is connected. Skipping. {str(e)}")
            finally:
                self._db = pg_db
        return self._db


class MongoTask(Task):
    _db = None

    @async_property
    async def db(self):
        if self._db is None:
            self._db = mongo_db
        return self._db
