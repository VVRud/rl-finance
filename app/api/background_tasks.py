import datetime
import dateutil.relativedelta
from celery_worker.worker import celery_app
from finances import av
from db import pg_db


async def add_tasks(symbol: str, profile: dict):
    companies = await pg_db.get_companies()
    if symbol not in [company["symbol"] for company in companies]:
        c_id = await pg_db.insert_company(profile)
        for interval in av.intervals:
            for time_slice in av.time_slices:
                celery_app.send_task("intraday_full", args=(symbol, interval, time_slice, c_id))

        celery_app.send_task("daily_full", args=(symbol, c_id))
        celery_app.send_task("weekly_full", args=(symbol, c_id))
        celery_app.send_task("monthly_full", args=(symbol, c_id))
        celery_app.send_task("balance_sheets_full", args=(symbol, c_id))
        celery_app.send_task("cash_flows_full", args=(symbol, c_id))
        celery_app.send_task("income_statements_full", args=(symbol, c_id))
        celery_app.send_task("similarities_full", args=(symbol, c_id))

        today = datetime.date.today()
        enddate = datetime.date(
            year=today.year, month=today.month + 1, day=1
        ) - datetime.timedelta(days=1)
        startdate = enddate - dateutil.relativedelta.relativedelta(months=3)
        for _ in range(4 * 3):
            celery_app.send_task(
                "sentiments_full",
                args=(symbol, c_id, startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))
            )
            celery_app.send_task(
                "dividents_full",
                args=(symbol, c_id, startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))
            )
            celery_app.send_task(
                "press_releases_full",
                args=(symbol, c_id, startdate.strftime("%Y-%m-%d"), enddate.strftime("%Y-%m-%d"))
            )
            enddate = enddate - dateutil.relativedelta.relativedelta(months=3)
            startdate = startdate - dateutil.relativedelta.relativedelta(months=3)
    else:
        company = await pg_db.get_company(symbol)
        for interval in av.intervals:
            celery_app.send_task("intraday_latest", args=(company["symbol"], interval, company["id"]))

        celery_app.send_task("daily_latest", args=(company["symbol"], company["id"]))
        celery_app.send_task("weekly_latest", args=(company["symbol"], company["id"]))
        celery_app.send_task("monthly_latest", args=(company["symbol"], company["id"]))
        celery_app.send_task("balance_sheets_latest", args=(company["symbol"], company["id"]))
        celery_app.send_task("cash_flows_latest", args=(company["symbol"], company["id"]))
        celery_app.send_task("income_statements_latest", args=(company["symbol"], company["id"]))
        celery_app.send_task("similarities_latest", args=(company["symbol"], company["id"]))

        enddate = datetime.date.today()
        startdate = datetime.date.today() - dateutil.relativedelta.relativedelta(months=3)
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
