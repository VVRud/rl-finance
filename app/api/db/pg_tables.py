from sqlalchemy import (
    BigInteger, Column, DateTime, Float, ForeignKey, Index,
    Integer, MetaData, String, Table, Text, text
)

metadata = MetaData()


companies = Table(
    'companies', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('companies_id_seq'::regclass)")),
    Column('name', String(128), nullable=False),
    Column('symbol', String(8), nullable=False),
    Column('state', String(128), nullable=False),
    Column('country', String(128), nullable=False),
    Column('city', String(128), nullable=False),
    Column('address', String(128), nullable=False),
    Column('exchange', String(32), nullable=False),
    Column('ipo', DateTime, nullable=False),
    Column('share_outstanding', Float, nullable=False),
    Column('market_capitalization', Float, nullable=False),
    Column('employeeTotal', Integer, nullable=False),
    Column('ggroup', String(128), nullable=False),
    Column('gind', String(128), nullable=False),
    Column('gsector', String(128), nullable=False),
    Column('gsubind', String(128), nullable=False),
    Column('naicsNationalIndustry', String(128), nullable=False),
    Column('naics', String(128), nullable=False),
    Column('naicsSector', String(128), nullable=False),
    Column('naicsSubsector', String(128), nullable=False),
    Column('description', Text, nullable=False),
    Column('finnhubIndustry', String(128), nullable=False)
)


crypto = Table(
    'crypto', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('crypto_id_seq'::regclass)")),
    Column('description', String(64), nullable=False),
    Column('displaySymbol', String(64), nullable=False),
    Column('symbol', String(64), nullable=False)
)


crypto_candles = Table(
    'crypto_candles', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('crypto_candles_id_seq'::regclass)")),
    Column('c_id', ForeignKey('crypto.id'), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('open', Float, nullable=False),
    Column('high', Float, nullable=False),
    Column('low', Float, nullable=False),
    Column('close', Float, nullable=False),
    Column('volume', BigInteger, nullable=False),
    Column('resolution', String(2), nullable=False),
    Index('crypto_candles_c_id_date_resolution_idx', 'c_id', 'date', 'resolution', unique=True)
)


dividends = Table(
    'dividends', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('dividends_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('amount', Float, nullable=False),
    Column('adj_amount', Float, nullable=False),
    Index('dividends_c_id_date_idx', 'c_id', 'date', unique=True)
)


earnings_calendars = Table(
    'earnings_calendars', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('earnings_calendars_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('epsActual', Float, nullable=False),
    Column('epsEstimate', Float, nullable=False),
    Column('hour', String(8), nullable=False),
    Column('quarter', Integer, nullable=False),
    Column('revenueActual', BigInteger, nullable=False),
    Column('revenueEstimate', BigInteger, nullable=False),
    Index('earnings_calendars_c_id_date_idx', 'c_id', 'date', unique=True)
)


eps_estimates = Table(
    'eps_estimates', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('eps_estimates_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('epsAvg', Float, nullable=False),
    Column('epsHigh', Float, nullable=False),
    Column('epsLow', Float, nullable=False),
    Column('numberAnalysts', Integer, nullable=False),
    Column('freq', String(64), nullable=False),
    Index('eps_estimates_c_id_date_idx', 'c_id', 'date', unique=True)
)


eps_surprises = Table(
    'eps_surprises', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('eps_surprises_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('actual', Float, nullable=False),
    Column('estimate', Float, nullable=False),
    Index('eps_surprises_c_id_date_idx', 'c_id', 'date', unique=True)
)


revenue_estimates = Table(
    'revenue_estimates', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('revenue_estimates_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('revenueAvg', BigInteger, nullable=False),
    Column('revenueHigh', BigInteger, nullable=False),
    Column('revenueLow', BigInteger, nullable=False),
    Column('numberAnalysts', Integer, nullable=False),
    Column('freq', String(64), nullable=False),
    Index('revenue_estimates_c_id_date_idx', 'c_id', 'date', unique=True)
)


sec_sentiment = Table(
    'sec_sentiment', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('sec_sentiment_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('form', String(8), nullable=False),
    Column('access_number', String(32), nullable=False),
    Column('negative', Float, nullable=False),
    Column('polarity', Float, nullable=False),
    Column('positive', Float, nullable=False),
    Column('litigious', Float, nullable=False),
    Column('modal_weak', Float, nullable=False),
    Column('uncertainty', Float, nullable=False),
    Column('constraining', Float, nullable=False),
    Column('modal_strong', Float, nullable=False),
    Column('modal_moderate', Float, nullable=False),
    Index('sec_sentiment_c_id_date_form_access_number_idx', 'c_id', 'date', 'form', 'access_number', unique=True)
)


sec_similarity = Table(
    'sec_similarity', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('sec_similarity_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('form', String(8), nullable=False),
    Column('access_number', String(32), nullable=False),
    Column('item1', Float, nullable=False),
    Column('item2', Float, nullable=False),
    Column('item1A', Float, nullable=False),
    Column('item7', Float, nullable=False),
    Column('item7A', Float, nullable=False),
    Index('sec_similarity_c_id_date_form_access_number_idx', 'c_id', 'date', 'form', 'access_number', unique=True)
)


splits = Table(
    'splits', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('splits_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('fromFactor', Float, nullable=False),
    Column('toFactor', Float, nullable=False),
    Index('splits_c_id_date_idx', 'c_id', 'date', unique=True)
)


stocks_candles = Table(
    'stocks_candles', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('stocks_candles_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('open', Float, nullable=False),
    Column('high', Float, nullable=False),
    Column('low', Float, nullable=False),
    Column('close', Float, nullable=False),
    Column('volume', BigInteger, nullable=False),
    Column('resolution', String(2), nullable=False),
    Index('stocks_candles_c_id_date_resolution_idx', 'c_id', 'date', 'resolution', unique=True)
)


trends = Table(
    'trends', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('trends_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('buy', Integer, nullable=False),
    Column('hold', Integer, nullable=False),
    Column('sell', Integer, nullable=False),
    Column('strongBuy', Integer, nullable=False),
    Column('strongSell', Integer, nullable=False),
    Index('trends_c_id_date_idx', 'c_id', 'date', unique=True)
)


upgrades_downgrades = Table(
    'upgrades_downgrades', metadata,
    Column('id', Integer, primary_key=True, server_default=text("nextval('upgrades_downgrades_id_seq'::regclass)")),
    Column('c_id', ForeignKey('companies.id'), nullable=False),
    Column('date', DateTime, nullable=False),
    Column('company', String(64), nullable=False),
    Column('fromGrade', String(64), nullable=False),
    Column('toGrade', String(64), nullable=False),
    Column('action', String(64), nullable=False),
    Index('upgrades_downgrades_c_id_date_idx', 'c_id', 'date', unique=True)
)