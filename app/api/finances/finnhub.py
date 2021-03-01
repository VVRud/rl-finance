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

        super(FinnHub, self).__init__([
            Limit(30, 1, 0.1, "fh:short"), Limit(60, 60, 1, "fh:long")
        ])

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
        path = "/stock/profile2"
        params = {
            "symbol": symbol,
            "token": self.apikey
        }

        async with await self.make_request("GET", self.url + path, params=params) as response:
            data = await response.json()
            result = {
                "symbol": data["ticker"],
                "country": data["country"],
                "exchange": data["exchange"],
                "ipo": datetime.date.fromisoformat(data["ipo"]),
                "share_outstanding": data["shareOutstanding"],
                "market_capitalization": data["marketCapitalization"],
                "industry": data["finnhubIndustry"]
            }

        return result

    async def get_press_releases(self, symbol: str, _from: str, _to: str) -> list:
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
            "from": _from,
            "to": _to,
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

    async def get_filings(self, symbol: str, _from: str, _to: str) -> list:
        path = "/stock/filings"
        params = {
            "symbol": symbol,
            "from": _from,
            "to": _to,
            "token": self.apikey
        }
        filings = []
        for form in ["10-K", "10-Q"]:
            params["form"] = form
            async with await self.make_request("GET", self.url + path, params=params) as response:
                data = await response.json()
                filings += [{
                    "date": datetime.date.fromisoformat(chunk["acceptedDate"].split(" ")[0]),
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
                    "date": datetime.date.fromisoformat(chunk["acceptedDate"].split(" ")[0]),
                    "form": chunk["form"],
                    "access_number": chunk["accessNumber"],
                    "item1": chunk["item1"],
                    "item2": chunk["item2"],
                    "item1A": chunk["Item1A"],
                    "item7": chunk["item7"],
                    "item7A": chunk["Item7A"]
                } for chunk in data.get("similarity", [])]
        return result

    async def get_dividends(self, symbol: str, _from: str, _to: str) -> list:
        path = "/stock/dividend"
        params = {
            "symbol": symbol,
            "from": _from,
            "to": _to,
            "token": self.apikey
        }
        async with await self.make_request("GET", self.url + path, params=params) as response:
            data = await response.json()
            result = [{
                "date": datetime.date.fromisoformat(chunk["date"]),
                "amount": chunk["amount"],
                "adj_amount": chunk["adjustedAmount"]
            } for chunk in data]
        return result

    async def get_available_stocks(self, exchange: str = "US", currency: str = "USD"):
        path = "/stock/symbol"
        params = {
            "exchange": exchange,
            "currency": currency
        }

        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()
        return result

    async def lookup(self, query: str):
        path = "/search"
        params = {
            "q": query
        }

        async with await self.make_request("GET", self.url + path, params=params) as response:
            result = await response.json()["result"]
        return result
