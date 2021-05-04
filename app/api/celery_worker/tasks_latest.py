import datetime
from finances import fh, fm
from celery_worker.worker import celery_app
from celery_worker.db_tasks import PostgresTask, MongoTask


def fill_name_value(results, name, value):
    for i in range(len(results)):
        results[i] = {**results[i], name: value}
    return results


@celery_app.task(name="stock_candles_latest", base=PostgresTask, bind=True)
async def latest_retrieve_stock_candles(self, symbol: str, c_id: int, resolution: str):
    latest = await (await self.db).get_stock_candles(symbol, resolution, 10)
    if len(latest) == 0:
        return
    startdate = latest[0]["date"]
    enddate = datetime.datetime.now()
    result = await fh.get_stock_candles(symbol, resolution, startdate, enddate)
    if len(result) != 0:
        result = fill_name_value(result, "c_id", c_id)
        result = fill_name_value(result, "resolution", resolution)
        await (await self.db).insert_stock_candles(result)


@celery_app.task(name="company_news_latest", base=MongoTask, bind=True)
async def latest_retrieve_company_news(self, symbol: str, c_id: int):
    latest = await (await self.db).get_company_news(symbol)
    if len(latest) == 0:
        return
    startdate = latest[0]["date"]
    enddate = datetime.datetime.now()
    result = await fh.get_company_news(symbol, startdate, enddate)
    if len(result) != 0:
        await (await self.db).insert_company_news(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="balance_sheets_latest", base=MongoTask, bind=True)
async def latest_retrieve_balance_sheets(self, symbol: str, c_id: int):
    result = await fh.get_balance_sheets(symbol)
    latest = await (await self.db).get_balance_sheets(symbol)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    if len(result) != 0:
        await (await self.db).insert_balance_sheets(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="cash_flows_latest", base=MongoTask, bind=True)
async def latest_retrieve_cash_flows(self, symbol: str, c_id: int):
    result = await fh.get_cash_flows(symbol)
    latest = await (await self.db).get_cash_flows(symbol)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    if len(result) != 0:
        await (await self.db).insert_cash_flows(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="income_statements_latest", base=MongoTask, bind=True)
async def latest_retrieve_income_statements(self, symbol: str, c_id: int):
    result = await fh.get_income_statements(symbol)
    latest = await (await self.db).get_income_statements(symbol)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    if len(result) != 0:
        await (await self.db).insert_income_statements(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="similarities_latest", base=PostgresTask, bind=True)
async def latest_retrieve_similarities(self, symbol: str, c_id: int):
    result = await fh.get_similarity_index(symbol)
    latest = await (await self.db).get_sec_similarities(symbol, 10)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    if len(result) != 0:
        await (await self.db).insert_sec_similarity(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="sentiments_latest", base=PostgresTask, bind=True)
async def latest_retrieve_sentiments(self, symbol: str, c_id: int):
    latest = await (await self.db).get_sec_sentiments(symbol, 10)
    if len(latest) == 0:
        return
    startdate = latest[0]["date"]
    enddate = datetime.datetime.now()
    result = await fh.get_sec_sentiments(await fh.get_filings(symbol, startdate, enddate))
    if len(result) != 0:
        await (await self.db).insert_sec_sentiment(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="dividends_latest", base=PostgresTask, bind=True)
async def latest_retrieve_dividends(self, symbol: str, c_id: int):
    latest = await (await self.db).get_dividends(symbol, 10)
    if len(latest) == 0:
        return
    startdate = latest[0]["date"]
    enddate = datetime.datetime.now()
    result = await fh.get_dividends(symbol, startdate, enddate)
    if len(result) != 0:
        await (await self.db).insert_dividends(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="press_releases_latest", base=MongoTask, bind=True)
