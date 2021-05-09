import datetime
import dateutil.relativedelta
from finances import fh
from celery_worker.worker import celery_app
from celery_worker.db_tasks import PostgresTask, MongoTask

HORIZON_YEARS_MARKET = 10
HORIZON_DAYS_MARKET = 21
HORIZON_YEARS_NEWS_RELEASES = 3


def fill_name_value(results, name, value):
    for i in range(len(results)):
        results[i] = {**results[i], name: value}
    return results


@celery_app.task(name="add_company_parsing_tasks")
async def add_company_parsing_tasks(symbol: str, c_id: int, ipo: datetime.datetime):
    # Dealing with candles
    enddate = datetime.datetime.now()
    startdate = enddate - dateutil.relativedelta.relativedelta(years=HORIZON_YEARS_MARKET)
    if ipo is not None:
        startdate = max(startdate, ipo)
    for resolution, priority in zip(fh.resolutions, fh.priorities):
        await celery_app.send_task(
            "stock_candles_full", args=(symbol, c_id, resolution, startdate, enddate), priority=priority
        )

    await celery_app.send_task("sentiments_full", args=(symbol, c_id, startdate, enddate))
    await celery_app.send_task("dividends_full", args=(symbol, c_id, startdate, enddate))
    await celery_app.send_task("splits_full", args=(symbol, c_id, startdate, enddate))
    await celery_app.send_task("upgrades_downgrades_full", args=(symbol, c_id, startdate, enddate))
    await celery_app.send_task("earnings_calendars_full", args=(symbol, c_id, startdate, enddate))

    await celery_app.send_task("balance_sheets_full", args=(symbol, c_id))
    await celery_app.send_task("cash_flows_full", args=(symbol, c_id))
    await celery_app.send_task("income_statements_full", args=(symbol, c_id))
    await celery_app.send_task("similarities_full", args=(symbol, c_id))
    await celery_app.send_task("trends_full", args=(symbol, c_id))
    await celery_app.send_task("eps_surprises_full", args=(symbol, c_id))
    await celery_app.send_task("eps_estimates_full", args=(symbol, c_id))
    await celery_app.send_task("revenue_estimates_full", args=(symbol, c_id))

    # Dealing with news and press releases
    enddate = datetime.datetime.now()
    startdate = enddate - dateutil.relativedelta.relativedelta(years=HORIZON_YEARS_NEWS_RELEASES)
    if ipo is not None:
        startdate = max(startdate, ipo)
    await celery_app.send_task("company_news_full", args=(symbol, c_id, startdate, enddate))
    await celery_app.send_task("press_releases_full", args=(symbol, c_id, startdate, enddate))


