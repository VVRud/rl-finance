import datetime
from db import pg_db, mongo_db
from finances import fh
from celery_worker.worker import celery_app


def fill_name_value(results, name, value):
    for i in range(len(results)):
        results[i] = {**results[i], name: value}
    return results


@celery_app.task(name="stock_candles_full", queue="stock_candles")
async def full_retrieve_stock_candles(
    symbol: str, c_id: int, resolution: str,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    result = await fh.get_stock_candles(symbol, resolution, startdate, enddate)
    if len(result) != 0:
        result = fill_name_value(result, "c_id", c_id)
        result = fill_name_value(result, "resolution", resolution)
        await pg_db.insert_stock_candles(result)


@celery_app.task(name="balance_sheets_full")
async def full_retrieve_balance_sheets(symbol: str, c_id: int):
    result = await fh.get_balance_sheets(symbol)
    if len(result) != 0:
        await mongo_db.insert_balance_sheets(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="cash_flows_full")
async def full_retrieve_cash_flows(symbol: str, c_id: int):
    result = await fh.get_cash_flows(symbol)
    if len(result) != 0:
        await mongo_db.insert_cash_flows(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="income_statements_full")
async def full_retrieve_income_statements(symbol: str, c_id: int):
    result = await fh.get_income_statements(symbol)
    if len(result) != 0:
        await mongo_db.insert_income_statements(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="similarities_full")
async def full_retrieve_similarities(symbol: str, c_id: int):
    result = await fh.get_similarity_index(symbol)
    if len(result) != 0:
        await pg_db.insert_sec_similarity(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="sentiments_full")
async def full_retrieve_sentiments(
    symbol: str, c_id: int,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    filings = await fh.get_filings(symbol, startdate, enddate)
    result = await fh.get_sec_sentiments(filings)
    if len(result) != 0:
        await pg_db.insert_sec_sentiment(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="dividents_full")
async def full_retrieve_dividents(
    symbol: str, c_id: int,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    result = await fh.get_dividends(symbol, startdate, enddate)
    if len(result) != 0:
        await pg_db.insert_dividends(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="press_releases_full")
async def full_retrieve_press_releases(
    symbol: str, c_id: int,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    result = await fh.get_press_releases(symbol, startdate, enddate)
    if len(result) != 0:
        await mongo_db.insert_prs(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="splits_full")
async def full_retrieve_splits(symbol: str, c_id: int, startdate: datetime.datetime, enddate: datetime.datetime):
    result = await fh.get_splits(symbol, startdate, enddate)
    if len(result) != 0:
        await pg_db.insert_splits(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="trends_full")
async def full_retrieve_trends(symbol: str, c_id: int):
    result = await fh.get_trends(symbol)
    if len(result) != 0:
        await pg_db.insert_trends(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="eps_surprises_full")
async def full_retrieve_eps_surprises(symbol: str, c_id: int):
    result = await fh.get_eps_surprises(symbol)
    if len(result) != 0:
        await pg_db.insert_eps_surprises(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="eps_estimates_full")
async def full_retrieve_eps_estimates(symbol: str, c_id: int):
    result = await fh.get_eps_estimates(symbol)
    if len(result) != 0:
        await pg_db.insert_eps_estimates(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="revenue_estimates_full")
async def full_retrieve_revenue_estimates(symbol: str, c_id: int):
    result = await fh.get_revenue_estimates(symbol)
    if len(result) != 0:
        await pg_db.insert_revenue_estimates(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="upgrades_downgrades_full")
async def full_retrieve_upgrades_downgrades(
    symbol: str, c_id: int,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    result = await fh.get_upgrades_downgrades(symbol, startdate, enddate)
    if len(result) != 0:
        await pg_db.insert_upgrades_downgrades(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="earnings_calendar_full")
async def full_retrieve_earnings_calendars(
    symbol: str, c_id: int,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    result = await fh.get_earnings_calendars(symbol, startdate, enddate)
    if len(result) != 0:
        await pg_db.insert_earnings_calendars(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="crypto_candles_full", queue="crypto_candles")
async def full_retrieve_crypto_candles(
    symbol: str, c_id: int, resolution: str,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    result = await fh.get_crypto_candles(symbol, resolution, startdate, enddate)
    if len(result) != 0:
        result = fill_name_value(result, "c_id", c_id)
        result = fill_name_value(result, "resolution", resolution)
        await pg_db.insert_crypto_candles(result)
