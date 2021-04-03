import datetime
import dateutil.relativedelta
from celery_worker.worker import celery_app
from finances import fh
from db import pg_db

HORIZON = 9


async def add_company_tasks(symbol: str, profile: dict):
    companies = await pg_db.get_company(symbol)
    if companies is None:
        today = datetime.datetime.today()
        enddate = datetime.datetime(
            year=today.year, month=today.month + 1, day=1
        ) - datetime.timedelta(days=1)
        startdate = enddate - dateutil.relativedelta.relativedelta(months=2)

        c_id = await pg_db.insert_company(profile)
        while startdate.year != (today.year - HORIZON):
            for resolution in fh.resolutions:
                celery_app.send_task("stock_candles_full", args=(symbol, c_id, resolution, startdate, enddate))
            celery_app.send_task("sentiments_full", args=(symbol, c_id, startdate, enddate))
            celery_app.send_task("dividents_full", args=(symbol, c_id, startdate, enddate))
            celery_app.send_task("press_releases_full", args=(symbol, c_id, startdate, enddate))
            celery_app.send_task("splits_full", args=(symbol, c_id, startdate, enddate))
            celery_app.send_task("upgrades_downgrades_full", args=(symbol, c_id, startdate, enddate))
            celery_app.send_task("earnings_calendars_full", args=(symbol, c_id, startdate, enddate))
            celery_app.send_task("company_news_full", args=(symbol, c_id, startdate, enddate))

            enddate = enddate - dateutil.relativedelta.relativedelta(months=2)
            startdate = startdate - dateutil.relativedelta.relativedelta(months=2)

        celery_app.send_task("balance_sheets_full", args=(symbol, c_id))
        celery_app.send_task("cash_flows_full", args=(symbol, c_id))
        celery_app.send_task("income_statements_full", args=(symbol, c_id))
        celery_app.send_task("similarities_full", args=(symbol, c_id))
        celery_app.send_task("trends_full", args=(symbol, c_id))
        celery_app.send_task("eps_surprises_full", args=(symbol, c_id))
        celery_app.send_task("eps_estimates_full", args=(symbol, c_id))
        celery_app.send_task("revenue_estimates_full", args=(symbol, c_id))


async def add_crypto_tasks(symbol: str, profile: dict):
    crypto = await pg_db.get_crypto(symbol)
    if crypto is None:
        today = datetime.datetime.today()
        enddate = datetime.datetime(
            year=today.year, month=today.month + 1, day=1
        ) - datetime.timedelta(days=1)
        startdate = enddate - dateutil.relativedelta.relativedelta(months=2)

        c_id = await pg_db.insert_crypto(profile)
        while startdate.year != (today.year - HORIZON):
            for resolution in fh.resolutions:
                celery_app.send_task("crypto_candles_full", args=(symbol, c_id, resolution, startdate, enddate))
            enddate = enddate - dateutil.relativedelta.relativedelta(months=2)
            startdate = startdate - dateutil.relativedelta.relativedelta(months=2)
