import os
import datetime
from .throttler import Limit, Throttler


class FinnHub(Throttler):

    def __init__(self):
        self.url = "https://finnhub.io/api/v1"
        self.apikey = os.getenv("FH_APIKEY")
        if self.apikey is None:
            raise ValueError(
                "API key for FinnHub was not found."
                " Set it into `.env` file as `FH_APIKEY`."
            )

        self.resolutions = ["1", "5", "15", "30", "60", "D", "W", "M"]

        super(FinnHub, self).__init__([
            Limit(30, 1, 0.5, "fh:short"), Limit(150, 60, 5, "fh:long")
        ])

    # Fundamentals
    async def __get_financials(self, params):
        path = "/stock/financials"
        result = []
        for freq in ["annual", "quarterly"]:
            params["freq"] = freq
            async with await self.make_request("GET", self.url + path, params=params) as response:
                data = await response.json()
                for res in data["financials"]:
                    res["date"] = datetime.datetime.fromisoformat(res["period"])
                    res["period"] = freq
                    res["symbol"] = params["symbol"]
                result += data["financials"]
        return result

    async def get_profile(self, symbol: str) -> dict:
        path = "/stock/profile"
        params = {
            "symbol": symbol,
            "token": self.apikey
        }

        async with await self.make_request("GET", self.url + path, params=params) as response:
            data = await response.json()
            result = {
                "name": data["name"],
                "symbol": data["ticker"],

                "state": data["state"],
                "country": data["country"],
                "city": data["city"],
                "address": data["address"],

                "exchange": data["exchange"],
                "ipo": datetime.datetime.fromisoformat(data["ipo"]),
                "share_outstanding": data["shareOutstanding"],
                "market_capitalization": data["marketCapitalization"],
                "employeeTotal": int(float(data["employeeTotal"])),

                "ggroup": data["ggroup"],
                "gind": data["gind"],
                "gsector": data["gsector"],
                "gsubind": data["gsubind"],

                "naicsNationalIndustry": data["naicsNationalIndustry"],
                "naics": data["naics"],
                "naicsSector": data["naicsSector"],
                "naicsSubsector": data["naicsSubsector"],

                "description": data["description"],
                "finnhubIndustry": data["finnhubIndustry"]
            }

        return result

    async def get_press_releases(self, symbol: str, _from: datetime.datetime, _to: datetime.datetime) -> list:
        def cleanup_chunk(chunk):
            try:
                res = {
                    "symbol": chunk["symbol"],
                    "date": datetime.datetime.fromisoformat(chunk["datetime"]),
                    "headline": chunk["headline"],
                    "description": chunk["description"]
                }
            except ValueError:
                res = {
                    "symbol": chunk["symbol"],
                    "date": chunk["datetime"],
                    "headline": chunk["headline"],
                    "description": chunk["description"]
                }

            return res

        path = "/press-releases"
        params = {
            "symbol": symbol,
            "from": _from.date().isoformat(),
            "to": _to.date().isoformat(),
            "token": self.apikey
        }

        async with await self.make_request("GET", self.url + path, params=params) as response:
            data = await response.json()
            result = [cleanup_chunk(chunk) for chunk in data.get("majorDevelopment", [])]

        return result

    async def get_balance_sheets(self, symbol: str):
        params = {
            "symbol": symbol,
            "statement": "bs",
            "token": self.apikey
        }
        return await self.__get_financials(params)

    async def get_income_statements(self, symbol: str):
        params = {
            "symbol": symbol,
            "statement": "ic",
            "token": self.apikey
        }
        return await self.__get_financials(params)

    async def get_cash_flows(self, symbol: str):
        params = {
            "symbol": symbol,
            "statement": "cf",
            "token": self.apikey
        }
        return await self.__get_financials(params)

    async def get_filings(self, symbol: str, _from: datetime.datetime, _to: datetime.datetime) -> list:
        path = "/stock/filings"
        params = {
            "symbol": symbol,
            "from": _from.date().isoformat(),
            "to": _to.date().isoformat(),
            "token": self.apikey
        }
        filings = []
        for form in ["10-K", "10-Q"]:
            params["form"] = form
            async with await self.make_request("GET", self.url + path, params=params) as response:
                data = await response.json()
                filings += [{
                    "date": datetime.datetime.fromisoformat(chunk["acceptedDate"].split(" ")[0]),
                    "access_number": chunk["accessNumber"],
                    "form": chunk["form"]
                } for chunk in data]
        return filings

    async def get_sec_sentiments(self, filings: list) -> list:
        path = "/stock/filings-sentiment"
        params = {
            "token": self.apikey
        }
        result = []
        for i, filing in enumerate(filings):
            params["accessNumber"] = filing["access_number"]
            try:
                async with await self.make_request("GET", self.url + path, params=params) as response:
                    data = await response.json()
                    sentiments = dict((k.replace("-", "_"), v) for k, v in data.get("sentiment", {}).items())
                    result.append({**filings, **sentiments})
            except Exception:
                pass

        return result

    async def get_similarity_index(self, symbol: str) -> list:
        path = "/stock/similarity-index"
        params = {
            "symbol": symbol,
            "token": self.apikey
        }
        result = []
        for freq in ["annual", "quarterly"]:
            params["freq"] = freq
            async with await self.make_request("GET", self.url + path, params=params) as response:
                data = await response.json()
                result += [{
                    "date": datetime.datetime.fromisoformat(chunk["acceptedDate"].split(" ")[0]),
                    "form": chunk["form"],
                    "access_number": chunk["accessNumber"],
                    "item1": chunk["item1"],
                    "item2": chunk["item2"],
                    "item1A": chunk["Item1A"],
                    "item7": chunk["item7"],
                    "item7A": chunk["Item7A"]
                } for chunk in data.get("similarity", [])]
        return result

    async def get_dividends(self, symbol: str, _from: datetime.datetime, _to: datetime.datetime) -> list:
        path = "/stock/dividend"
        params = {
            "symbol": symbol,
            "from": _from.date().isoformat(),
            "to": _to.date().isoformat(),
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            data = await response.json()
            result = [{
                "date": datetime.datetime.fromisoformat(chunk["date"]),
                "amount": chunk["amount"],
                "adj_amount": chunk["adjustedAmount"]
            } for chunk in data]
        return result

    async def get_available_stocks(self, exchange: str = "US", currency: str = "USD"):
        path = "/stock/symbol"
        params = {
            "exchange": exchange,
            "currency": currency,
            "token": self.apikey
        }

        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        return result

    async def stocks_symbol_lookup(self, query: str):
        path = "/search"
        params = {
            "q": query,
            "token": self.apikey
        }

        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()["result"]
        return result

    # Stocks
    async def get_stock_candles(self, symbol: str, resolution: str, _from: datetime.datetime, _to: datetime.datetime):
        path = "/stock/candle"
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": int(_from.timestamp()),
            "to": int(_to.timestamp()),
            "format": "json",
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        if result["s"] == "ok" and result["t"] is not None:
            result = [
                {
                    "date": datetime.datetime.fromtimestamp(result["t"][i]),
                    "open": result["o"][i],
                    "high": result["h"][i],
                    "low": result["l"][i],
                    "close": result["c"][i],
                    "volume": result["v"][i],
                    "resolution": resolution
                }
                for i in range(len(result["t"]))
            ]
            return result
        return []

    async def get_stock_candle_latest(self, symbol: str):
        path = "/quote"
        params = {
            "symbol": symbol,
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        return {
            "open": result["o"],
            "close": result["c"],
            "high": result["h"],
            "low": result["l"]
        }

    async def get_tickers(self, symbol: str, date: datetime.datetime, limit: int, skip: int):
        # path = "/stock/tick"
        # params = {
        #     "symbol": symbol,
        #     "date": date.isoformat(),
        #     "limit": limit,
        #     "skip": skip,
        #     "format": "csv",
        #     "token": self.apikey
        # }
        raise NotImplementedError()

    async def get_latest_bid_ask(self, symbol: str):
        path = "/stock/bidask"
        params = {
            "symbol": symbol,
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        return {
            "date": datetime.datetime.fromtimestamp(result["t"]),
            "ask": result["a"],
            "bid": result["b"],
            "ask_volume": result["av"],
            "bid_volume": result["bv"]
        }

    async def get_splits(self, symbol: str, _from: datetime.datetime, _to: datetime.datetime):
        path = "/stock/split"
        params = {
            "symbol": symbol,
            "from": _from.date().isoformat(),
            "to": _to.date().isoformat(),
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        for res in result:
            res["date"] = datetime.datetime.fromisoformat(res["date"])
            res["fromFactor"] = float(res["fromFactor"])
            res["toFactor"] = float(res["toFactor"])
            del res["symbol"]
        return result

    # Estimates
    async def get_trends(self, symbol: str):
        path = "/stock/recommendation"
        params = {
            "symbol": symbol,
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        for res in result:
            res["date"] = datetime.datetime.fromisoformat(res["period"])
            del res["period"]
            del res["symbol"]
        return result

    async def get_target_price(self, symbol: str):
        path = "/stock/price-target"
        params = {
            "symbol": symbol,
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        result["date"] = datetime.datetime.fromisoformat(result["lastUpdated"])
        del result["lastUpdated"]
        del result["symbol"]
        return result

    async def get_eps_surprises(self, symbol: str):
        path = "/stock/earnings"
        params = {
            "symbol": symbol,
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        for res in result:
            res["date"] = datetime.datetime.fromisoformat(res["period"])
            del res["period"]
            del res["symbol"]
        return result

    async def get_eps_estimates(self, symbol: str):
        path = "/stock/eps-estimate"
        params = {
            "symbol": symbol,
            "token": self.apikey
        }
        data = []
        for freq in ["annual", "quarterly"]:
            params["freq"] = freq
            async with await self.make_request("GET", self.url + path, params=params) as response:
                result = await response.json()
            for res in result["data"]:
                res["date"] = datetime.datetime.fromisoformat(res["period"])
                del res["period"]
            data += [{**d, "freq": freq} for d in result["data"]]

        return data

    async def get_revenue_estimates(self, symbol: str):
        path = "/stock/revenue-estimate"
        params = {
            "symbol": symbol,
            "token": self.apikey
        }
        data = []
        for freq in ["annual", "quarterly"]:
            params["freq"] = freq
            async with await self.make_request("GET", self.url + path, params=params) as response:
                result = await response.json()
            for res in result["data"]:
                res["date"] = datetime.datetime.fromisoformat(res["period"])
                del res["period"]
            data += [{**d, "freq": freq} for d in result["data"]]

        return data

    async def get_upgrades_downgrades(
        self, symbol: str = None,
        _from: datetime.datetime = None, _to: datetime.datetime = None
    ):
        path = "/stock/upgrade-downgrade"
        params = {
            "token": self.apikey
        }
        if symbol is not None:
            params["symbol"] = symbol
        if _from is not None:
            params["from"] = _from.date().isoformat()
        if _to is not None:
            params["to"] = _to.date().isoformat()
        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        for res in result:
            res["date"] = datetime.datetime.fromtimestamp(res["gradeTime"])
            del res["gradeTime"]
            del res["symbol"]
        return result

    async def get_earnings_calendars(self, symbol: str, _from: datetime.datetime, _to: datetime.datetime):
        path = "/calendar/earnings"
        params = {
            "symbol": symbol,
            "from": _from.date().isoformat(),
            "to": _to.date().isoformat(),
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = (await response.json())["earningsCalendar"]
        for res in result:
            res["date"] = datetime.datetime.fromisoformat(res["date"])
            del res["symbol"]
            del res["year"]
        return result

    # Crypto
    async def get_crypto_exchanges(self):
        path = "/crypto/exchange"
        params = {
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        return result

    async def get_crypto_symbols(self, exchange: str):
        path = "/crypto/symbol"
        params = {
            "exchange": exchange,
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        return result

    async def get_crypto_candles(self, symbol: str, resolution: str, _from: datetime.datetime, _to: datetime.datetime):
        path = "/crypto/candle"
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": int(_from.timestamp()),
            "to": int(_to.timestamp()),
            "format": "json",
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        if result["s"] == "ok" and result["t"] is not None:
            result = [
                {
                    "date": datetime.datetime.fromtimestamp(result["t"][i]),
                    "open": result["o"][i],
                    "close": result["c"][i],
                    "high": result["h"][i],
                    "low": result["l"][i],
                    "volume": result["v"][i],
                    "resolution": resolution
                }
                for i in range(len(result["t"]))
            ]
            return result
        return []
