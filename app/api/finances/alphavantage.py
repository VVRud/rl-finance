import os
import datetime
from itertools import product
from .throttler import Limit, Throttler


class AlphaVantage(Throttler):

    def __init__(self):
        self.url = "https://www.alphavantage.co/query"
        self.apikey = os.getenv("AV_APIKEY")
        if self.apikey is None:
            raise ValueError(
                "API key for Alpha Vantage was not found."
                " Set it into `.env` file as `AV_APIKEY`."
            )

        super(AlphaVantage, self).__init__([
            Limit(5, 60, 1, "av_1"), Limit(500, 86400, 1800, "av_2")
        ])

        self.intervals = [
            "1min", "5min", "15min", "30min", "60min"
        ]
        self.time_slices = [
            "year{}month{}".format(y, m)
            for y, m in product([1, 2], range(1, 13))
        ]

    def _values_to_types(self, headers: list, values: list):
        result = []
        for k, v in zip(headers, values):
            if k == "date":
                result.append(datetime.date.fromisoformat(v))
            elif k == "date_time":
                result.append(datetime.datetime.fromisoformat(v))
            elif k == "volume":
                result.append(int(v))
            else:
                result.append(float(v))
        return result

    def _cleanup_intraday_csv(self, content: str):
        content = content.strip().split("\r\n")

        header = content[0].split(",")
        header[0] = "date_time"

        body = [values.split(",") for values in content[1:]]
        body = [self._values_to_types(header, values) for values in body]

        return [dict(zip(header, values)) for values in body]

    def _cleanup_other_csv(self, content: str):
        content = content.strip().split("\r\n")

        header = content[0].split(",")
        try:
            dividend_index = header.index("dividend amount")
        except Exception:
            print("Failed to find `dividend amount`")
            dividend_index = header.index("dividend_amount")

        try:
            adjusted_index = header.index("adjusted close")
        except Exception:
            print("Failed to find `adjusted close`")
            adjusted_index = header.index("adjusted_close")

        header[header.index("timestamp")] = "date"
        header[adjusted_index] = "adj_close"
        header = header[:dividend_index] + header[dividend_index + 1:]

        body = [values.split(",") for values in content[1:]]
        body = [values[:dividend_index] + values[dividend_index + 1:] for values in body]
        body = [self._values_to_types(header, values) for values in body]

        return [dict(zip(header, values)) for values in body]

    async def get_intraday_full(
            self,
            symbol: str, interval: str, time_slice: str = "year1month1"
    ) -> list:
        params = {
            "function": "TIME_SERIES_INTRADAY_EXTENDED",
            "symbol": symbol,
            "interval": interval,
            "slice": time_slice,
            "adjusted": "true",
            "apikey": self.apikey
        }

        async with await self.make_request("GET", self.url, params=params) as response:
            result = self._cleanup_intraday_csv(await response.text())

        return result

    async def get_intraday_latest(self, symbol: str, interval: str) -> list:
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": symbol,
            "interval": interval,
            "adjusted": "true",
            "datatype": "csv",
            "outputsize": "full",
            "apikey": self.apikey
        }

        async with await self.make_request("GET", self.url, params=params) as response:
            result = self._cleanup_intraday_csv(await response.text())

        return result

    async def get_daily(self, symbol: str, outputsize: str = "full") -> list:
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": outputsize,
            "datatype": "csv",
            "apikey": self.apikey
        }

        async with await self.make_request("GET", self.url, params=params) as response:
            result = self._cleanup_other_csv(await response.text())[1:]

        return result

    async def get_weekly(self, symbol: str) -> list:
        params = {
            "function": "TIME_SERIES_WEEKLY_ADJUSTED",
            "symbol": symbol,
            "datatype": "csv",
            "apikey": self.apikey
        }

        async with await self.make_request("GET", self.url, params=params) as response:
            result = self._cleanup_other_csv(await response.text())[1:]

        return result

    async def get_monthly(self, symbol: str) -> list:
        params = {
            "function": "TIME_SERIES_MONTHLY_ADJUSTED",
            "symbol": symbol,
            "datatype": "csv",
            "apikey": self.apikey
        }

        async with await self.make_request("GET", self.url, params=params) as response:
            result = self._cleanup_other_csv(await response.text())[1:]

        return result
