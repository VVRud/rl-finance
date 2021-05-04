import datetime
import dateutil.relativedelta
from celery_worker.worker import celery_app
from finances import fh
from db import pg_db

HORIZON_YEARS_MARKET = 10
HORIZON_DAYS_MARKET = 21
HORIZON_YEARS_NEWS_RELEASES = 3


async def add_company_tasks(symbol: str, profile: dict, track: bool):
    companies = await pg_db.get_company(symbol)
    if companies is None:
        if not track:
            profile = await fh.get_profile(symbol)
        if profile is not None:
            c_id = await pg_db.insert_company(profile)

            # Dealing with candles
            enddate = datetime.datetime.now()
            startdate = enddate - dateutil.relativedelta.relativedelta(years=HORIZON_YEARS_MARKET)
            if profile["ipo"] is not None:
                startdate = max(startdate, profile["ipo"])
            for resolution in fh.resolutions:
                celery_app.send_task("stock_candles_full", args=(symbol, c_id, resolution, startdate, enddate))

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

            # Dealing with news and press releases
            enddate = datetime.datetime.now()
            startdate = enddate - dateutil.relativedelta.relativedelta(years=HORIZON_YEARS_NEWS_RELEASES)
            if profile["ipo"] is not None:
                startdate = max(startdate, profile["ipo"])
            celery_app.send_task("company_news_full", args=(symbol, c_id, startdate, enddate))
            celery_app.send_task("press_releases_full", args=(symbol, c_id, startdate, enddate))


async def add_crypto_tasks(symbol: str, profile: dict):
    crypto = await pg_db.get_crypto(symbol)
    if crypto is None:
        c_id = await pg_db.insert_crypto(profile)
        
        enddate = datetime.datetime.now()
        startdate = enddate - dateutil.relativedelta.relativedelta(years=HORIZON_YEARS_MARKET)
        for resolution in fh.resolutions:
            celery_app.send_task("stock_candles_full", args=(symbol, c_id, resolution, startdate, enddate))
