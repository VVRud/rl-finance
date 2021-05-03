import datetime
import dateutil.relativedelta
from celery_worker.worker import celery_app
from db import pg_db

HORIZON_YEARS = 10
HORIZON_DAYS = 21


async def add_company_tasks(symbol: str, profile: dict):
    companies = await pg_db.get_company(symbol)
    if companies is None:
        c_id = await pg_db.insert_company(profile)

        today = datetime.datetime.now()
        finish = today - dateutil.relativedelta.relativedelta(years=HORIZON_YEARS)
        if profile["ipo"] is not None:
            finish = max(finish, profile["ipo"])

        enddate = today
        startdate = enddate - dateutil.relativedelta.relativedelta(days=HORIZON_DAYS)
        while startdate >= finish:
            for resolution in ["1", "5", "15", "30", "60"]:
                celery_app.send_task("stock_candles_full", args=(symbol, c_id, resolution, startdate, enddate))
            enddate = enddate - dateutil.relativedelta.relativedelta(days=HORIZON_DAYS)
            startdate = startdate - dateutil.relativedelta.relativedelta(days=HORIZON_DAYS)

        enddate = today
        startdate = finish
        for resolution in ["D", "W", "M"]:
            celery_app.send_task("stock_candles_full", args=(symbol, c_id, resolution, startdate, enddate))

            # TODO: Fix issues with next
#         celery_app.send_task("press_releases_full", args=(symbol, c_id, startdate, enddate))
#         celery_app.send_task("company_news_full", args=(symbol, c_id, startdate, enddate))
        celery_app.send_task("sentiments_full", args=(symbol, c_id, startdate, enddate))
        celery_app.send_task("dividends_full", args=(symbol, c_id, startdate, enddate))
        celery_app.send_task("splits_full", args=(symbol, c_id, startdate, enddate))
        celery_app.send_task("upgrades_downgrades_full", args=(symbol, c_id, startdate, enddate))
        celery_app.send_task("earnings_calendars_full", args=(symbol, c_id, startdate, enddate))

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
        c_id = await pg_db.insert_crypto(profile)

        today = datetime.datetime.now()
        finish = today - dateutil.relativedelta.relativedelta(years=HORIZON_YEARS)
        enddate = today
        startdate = enddate - dateutil.relativedelta.relativedelta(days=HORIZON_DAYS)
        while startdate >= finish:
            for resolution in ["1", "5", "15", "30", "60"]:
                celery_app.send_task("crypto_candles_full", args=(symbol, c_id, resolution, startdate, enddate))
            enddate = enddate - dateutil.relativedelta.relativedelta(days=HORIZON_DAYS)
            startdate = startdate - dateutil.relativedelta.relativedelta(days=HORIZON_DAYS)

        enddate = datetime.datetime.now()
        startdate = enddate - dateutil.relativedelta.relativedelta(years=HORIZON_YEARS)
        for resolution in ["D", "W", "M"]:
            celery_app.send_task("crypto_candles_full", args=(symbol, c_id, resolution, startdate, enddate))
