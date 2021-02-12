import datetime
import dateutil.relativedelta
from finances import av, fm
from db import mongo_db
from celery_worker.worker import celery_app
from celery_worker.db_tasks import PostgresTask


funcs = {
    "INSIGHT": {
        "insert": mongo_db.insert_insights,
        "get": mongo_db.get_insights
    },
    "DAILY_BRIEF": {
        "insert": mongo_db.insert_briefs,
        "get": mongo_db.get_briefs
    },
    "OTHER": {
        "insert": mongo_db.insert_other,
        "get": mongo_db.get_other
    }
}


async def get_missed_ids() -> dict:
    results = dict()
    for c_type, crud in funcs.items():
        latest = [doc["_id"] for doc in await crud["get"](c_type)]
        _, ids, cursors = await fm.get_ids(c_type)
        ids_next = ids.copy()
        while not any(_id in ids_next for _id in latest) and len(cursors) != 0:
            _, ids_next, cursors = await fm.get_ids(c_type, cursors[-1])
            ids += ids_next
        results[c_type] = ids
    return results


async def get_documents(content_ids: dict) -> dict:
    results = dict()
    for name, ids in content_ids.items():
        results[name] = [await fm.get_single(_id) for _id in ids]
    return results


@celery_app.task(name="update_daily", base=PostgresTask, bind=True)
async def update_daily(self):
    for name, documents in await get_documents(await get_missed_ids()):
        await funcs[name]["insert"](documents)

    companies = await (await self.db).get_companies()
    for company in companies:
        for interval in av.intervals:
            celery_app.send_task("intraday_latest", args=(company["symbol"], interval, company["id"]))
        celery_app.send_task("daily_latest", args=(company["symbol"], company["id"]))


@celery_app.task(name="update_weekly", base=PostgresTask, bind=True)
async def update_weekly(self):
    companies = await (await self.db).get_companies()
    for company in companies:
        celery_app.send_task("weekly_latest", args=(company["symbol"], company["id"]))


@celery_app.task(name="update_monthly", base=PostgresTask, bind=True)
async def update_monthly(self):
    enddate = datetime.date.today()
    startdate = datetime.date.today() - dateutil.relativedelta.relativedelta(months=3)
    companies = await (await self.db).get_companies()
    for company in companies:
        celery_app.send_task("monthly_latest", args=(company["symbol"], company["id"]))
        celery_app.send_task("balance_sheets_latest", args=(company["symbol"], company["id"]))
        celery_app.send_task("cash_flows_latest", args=(company["symbol"], company["id"]))
        celery_app.send_task("income_statements_latest", args=(company["symbol"], company["id"]))
        celery_app.send_task("similarities_latest", args=(company["symbol"], company["id"]))
        celery_app.send_task(
            "sentiments_latest",
            args=(company["symbol"], company["id"], startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))
        )
        celery_app.send_task(
            "dividents_latest",
            args=(company["symbol"], company["id"], startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))
        )
        celery_app.send_task(
            "press_releases_latest",
            args=(company["symbol"], company["id"], startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))
        )