async def latest_retrieve_press_releases(self, symbol: str, c_id: int):
    latest = await (await self.db).get_press_releases(symbol)
    if len(latest) == 0:
        return
    startdate = latest[0]["date"]
    enddate = datetime.datetime.now()
    result = await fh.get_press_releases(symbol, startdate, enddate)
    if len(result) != 0:
        await (await self.db).insert_press_releases(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="splits_latest", base=PostgresTask, bind=True)
async def latest_retrieve_splits(self, symbol: str, c_id: int):
    latest = await (await self.db).get_splits(symbol)
    if len(latest) == 0:
        return
    startdate = latest[0]["date"]
    enddate = datetime.datetime.now()
    result = await fh.get_splits(symbol, startdate, enddate)
    if len(result) != 0:
        await (await self.db).insert_splits(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="trends_latest", base=PostgresTask, bind=True)
async def latest_retrieve_trends(self, symbol: str, c_id: int):
    result = await fh.get_trends(symbol)
    latest = await (await self.db).get_trends(symbol)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    if len(result) != 0:
        await (await self.db).insert_trends(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="eps_surprises_latest", base=PostgresTask, bind=True)
async def latest_retrieve_eps_surprises(self, symbol: str, c_id: int):
    result = await fh.get_eps_surprises(symbol)
    latest = await (await self.db).get_eps_surprises(symbol)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    if len(result) != 0:
        await (await self.db).insert_eps_surprises(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="eps_estimates_latest", base=PostgresTask, bind=True)
async def latest_retrieve_eps_estimates(self, symbol: str, c_id: int):
    result = await fh.get_eps_estimates(symbol)
    latest = await (await self.db).get_eps_estimates(symbol)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    if len(result) != 0:
        await (await self.db).insert_eps_estimates(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="revenue_estimates_latest", base=PostgresTask, bind=True)
async def latest_retrieve_revenue_estimates(self, symbol: str, c_id: int):
    result = await fh.get_revenue_estimates(symbol)
    latest = await (await self.db).get_revenue_estimates(symbol)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    if len(result) != 0:
        await (await self.db).insert_revenue_estimates(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="upgrades_downgrades_latest", base=PostgresTask, bind=True)
async def latest_retrieve_upgrades_downgrades(self, symbol: str, c_id: int):
    latest = await (await self.db).get_upgrades_downgrades(symbol)
    if len(latest) == 0:
        return
    startdate = latest[0]["date"]
    enddate = datetime.datetime.now()
    result = await fh.get_upgrades_downgrades(symbol, startdate, enddate)
    if len(result) != 0:
        await (await self.db).insert_upgrades_downgrades(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="earnings_calendars_latest", base=PostgresTask, bind=True)
async def latest_retrieve_earnings_calendars(self, symbol: str, c_id: int):
    latest = await (await self.db).get_earnings_calendars(symbol)
    if len(latest) == 0:
        return
    startdate = latest[0]["date"]
    enddate = datetime.datetime.now()
    result = await fh.get_earnings_calendars(symbol, startdate, enddate)
    if len(result) != 0:
        await (await self.db).insert_earnings_calendars(fill_name_value(result, "c_id", c_id))


@celery_app.task(name="crypto_candles_latest", base=PostgresTask, bind=True)
async def latest_retrieve_crypto_candles(self, symbol: str, c_id: int, resolution: str):
    latest = await (await self.db).get_crypto_candles(symbol, resolution, 10)
    if len(latest) == 0:
        return
    startdate = latest[0]["date"]
    enddate = datetime.datetime.now()
    result = await fh.get_crypto_candles(symbol, resolution, startdate, enddate)
    if len(result) != 0:
        result = fill_name_value(result, "c_id", c_id)
        result = fill_name_value(result, "resolution", resolution)
        await (await self.db).insert_crypto_candles(result)


@celery_app.task(name="finimize_latest", base=MongoTask, bind=True)
async def latest_retrieve_finimize(self, _id):
    this, _ = await fm.get_single(_id)
    if this is not None:
        await (await self.db).insert_finimize_news([this])