@celery_app.task(name="stock_candles_full", base=PostgresTask, bind=True)
async def full_retrieve_stock_candles(
    self, symbol: str, c_id: int, resolution: str,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    result = await fh.get_stock_candles(symbol, resolution, startdate, enddate)
    if len(result) == 0 or startdate + dateutil.relativedelta.relativedelta(days=1) >= enddate:
        return
    result = fill_name_value(result, "c_id", c_id)
    result = fill_name_value(result, "resolution", resolution)
    prev_date = enddate
    enddate = min([res["date"] for res in result])
    if enddate == prev_date:
        return
    await (await self.db).insert_stock_candles(result)
    await celery_app.send_task("stock_candles_full", args=(symbol, c_id, resolution, startdate, enddate))


@celery_app.task(name="company_news_full", base=MongoTask, bind=True)
async def full_retrieve_company_news(
    self, symbol: str, c_id: int,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    result = await fh.get_company_news(symbol, startdate, enddate)
    if len(result) != 0 and startdate + dateutil.relativedelta.relativedelta(days=1) < enddate:
        prev_date = enddate
        enddate = min([res["date"] for res in result])
        if enddate != prev_date:
            await (await self.db).insert_company_news(fill_name_value(result, "c_id", c_id))
            await celery_app.send_task("company_news_full", args=(symbol, c_id, startdate, enddate))


@celery_app.task(name="balance_sheets_full", base=MongoTask, bind=True)
async def full_retrieve_balance_sheets(self, symbol: str, c_id: int):
    result = await fh.get_balance_sheets(symbol)
    if len(result) != 0:
        await (await self.db).insert_balance_sheets(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="cash_flows_full", base=MongoTask, bind=True)
async def full_retrieve_cash_flows(self, symbol: str, c_id: int):
    result = await fh.get_cash_flows(symbol)
    if len(result) != 0:
        await (await self.db).insert_cash_flows(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="income_statements_full", base=MongoTask, bind=True)
async def full_retrieve_income_statements(self, symbol: str, c_id: int):
    result = await fh.get_income_statements(symbol)
    if len(result) != 0:
        await (await self.db).insert_income_statements(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="similarities_full", base=PostgresTask, bind=True)
async def full_retrieve_similarities(self, symbol: str, c_id: int):
    result = await fh.get_similarity_index(symbol)
    if len(result) != 0:
        await (await self.db).insert_sec_similarity(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="sentiments_full", base=PostgresTask, bind=True)
async def full_retrieve_sentiments(
    self, symbol: str, c_id: int,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    filings = await fh.get_filings(symbol, startdate, enddate)
    result = await fh.get_sec_sentiments(filings)
    if len(result) != 0 and startdate + dateutil.relativedelta.relativedelta(days=1) < enddate:
        prev_date = enddate
        enddate = min([res["date"] for res in result])
        if enddate != prev_date:
            await (await self.db).insert_sec_sentiment(fill_name_value(result, "c_id", c_id))
            await celery_app.send_task("sentiments_full", args=(symbol, c_id, startdate, enddate))


@celery_app.task(name="dividends_full", base=PostgresTask, bind=True)
async def full_retrieve_dividends(
    self, symbol: str, c_id: int,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    result = await fh.get_dividends(symbol, startdate, enddate)
    if len(result) != 0 and startdate + dateutil.relativedelta.relativedelta(days=1) < enddate:
        prev_date = enddate
        enddate = min([res["date"] for res in result])
        if enddate != prev_date:
            await (await self.db).insert_dividends(fill_name_value(result, "c_id", c_id))
            await celery_app.send_task("dividends_full", args=(symbol, c_id, startdate, enddate))


@celery_app.task(name="press_releases_full", base=MongoTask, bind=True)
async def full_retrieve_press_releases(
    self, symbol: str, c_id: int,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    result = await fh.get_press_releases(symbol, startdate, enddate)
    if len(result) != 0 and startdate + dateutil.relativedelta.relativedelta(days=1) < enddate:
        prev_date = enddate
        enddate = min([res["date"] for res in result])
        if enddate != prev_date:
            await (await self.db).insert_press_releases(fill_name_value(result, "c_id", c_id))
            await celery_app.send_task("press_releases_full", args=(symbol, c_id, startdate, enddate))


@celery_app.task(name="splits_full", base=PostgresTask, bind=True)
async def full_retrieve_splits(self, symbol: str, c_id: int, startdate: datetime.datetime, enddate: datetime.datetime):
    result = await fh.get_splits(symbol, startdate, enddate)
    if len(result) != 0 and startdate + dateutil.relativedelta.relativedelta(days=1) < enddate:
        prev_date = enddate
        enddate = min([res["date"] for res in result])
        if enddate != prev_date:
            await (await self.db).insert_splits(fill_name_value(result, "c_id", c_id))
            await celery_app.send_task("splits_full", args=(symbol, c_id, startdate, enddate))


@celery_app.task(name="trends_full", base=PostgresTask, bind=True)
async def full_retrieve_trends(self, symbol: str, c_id: int):
    result = await fh.get_trends(symbol)
    if len(result) != 0:
        await (await self.db).insert_trends(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="eps_surprises_full", base=PostgresTask, bind=True)
async def full_retrieve_eps_surprises(self, symbol: str, c_id: int):
    result = await fh.get_eps_surprises(symbol)
    if len(result) != 0:
        await (await self.db).insert_eps_surprises(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="eps_estimates_full", base=PostgresTask, bind=True)
async def full_retrieve_eps_estimates(self, symbol: str, c_id: int):
    result = await fh.get_eps_estimates(symbol)
    if len(result) != 0:
        await (await self.db).insert_eps_estimates(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="revenue_estimates_full", base=PostgresTask, bind=True)
async def full_retrieve_revenue_estimates(self, symbol: str, c_id: int):
    result = await fh.get_revenue_estimates(symbol)
    if len(result) != 0:
        await (await self.db).insert_revenue_estimates(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="upgrades_downgrades_full", base=PostgresTask, bind=True)
async def full_retrieve_upgrades_downgrades(
    self, symbol: str, c_id: int,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    result = await fh.get_upgrades_downgrades(symbol, startdate, enddate)
    if len(result) != 0 and startdate + dateutil.relativedelta.relativedelta(days=1) < enddate:
        prev_date = enddate
        enddate = min([res["date"] for res in result])
        if enddate != prev_date:
            await (await self.db).insert_upgrades_downgrades(fill_name_value(result, "c_id", c_id))
            await celery_app.send_task("upgrades_downgrades_full", args=(symbol, c_id, startdate, enddate))


@celery_app.task(name="earnings_calendars_full", base=PostgresTask, bind=True)
async def full_retrieve_earnings_calendars(
    self, symbol: str, c_id: int,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    result = await fh.get_earnings_calendars(symbol, startdate, enddate)
    if len(result) != 0 and startdate + dateutil.relativedelta.relativedelta(days=1) < enddate:
        prev_date = enddate
        enddate = min([res["date"] for res in result])
        if enddate != prev_date:
            await (await self.db).insert_earnings_calendars(fill_name_value(result, "c_id", c_id))
            await celery_app.send_task("earnings_calendars_full", args=(symbol, c_id, startdate, enddate))


@celery_app.task(name="crypto_candles_full", base=PostgresTask, bind=True)
async def full_retrieve_crypto_candles(
    self, symbol: str, c_id: int, resolution: str,
    startdate: datetime.datetime, enddate: datetime.datetime
):
    while True:
        result = await fh.get_crypto_candles(symbol, resolution, startdate, enddate)
        if len(result) == 0 or startdate + dateutil.relativedelta.relativedelta(days=1) >= enddate:
            return
        result = fill_name_value(result, "c_id", c_id)
        result = fill_name_value(result, "resolution", resolution)
        prev_date = enddate
        enddate = min([res["date"] for res in result])
        if enddate == prev_date:
            return
        await (await self.db).insert_crypto_candles(result)
