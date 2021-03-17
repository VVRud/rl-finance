import inspect
from .postgres import PgCrud
from .mongo import MongoCrud

pg_db = PgCrud()
mongo_db = MongoCrud()

data_functions = dict([
    (k.replace("get_", ""), v)
    for k, v in inspect.getmembers(pg_db) + inspect.getmembers(mongo_db)
    if (
        k.startswith("get_") and
        len(inspect.signature(v).parameters) >= 2 and
        "limit" in inspect.signature(v).parameters
    )
])

data_parameters = dict([
    (k.replace("get_", ""), list(inspect.signature(v).parameters.keys()))
    for k, v in inspect.getmembers(pg_db) + inspect.getmembers(mongo_db)
    if (
        k.startswith("get_") and
        len(inspect.signature(v).parameters) >= 2 and
        "limit" in inspect.signature(v).parameters
    )
])
