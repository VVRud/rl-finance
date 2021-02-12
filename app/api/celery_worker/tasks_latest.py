import datetime
from finances import av, fh
from celery_worker.worker import celery_app
from celery_worker.db_tasks import PostgresTask, MongoTask


def fill_id(results, c_id):
    c_id = {"c_id": c_id}
    for i in range(len(results)):
        results[i] = {**results[i], **c_id}
    return results


@celery_app.task(name="intraday_latest", base=PostgresTask, bind=True)
async def latest_retrieve_intraday(self, symbol: str, interval: str, c_id: int):
    result = await av.get_intraday_latest(symbol, interval)
    latest = await (await self.db).get_intraday(symbol, interval, 10)
    if datetime.datetime.today().minute % int(interval.replace("min")) != 0:
        result = result[1:]
    result = [res for res in result if res["date_time"] > latest[0]["date_time"]]
    ids = await (await self.db).insert_intraday(fill_id(result, c_id), interval)
    return ids


@celery_app.task(name="daily_latest", base=PostgresTask, bind=True)
async def latest_retrieve_daily(self, symbol: str, c_id: int):
    result = await av.get_daily(symbol)
    latest = await (await self.db).get_daily(symbol, 10)
    h = datetime.datetime.today().hour
    if h > 16 or h < 3:
        result = result[1:]
    result = [res for res in result if res["date"] > latest[0]["date"]]
    ids = await (await self.db).insert_daily(fill_id(result, c_id))
    return ids


@celery_app.task(name="weekly_latest", base=PostgresTask, bind=True)
async def latest_retrieve_weekly(self, symbol: str, c_id: int):
    result = await av.get_weekly(symbol)
    latest = await (await self.db).get_weekly(symbol, 10)
    if datetime.date.today().weekday < 5:
        result = result[1:]
    result = [res for res in result if res["date"] > latest[0]["date"]]
    ids = await (await self.db).insert_weekly(fill_id(result, c_id))
    return ids


@celery_app.task(name="monthly_latest", base=PostgresTask, bind=True)
async def latest_retrieve_monthly(self, symbol: str, c_id: int):
    result = await av.get_monthly(symbol)
    latest = await (await self.db).get_monthly(symbol, 10)
    if result[0]["date"].month == datetime.date.today().month:
        result = result[1:]
    result = [res for res in result if res["date"] > latest[0]["date"]]
    ids = await (await self.db).insert_monthly(fill_id(result, c_id))
    return ids


@celery_app.task(name="balance_sheets_latest", base=MongoTask, bind=True)
async def latest_retrieve_balance_sheets(self, symbol: str, c_id: int):
    result = await fh.get_balance_sheets(symbol)
    latest = await (await self.db).get_balance_sheets(symbol)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    ids = None
    if len(result) != 0:
        ids = await (await self.db).insert_balance_sheets(fill_id(result, c_id))
        ids = [str(_id) for _id in ids.inserted_ids]
    return ids


@celery_app.task(name="cash_flows_latest", base=MongoTask, bind=True)
async def latest_retrieve_cash_flows(self, symbol: str, c_id: int):
    result = await fh.get_cash_flows(symbol)
    latest = await (await self.db).get_cash_flows(symbol)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    ids = None
    if len(result) != 0:
        ids = await (await self.db).insert_cash_flows(fill_id(result, c_id))
        ids = [str(_id) for _id in ids.inserted_ids]
    return ids


@celery_app.task(name="income_statements_latest", base=MongoTask, bind=True)
async def latest_retrieve_income_statements(self, symbol: str, c_id: int):
    result = await fh.get_income_statements(symbol)
    latest = await (await self.db).get_income_statements(symbol)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    ids = None
    if len(result) != 0:
        ids = await (await self.db).insert_income_statements(fill_id(result, c_id))
        ids = [str(_id) for _id in ids.inserted_ids]
    return ids


@celery_app.task(name="similarities_latest", base=PostgresTask, bind=True)
async def latest_retrieve_similarities(self, symbol: str, c_id: int):
    result = await fh.get_similarity_index(symbol)
    latest = await (await self.db).get_sec_similarities(symbol, 10)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    ids = await (await self.db).insert_sec_similarity(fill_id(result, c_id))
    return ids


@celery_app.task(name="sentiments_latest", base=PostgresTask, bind=True)
async def latest_retrieve_sentiments(self, symbol: str, c_id: int, startdate: str, enddate: str):
    result = await fh.get_sec_sentiments(await fh.get_filings(symbol, startdate, enddate))
    latest = await (await self.db).get_sec_sentiments(symbol, 10)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    ids = await (await self.db).insert_sec_sentiment(fill_id(result, c_id))
    return ids


@celery_app.task(name="dividents_latest", base=PostgresTask, bind=True)
async def latest_retrieve_dividents(self, symbol: str, c_id: int, startdate: str, enddate: str):
    result = await fh.get_dividends(symbol, startdate, enddate)
    latest = await (await self.db).get_dividends(symbol, 10)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    ids = await (await self.db).insert_dividends(fill_id(result, c_id))
    return ids


@celery_app.task(name="press_releases_latest", base=MongoTask, bind=True)
async def latest_retrieve_press_releases(self, symbol: str, c_id: int, startdate: str, enddate: str):
    result = await fh.get_press_releases(symbol, startdate, enddate)
    latest = await (await self.db).get_prs(symbol)
    result = [res for res in result if res["date"] > latest[0]["date"]]
    ids = None
    if len(result) != 0:
        ids = await (await self.db).insert_prs(fill_id(result, c_id))
        ids = [str(_id) for _id in ids.inserted_ids]
    return ids
