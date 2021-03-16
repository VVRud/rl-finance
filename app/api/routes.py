from fastapi import APIRouter, Query, BackgroundTasks

from models import StatusModel
from db import pg_db, mongo_db
from finances import fh, fm

from background_tasks import add_company_tasks, add_crypto_tasks

router = APIRouter()


@router.get(
    "/status", response_model=StatusModel,
    summary="Status of the API.",
    description="Allows you to get the status of all running services into this API."
)
async def status():
    return {
        "postgres": pg_db.get_status(),
        "mongo": mongo_db.get_status(),
        "finnhub": fh.get_status(),
        "finimize": fm.get_status()
    }


@router.get(
    "/add_stock_symbol",
    summary="Add stocks symbol to the database.",
    description="Adds symbol to the database and collects info (in background)"
)
async def add_stock_symbol(
    background_tasks: BackgroundTasks,
    symbol: str = Query(
        ..., title="Symbol of the company",
        description="Symbol to be added to the database."
    )
):
    profile = await fh.get_profile(symbol)
    if profile["symbol"] == symbol:
        background_tasks.add_task(add_company_tasks, symbol=symbol, profile=profile)
        return profile
    else:
        return {"error": True}


@router.get(
    "/add_crypto_symbol",
    summary="Add crypto symbol to the database.",
    description="Adds symbol to the database and collects info (in background)"
)
async def add_crypto_symbol(
    background_tasks: BackgroundTasks,
    symbol: str = Query(
        ..., title="Symbol of the cryptocurrency",
        description="Symbol to be added to the database."
    )
):
    profiles = await fh.get_crypto_symbols(symbol.split(":")[0])
    for profile in profiles:
        if profile["symbol"] == symbol:
            background_tasks.add_task(add_crypto_tasks, symbol=symbol, profile=profile)
            return profile
    return {"error": True}


# @router.get(
#     "/lookup",
#     summary="Add symbol to the API.",
#     description="Adds symbol to the database and collects info (in background)"
# )
# async def lookup(
#     background_tasks: BackgroundTasks,
#     symbol: str = Query(
#         ..., title="Symbol of the company",
#         description="Symbol to be added to the database."
#     )
# ):
#     profile = await fh.get_profile(symbol)
#     if profile["symbol"] == symbol:
#         background_tasks.add_task(retrieve_symbol_data, symbol=symbol, profile=profile)
#         return profile
#     else:
#         return {"error": True}


# @router.get(
#     "/get_monthly",
#     summary="Get symbol monthly"
# )
# async def get_monthly(
#     background_tasks: BackgroundTasks,
#     symbol: str = Query(
#         ..., title="Symbol of the company",
#         description="Symbol to be added to the database."
#     )
# ):
#     profile = await av.get_monthly(symbol)
#     return profile


@router.get(
    "/get_companies",
    summary="Get all the companies added to Database."
)
async def get_companies():
    return await pg_db.get_companies()


@router.get(
    "/get_cryptos",
    summary="Get all the cryptocurrencies added to Database."
)
async def get_cryptos():
    return await pg_db.get_cryptos()


# @router.get("/get_symbol_info/{symbol}")
# async def get_symbol_info(symbol: str):
#     pass
