CREATE TABLE "companies" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "symbol" varchar(8) UNIQUE NOT NULL,
  "country" varchar(64) NOT NULL,
  "exchange" varchar(64) NOT NULL,
  "ipo" date NOT NULL,
  "share_outstanding" float8 NOT NULL,
  "market_capitalization" float8 NOT NULL,
  "industry" varchar(64) NOT NULL
);

CREATE TABLE "sec_sentiment" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" date NOT NULL,
  "form" varchar(8) NOT NULL,
  "access_number" varchar(32) NOT NULL,
  "negative" float8 NOT NULL,
  "polarity" float8 NOT NULL,
  "positive" float8 NOT NULL,
  "litigious" float8 NOT NULL,
  "modal_weak" float8 NOT NULL,
  "uncertainty" float8 NOT NULL,
  "constraining" float8 NOT NULL,
  "modal_strong" float8 NOT NULL,
  "modal_moderate" float8 NOT NULL
);

CREATE TABLE "sec_similarity" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" date NOT NULL,
  "form" varchar(8) NOT NULL,
  "access_number" varchar(32) NOT NULL,
  "item1" float8 NOT NULL,
  "item2" float8 NOT NULL,
  "item1A" float8 NOT NULL,
  "item7" float8 NOT NULL,
  "item7A" float8 NOT NULL
);

CREATE TABLE "dividends" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" date NOT NULL,
  "amount" float8 NOT NULL,
  "adj_amount" float8 NOT NULL
);

CREATE TABLE "intraday_prices_1min" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date_time" timestamp NOT NULL,
  "open" float8 NOT NULL,
  "high" float8 NOT NULL,
  "low" float8 NOT NULL,
  "close" float8 NOT NULL,
  "volume" integer NOT NULL
);

CREATE TABLE "intraday_prices_5min" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date_time" timestamp NOT NULL,
  "open" float8 NOT NULL,
  "high" float8 NOT NULL,
  "low" float8 NOT NULL,
  "close" float8 NOT NULL,
  "volume" integer NOT NULL
);

CREATE TABLE "intraday_prices_15min" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date_time" timestamp NOT NULL,
  "open" float8 NOT NULL,
  "high" float8 NOT NULL,
  "low" float8 NOT NULL,
  "close" float8 NOT NULL,
  "volume" integer NOT NULL
);

CREATE TABLE "intraday_prices_30min" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date_time" timestamp NOT NULL,
  "open" float8 NOT NULL,
  "high" float8 NOT NULL,
  "low" float8 NOT NULL,
  "close" float8 NOT NULL,
  "volume" integer NOT NULL
);

CREATE TABLE "intraday_prices_60min" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date_time" timestamp NOT NULL,
  "open" float8 NOT NULL,
  "high" float8 NOT NULL,
  "low" float8 NOT NULL,
  "close" float8 NOT NULL,
  "volume" integer NOT NULL
);

CREATE TABLE "daily_prices" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" date NOT NULL,
  "open" float8 NOT NULL,
  "high" float8 NOT NULL,
  "low" float8 NOT NULL,
  "close" float8 NOT NULL,
  "adj_close" float8 NOT NULL,
  "volume" integer NOT NULL,
  "split_coefficient" float8 NOT NULL
);

CREATE TABLE "weekly_prices" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" date NOT NULL,
  "open" float8 NOT NULL,
  "high" float8 NOT NULL,
  "low" float8 NOT NULL,
  "close" float8 NOT NULL,
  "adj_close" float8 NOT NULL,
  "volume" bigint NOT NULL
);

CREATE TABLE "monthly_prices" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" date NOT NULL,
  "open" float8 NOT NULL,
  "high" float8 NOT NULL,
  "low" float8 NOT NULL,
  "close" float8 NOT NULL,
  "adj_close" float8 NOT NULL,
  "volume" bigint NOT NULL
);

ALTER TABLE "sec_sentiment" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "sec_similarity" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "dividends" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "intraday_prices_1min" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "intraday_prices_5min" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "intraday_prices_15min" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "intraday_prices_30min" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "intraday_prices_60min" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "daily_prices" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "weekly_prices" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "monthly_prices" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");
