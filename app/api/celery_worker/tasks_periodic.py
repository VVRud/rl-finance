from finances import fm
from db import mongo_db
from celery_worker.worker import celery_app
from celery_worker.db_tasks import PostgresTask


async def get_missed_ids() -> dict:
    results = []
    for c_type in fm.content_types:
        latest = [doc["_id"] for doc in await mongo_db.get_finimize_news(c_type, 20)]
        ids, cursors = await fm.get_ids(c_type)
        ids_next = ids.copy()
        mask = [_id not in latest for _id in ids_next]
        mask_next = mask.copy()
        while all(mask_next) and len(cursors) != 0:
            ids_next, cursors = await fm.get_ids(c_type, cursors[-1])
            mask_next = [_id not in latest for _id in ids_next]
            ids += ids_next
            mask += mask_next
        results += [_id for _id, masked in zip(ids, mask) if masked]
    return results


@celery_app.task(name="update_daily", base=PostgresTask, bind=True)
async def update_daily(self):
    ids = await get_missed_ids()
    for _id in ids:
        await celery_app.send_task("finimize_latest", args=(_id,))

    companies = await (await self.db).get_companies()
    for company in companies:
        await celery_app.send_task("company_news_latest", args=(company["symbol"], company["id"]))
        for resolution in ["1", "5", "15", "30", "60", "D"]:
            await celery_app.send_task("stock_candles_latest", args=(company["symbol"], company["id"], resolution))

    cryptos = await (await self.db).get_cryptos()
    for crypto in cryptos:
        for resolution in ["1", "5", "15", "30", "60", "D"]:
            await celery_app.send_task("crypto_candles_latest", args=(crypto["symbol"], crypto["id"], resolution))


@celery_app.task(name="update_weekly", base=PostgresTask, bind=True)
async def update_weekly(self):
    companies = await (await self.db).get_companies()
    for company in companies:
        await celery_app.send_task("stock_candles_latest", args=(company["symbol"], company["id"], "W"))

    cryptos = await (await self.db).get_cryptos()
    for crypto in cryptos:
        await celery_app.send_task("stock_candles_latest", args=(crypto["symbol"], crypto["id"], "W"))


@celery_app.task(name="update_monthly", base=PostgresTask, bind=True)
async def update_monthly(self):
    companies = await (await self.db).get_companies()
    for company in companies:
        await celery_app.send_task("stock_candles_latest", args=(company["symbol"], company["id"], "M"))
        await celery_app.send_task("sentiments_latest", args=(company["symbol"], company["id"]))
        await celery_app.send_task("dividends_latest", args=(company["symbol"], company["id"]))
        await celery_app.send_task("press_releases_latest", args=(company["symbol"], company["id"]))
        await celery_app.send_task("splits_latest", args=(company["symbol"], company["id"]))
        await celery_app.send_task("upgrades_downgrades_latest", args=(company["symbol"], company["id"]))
        await celery_app.send_task("balance_sheets_latest", args=(company["symbol"], company["id"]))
        await celery_app.send_task("cash_flows_latest", args=(company["symbol"], company["id"]))
        await celery_app.send_task("income_statements_latest", args=(company["symbol"], company["id"]))
        await celery_app.send_task("similarities_latest", args=(company["symbol"], company["id"]))
        await celery_app.send_task("trends_latest", args=(company["symbol"], company["id"]))
        await celery_app.send_task("eps_surprises_latest", args=(company["symbol"], company["id"]))
        await celery_app.send_task("eps_estimates_latest", args=(company["symbol"], company["id"]))
        await celery_app.send_task("revenue_estimates_latest", args=(company["symbol"], company["id"]))

    cryptos = await (await self.db).get_cryptos()
    for crypto in cryptos:
        await celery_app.send_task("stock_candles_latest", args=(crypto["symbol"], crypto["id"], "M"))
