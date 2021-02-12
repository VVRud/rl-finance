import datetime
from finances import av, fh
from celery_worker.worker import celery_app
from celery_worker.db_tasks import PostgresTask, MongoTask


def fill_id(results, c_id):
    c_id = {"c_id": c_id}
    for i in range(len(results)):
        results[i] = {**results[i], **c_id}
    return results


@celery_app.task(name="intraday_full", base=PostgresTask, bind=True, queue="intraday")
async def full_retrieve_intraday(self, symbol: str, interval: str, time_slice: str, c_id: int):
    result = await av.get_intraday_full(symbol, interval, time_slice)
    if datetime.datetime.today().minute % int(interval.replace("min", "").strip()) != 0:
        result = result[1:]
    ids = await (await self.db).insert_intraday(fill_id(result, c_id), interval)
    return ids


@celery_app.task(name="daily_full", base=PostgresTask, bind=True, queue="daily")
async def full_retrieve_daily(self, symbol: str, c_id: int):
    h = datetime.datetime.today().hour
    result = await av.get_daily(symbol)
    if h > 16 or h < 3:
        result = result[1:]
    ids = await (await self.db).insert_daily(fill_id(result, c_id))
    return ids


@celery_app.task(name="weekly_full", base=PostgresTask, bind=True)
async def full_retrieve_weekly(self, symbol: str, c_id: int):
    result = await av.get_weekly(symbol)
    if datetime.date.today().weekday < 5:
        result = result[1:]
    ids = await (await self.db).insert_weekly(fill_id(result, c_id))
    return ids


@celery_app.task(name="monthly_full", base=PostgresTask, bind=True)
async def full_retrieve_monthly(self, symbol: str, c_id: int):
    result = await av.get_monthly(symbol)
    if result[0]["date"].month == datetime.date.today().month:
        result = result[1:]
    ids = await (await self.db).insert_monthly(fill_id(result, c_id))
    return ids


@celery_app.task(name="balance_sheets_full", base=MongoTask, bind=True)
async def full_retrieve_balance_sheets(self, symbol: str, c_id: int):
    result = await fh.get_balance_sheets(symbol)
    ids = None
    if len(result) != 0:
        ids = await (await self.db).insert_balance_sheets(fill_id(result, c_id))
        ids = [str(_id) for _id in ids.inserted_ids]
    return ids


@celery_app.task(name="cash_flows_full", base=MongoTask, bind=True)
async def full_retrieve_cash_flows(self, symbol: str, c_id: int):
    result = await fh.get_cash_flows(symbol)
    ids = None
    if len(result) != 0:
        ids = await (await self.db).insert_cash_flows(fill_id(result, c_id))
        ids = [str(_id) for _id in ids.inserted_ids]
    return ids


@celery_app.task(name="income_statements_full", base=MongoTask, bind=True)
async def full_retrieve_income_statements(self, symbol: str, c_id: int):
    result = await fh.get_income_statements(symbol)
    ids = None
    if len(result) != 0:
        ids = await (await self.db).insert_income_statements(fill_id(result, c_id))
        ids = [str(_id) for _id in ids.inserted_ids]
    return ids


@celery_app.task(name="similarities_full", base=PostgresTask, bind=True)
async def full_retrieve_similarities(self, symbol: str, c_id: int):
    result = await fh.get_similarity_index(symbol)
    ids = await (await self.db).insert_sec_similarity(fill_id(result, c_id))
    return ids


@celery_app.task(name="sentiments_full", base=PostgresTask, bind=True)
async def full_retrieve_sentiments(self, symbol: str, c_id: int, startdate: str, enddate: str):
    filings = await fh.get_filings(symbol, enddate, startdate)
    result = await fh.get_sec_sentiments(filings)
    ids = await (await self.db).insert_sec_sentiment(fill_id(result, c_id))
    return ids


@celery_app.task(name="dividents_full", base=PostgresTask, bind=True)
async def full_retrieve_dividents(self, symbol: str, c_id: int, startdate: str, enddate: str):
    result = await fh.get_dividends(symbol, enddate, startdate)
    ids = await (await self.db).insert_dividends(fill_id(result, c_id))
    return ids


@celery_app.task(name="press_releases_full", base=MongoTask, bind=True)
async def full_retrieve_press_releases(self, symbol: str, c_id: int, startdate: str, enddate: str):
    result = await fh.get_press_releases(symbol, enddate, startdate)
    ids = None
    if len(result) != 0:
        ids = await (await self.db).insert_prs(fill_id(result, c_id))
        ids = [str(_id) for _id in ids.inserted_ids]
    return ids
