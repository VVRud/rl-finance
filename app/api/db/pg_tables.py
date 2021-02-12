from sqlalchemy import (
    Column, Date, DateTime, Float, ForeignKey, Integer,
    BigInteger, MetaData, String, Table, text
)

metadata = MetaData()


companies = Table(
    'companies', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('companies_id_seq'::regclass)")),
    Column('symbol', String(8), nullable=False, unique=True),
    Column('country', String(64), nullable=False),
    Column('exchange', String(64), nullable=False),
    Column('ipo', Date, nullable=False),
    Column('share_outstanding', Float(53), nullable=False),
    Column('market_capitalization', Float(53), nullable=False),
    Column('industry', String(64), nullable=False)
)


daily_prices = Table(
    'daily_prices', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('daily_prices_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', Date, nullable=False),
    Column('open', Float(53), nullable=False),
    Column('high', Float(53), nullable=False),
    Column('low', Float(53), nullable=False),
    Column('close', Float(53), nullable=False),
    Column('adj_close', Float(53), nullable=False),
    Column('volume', Integer, nullable=False),
    Column('split_coefficient', Float(53), nullable=False)
)


dividends = Table(
    'dividends', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('dividends_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', Date, nullable=False),
    Column('amount', Float(53), nullable=False),
    Column('adj_amount', Float(53), nullable=False)
)


intraday_prices_15min = Table(
    'intraday_prices_15min', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('intraday_prices_15min_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date_time', DateTime, nullable=False),
    Column('open', Float(53), nullable=False),
    Column('high', Float(53), nullable=False),
    Column('low', Float(53), nullable=False),
    Column('close', Float(53), nullable=False),
    Column('volume', Integer, nullable=False)
)


intraday_prices_1min = Table(
    'intraday_prices_1min', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('intraday_prices_1min_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date_time', DateTime, nullable=False),
    Column('open', Float(53), nullable=False),
    Column('high', Float(53), nullable=False),
    Column('low', Float(53), nullable=False),
    Column('close', Float(53), nullable=False),
    Column('volume', Integer, nullable=False)
)


intraday_prices_30min = Table(
    'intraday_prices_30min', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('intraday_prices_30min_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date_time', DateTime, nullable=False),
    Column('open', Float(53), nullable=False),
    Column('high', Float(53), nullable=False),
    Column('low', Float(53), nullable=False),
    Column('close', Float(53), nullable=False),
    Column('volume', Integer, nullable=False)
)


intraday_prices_5min = Table(
    'intraday_prices_5min', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('intraday_prices_5min_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date_time', DateTime, nullable=False),
    Column('open', Float(53), nullable=False),
    Column('high', Float(53), nullable=False),
    Column('low', Float(53), nullable=False),
    Column('close', Float(53), nullable=False),
    Column('volume', Integer, nullable=False)
)


intraday_prices_60min = Table(
    'intraday_prices_60min', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('intraday_prices_60min_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date_time', DateTime, nullable=False),
    Column('open', Float(53), nullable=False),
    Column('high', Float(53), nullable=False),
    Column('low', Float(53), nullable=False),
    Column('close', Float(53), nullable=False),
    Column('volume', Integer, nullable=False)
)


monthly_prices = Table(
    'monthly_prices', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('monthly_prices_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', Date, nullable=False),
    Column('open', Float(53), nullable=False),
    Column('high', Float(53), nullable=False),
    Column('low', Float(53), nullable=False),
    Column('close', Float(53), nullable=False),
    Column('adj_close', Float(53), nullable=False),
    Column('volume', BigInteger, nullable=False)
)


sec_sentiment = Table(
    'sec_sentiment', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('sec_sentiment_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', Date, nullable=False),
    Column('form', String(8), nullable=False),
    Column('access_number', String(32), nullable=False),
    Column('negative', Float(53), nullable=False),
    Column('polarity', Float(53), nullable=False),
    Column('positive', Float(53), nullable=False),
    Column('litigious', Float(53), nullable=False),
    Column('modal_weak', Float(53), nullable=False),
    Column('uncertainty', Float(53), nullable=False),
    Column('constraining', Float(53), nullable=False),
    Column('modal_strong', Float(53), nullable=False),
    Column('modal_moderate', Float(53), nullable=False)
)


sec_similarity = Table(
    'sec_similarity', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('sec_similarity_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', Date, nullable=False),
    Column('form', String(8), nullable=False),
    Column('access_number', String(32), nullable=False),
    Column('item1', Float(53), nullable=False),
    Column('item2', Float(53), nullable=False),
    Column('item1A', Float(53), nullable=False),
    Column('item7', Float(53), nullable=False),
    Column('item7A', Float(53), nullable=False)
)


weekly_prices = Table(
    'weekly_prices', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('weekly_prices_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', Date, nullable=False),
    Column('open', Float(53), nullable=False),
    Column('high', Float(53), nullable=False),
    Column('low', Float(53), nullable=False),
    Column('close', Float(53), nullable=False),
    Column('adj_close', Float(53), nullable=False),
    Column('volume', BigInteger, nullable=False)
)
