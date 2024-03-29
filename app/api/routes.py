from typing import Optional
from fastapi import APIRouter, Query, Path, BackgroundTasks, Response, status

from models import StatusModel
from db import pg_db, mongo_db, data_functions, data_parameters
from finances import fh, fm
from celery_worker.worker import celery_app

from background_tasks import add_crypto_tasks

router = APIRouter()


@router.get(
    "/status", response_model=StatusModel,
    summary="Status of the API.",
    description="Allows you to get the status of all running services into this API.",
    tags=["status"]
)
async def get_status():
    return {
        "postgres": pg_db.get_status(),
        "mongo": mongo_db.get_status(),
        "finnhub": fh.get_status(),
        "finimize": fm.get_status()
    }


@router.get(
    "/add_stock_symbol",
    summary="Add stocks symbol to the database.",
    description="Adds symbol to the database and collects info (in background)",
    tags=["companies"]
)
async def add_stock_symbol(
    background_tasks: BackgroundTasks,
    response: Response,
    symbol: str = Query(..., title="Symbol of the company", description="Symbol to be added to the database.")
):
    profile = await pg_db.get_company(symbol)
    if profile is not None:
        return profile

    profile = await fh.get_profile(symbol)
    if profile is not None:
        c_id = await pg_db.insert_company(profile)
        celery_app.send_task("add_company_parsing_tasks", args=(symbol, c_id, profile["ipo"]), priority=9)
        return profile

    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": "Company not found."}


@router.get(
    "/get_company",
    summary="Get single company profile.",
    tags=["companies"]
)
async def get_company(
    symbol: str = Query(
        ..., title="Symbol of the company",
        description="Symbol to get profile of."
    )
):
    return await pg_db.get_company(symbol)


@router.get(
    "/get_companies",
    summary="Get all the companies added to Database.",
    tags=["companies"]
)
async def get_companies():
    return await pg_db.get_companies()


@router.get(
    "/lookup_stocks",
    summary="Search stocks",
    description="Search available stocks symbols by query",
    tags=["companies"]
)
async def lookup_stocks(
    query: str = Query(..., title="Query", description="Query to look for.")
):
    return await fh.stocks_symbol_lookup(query)


@router.get(
    "/add_crypto_symbol",
    summary="Add crypto symbol to the database.",
    description="Adds symbol to the database and collects info (in background)",
    tags=["cryptos"]
)
async def add_crypto_symbol(
    background_tasks: BackgroundTasks,
    response: Response,
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
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"error": "Profile not found"}


@router.get(
    "/get_crypto",
    summary="Get single cpypto profile.",
    tags=["cryptos"]
)
async def get_crypto(
    symbol: str = Query(
        ..., title="Symbol of the cryptocurrency",
        description="Symbol to get profile of."
    )
):
    return await pg_db.get_crypto(symbol)


@router.get(
    "/get_cryptos",
    summary="Get all the cryptocurrencies added to Database.",
    tags=["cryptos"]
)
async def get_cryptos():
    return await pg_db.get_cryptos()


@router.get(
    "/lookup_crypto_exchanges",
    summary="Search crypto exchanges",
    description="Search available crypto exchanges",
    tags=["cryptos"]
)
async def lookup_crypto_exchanges():
    return await fh.get_crypto_exchanges()


@router.get(
    "/lookup_crypto_symbols",
    summary="Search crypto symbols",
    description="Search available crypto symbols by exchange",
    tags=["cryptos"]
)
async def lookup_crypto_symbols(
    exchange: str = Query(..., title="Exchnage", description="Exchange to look on.")
):
    return await fh.get_crypto_symbols(exchange)


@router.get(
    "/get_data_parameters",
    summary="Get parameters",
    description="Get parameters of data retrieve functions",
    tags=["data"]
)
def get_data_parameters():
    return data_parameters


@router.get(
    "/get_data/{function}",
    summary="Get data",
    description="Get data from database",
    tags=["data"]
)
async def get_data(
    response: Response,
    function: str = Path(..., title="Function", decription="Function name to call and data name to get."),
    symbol: Optional[str] = Query(None, title="Symbol", description="Symbol to retrieve data for."),
    resolution: Optional[str] = Query(None, title="Resolution", description="Resolution for candles."),
    content_type: Optional[str] = Query(None, title="Resolution", description="Content type for Finimize News."),
    limit: int = Query(100, title="Limit", description="Limit for response."),
    offset: int = Query(0, title="Offset", description="Offset for response.")
):
    parameters = {
        "limit": limit,
        "offset": offset
    }

    if symbol:
        parameters["symbol"] = symbol
    if resolution:
        parameters["resolution"] = resolution
    if content_type:
        parameters["content_type"] = content_type

    if function not in data_parameters:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"Function `{function}` not found."}

    missed_parameters = set(data_parameters[function]) - set(parameters)
    if len(missed_parameters) != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Not all parameters are included. Missed are {list(missed_parameters)}"}

    excess_parameters = set(parameters) - set(data_parameters[function])
    if len(excess_parameters) != 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"More than need parameters are included. Excess are {list(excess_parameters)}"}

    if "symbol" in data_parameters[function]:
        company = await pg_db.get_company(symbol)
        if company is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": f"Company {symbol} not found."}

    if "resolution" in data_parameters[function] and resolution not in fh.resolutions:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Wrong `resolution` parameter. Available are: {fh.resolutions}."}

    if "content_type" in data_parameters[function] and content_type not in fm.content_types:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Wrong `content_type` parameter. Available are: {fm.content_types}."}

    return await data_functions[function](**parameters)
