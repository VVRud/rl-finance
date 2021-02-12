import os
import datetime
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from .throttler import Limit, Throttler


class Finimize(Throttler):

    def __init__(self):
        self.queries_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finimize_queries")
        self.url = "https://app.finimize.com/api/graphql/"
        self.headers = {
            "x-app-version": "2.0.2",
            "Accept-Encoding": "gzip",
            "cookie": "csrftoken=qd5DjEr1jRqrxLsSa0idPYyY4h75mi2AhUdmxAuy3fuwZH7xxNeUcT2tVPisAHkM",
            "authorization": "Token ecc4de1d89b4d082770482b98bcc104594957fe908d560ad351189551a9faa4e",
            "User-Agent": "okhttp/3.12.1",
            "Content-Type": "application/json"
        }

        self.transport = AIOHTTPTransport(url=self.url, headers=self.headers)
        self.client = Client(transport=self.transport)

        super(Finimize, self).__init__([
            Limit(30, 60, 1, "fm_1"), Limit(1000, 86400, 1800, "fm_2")
        ])

        self.content_types = [
            "DAILY_BRIEF", "INSIGHT", "OTHER"
        ]

    async def get_ids(self, content_type: str, after: str = None):
        params = {
            "count": 10,
            "after": after,
            "contentTypes": [content_type],
            "tagName": None
        }

        with open(os.path.join(self.queries_dir, "content_pagination.graphql"), "r") as file:
            query = gql(file.read())

        async with self.client as session:
            response = await session.execute(query, variable_values=params)

        data = response["viewer"]["me"]["contentPieces"]["edges"]

        docs = [datum["node"] for datum in data]
        ids = [doc["id"] for doc in docs]
        cursors = [datum["cursor"] for datum in data]

        return docs, ids, cursors

    async def get_single(self, _id: str):
        params = {
            "contentPieceId": _id
        }

        with open(os.path.join(self.queries_dir, "single_content_piece.graphql"), "r") as file:
            query = gql(file.read())

        async with self.client as session:
            response = await session.execute(query, variable_values=params)
        response = response["viewer"]["me"]["contentPiece"]
        response["_id"] = response.pop("id")
        response["dateUpdatedDisplay"] = datetime.datetime.fromisoformat(response["dateUpdatedDisplay"])

        return response
