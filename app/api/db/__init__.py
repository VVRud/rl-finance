from .postgres import PgCrud
from .mongo import MongoCrud

pg_db = PgCrud()
mongo_db = MongoCrud()
