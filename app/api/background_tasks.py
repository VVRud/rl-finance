import datetime
import dateutil.relativedelta
from celery_worker.worker import celery_app
from finances import fh
from db import pg_db

HORIZON_YEARS_MARKET = 10
HORIZON_DAYS_MARKET = 21
HORIZON_YEARS_NEWS_RELEASES = 3


async def add_crypto_tasks(symbol: str, profile: dict):
    crypto = await pg_db.get_crypto(symbol)
    if crypto is None:
        c_id = await pg_db.insert_crypto(profile)

        enddate = datetime.datetime.now()
        startdate = enddate - dateutil.relativedelta.relativedelta(years=HORIZON_YEARS_MARKET)
        for resolution in fh.resolutions:
            celery_app.send_task("stock_candles_full", args=(symbol, c_id, resolution, startdate, enddate))
