import os
import logging
from fastapi import FastAPI
from fastapi.logger import logger as api_logger
from databases.core import logger as db_logger
from db import pg_db, mongo_db
from finances import fh, fm
from routes import router

gunicorn_logger = logging.getLogger("gunicorn.error")
api_logger.handlers = gunicorn_logger.handlers
api_logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
db_logger.handlers = gunicorn_logger.handlers
db_logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

app = FastAPI(redoc_url=None)
app.include_router(router)


@app.on_event("startup")
async def startup():
    await pg_db.connect()


@app.on_event("shutdown")
async def shutdown():
    await pg_db.disconnect()
    mongo_db.close()
    await fh.close()
    await fm.close()
