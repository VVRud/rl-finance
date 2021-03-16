CREATE TABLE "companies" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "name" varchar(128) NOT NULL,
  "symbol" varchar(8) NOT NULL,
  "state" varchar(128) NOT NULL,
  "country" varchar(128) NOT NULL,
  "city" varchar(128) NOT NULL,
  "address" varchar(128) NOT NULL,
  "exchange" varchar(32) NOT NULL,
  "ipo" timestamp NOT NULL,
  "share_outstanding" float(8) NOT NULL,
  "market_capitalization" float(8) NOT NULL,
  "employeeTotal" integer NOT NULL,
  "ggroup" varchar(128) NOT NULL,
  "gind" varchar(128) NOT NULL,
  "gsector" varchar(128) NOT NULL,
  "gsubind" varchar(128) NOT NULL,
  "naicsNationalIndustry" varchar(128) NOT NULL,
  "naics" varchar(128) NOT NULL,
  "naicsSector" varchar(128) NOT NULL,
  "naicsSubsector" varchar(128) NOT NULL,
  "description" text NOT NULL,
  "finnhubIndustry" varchar(128) NOT NULL
);

CREATE TABLE "sec_sentiment" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" timestamp NOT NULL,
  "form" varchar(8) NOT NULL,
  "access_number" varchar(32) NOT NULL,
  "negative" float(8) NOT NULL,
  "polarity" float(8) NOT NULL,
  "positive" float(8) NOT NULL,
  "litigious" float(8) NOT NULL,
  "modal_weak" float(8) NOT NULL,
  "uncertainty" float(8) NOT NULL,
  "constraining" float(8) NOT NULL,
  "modal_strong" float(8) NOT NULL,
  "modal_moderate" float(8) NOT NULL
);

CREATE TABLE "sec_similarity" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" timestamp NOT NULL,
  "form" varchar(8) NOT NULL,
  "access_number" varchar(32) NOT NULL,
  "item1" float(8) NOT NULL,
  "item2" float(8) NOT NULL,
  "item1A" float(8) NOT NULL,
  "item7" float(8) NOT NULL,
  "item7A" float(8) NOT NULL
);

CREATE TABLE "dividends" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" timestamp NOT NULL,
  "amount" float(8) NOT NULL,
  "adj_amount" float(8) NOT NULL
);

CREATE TABLE "stocks_candles" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" timestamp NOT NULL,
  "open" float(8) NOT NULL,
  "high" float(8) NOT NULL,
  "low" float(8) NOT NULL,
  "close" float(8) NOT NULL,
  "volume" bigint NOT NULL,
  "resolution" varchar(2) NOT NULL
);

CREATE TABLE "splits" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" timestamp NOT NULL,
  "fromFactor" float(8) NOT NULL,
  "toFactor" float(8) NOT NULL
);

CREATE TABLE "trends" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" timestamp NOT NULL,
  "buy" integer NOT NULL,
  "hold" integer NOT NULL,
  "sell" integer NOT NULL,
  "strongBuy" integer NOT NULL,
  "strongSell" integer NOT NULL
);

CREATE TABLE "eps_surprises" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" timestamp NOT NULL,
  "actual" float(8) NOT NULL,
  "estimate" float(8) NOT NULL
);

CREATE TABLE "eps_estimates" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" timestamp NOT NULL,
  "epsAvg" float(8) NOT NULL,
  "epsHigh" float(8) NOT NULL,
  "epsLow" float(8) NOT NULL,
  "numberAnalysts" integer NOT NULL,
  "freq" varchar(64) NOT NULL
);

CREATE TABLE "revenue_estimates" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" timestamp NOT NULL,
  "revenueAvg" bigint NOT NULL,
  "revenueHigh" bigint NOT NULL,
  "revenueLow" bigint NOT NULL,
  "numberAnalysts" integer NOT NULL,
  "freq" varchar(64) NOT NULL
);

CREATE TABLE "upgrades_downgrades" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" timestamp NOT NULL,
  "company" varchar(64) NOT NULL,
  "fromGrade" varchar(64) NOT NULL,
  "toGrade" varchar(64) NOT NULL,
  "action" varchar(64) NOT NULL
);

CREATE TABLE "earnings_calendars" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" timestamp NOT NULL,
  "epsActual" float(8) NOT NULL,
  "epsEstimate" float(8) NOT NULL,
  "hour" varchar(8) NOT NULL,
  "quarter" integer NOT NULL,
  "revenueActual" bigint NOT NULL,
  "revenueEstimate" bigint NOT NULL
);

CREATE TABLE "crypto" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "description" varchar(64) NOT NULL,
  "displaySymbol" varchar(64) NOT NULL,
  "symbol" varchar(64) NOT NULL
);

CREATE TABLE "crypto_candles" (
  "id" SERIAL UNIQUE PRIMARY KEY,
  "c_id" integer NOT NULL,
  "date" timestamp NOT NULL,
  "open" float(8) NOT NULL,
  "high" float(8) NOT NULL,
  "low" float(8) NOT NULL,
  "close" float(8) NOT NULL,
  "volume" bigint NOT NULL,
  "resolution" varchar(2) NOT NULL
);

ALTER TABLE "sec_sentiment" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "sec_similarity" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "dividends" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "stocks_candles" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "splits" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "trends" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "eps_surprises" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "eps_estimates" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "revenue_estimates" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "upgrades_downgrades" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "earnings_calendars" ADD FOREIGN KEY ("c_id") REFERENCES "companies" ("id");

ALTER TABLE "crypto_candles" ADD FOREIGN KEY ("c_id") REFERENCES "crypto" ("id");
